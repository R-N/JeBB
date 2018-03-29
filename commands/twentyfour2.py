from line2.models.command import ContinuousTextCommand, Parameter, ParameterType, CommandResultType, CommandResult, CommandContinuousCallType
from line2.models.messages import Buttons
from line2.utils import IsEmpty, Lock, AddAtExit, DelAtExit, Acquire
from werewolf import Vote
from re import compile, DOTALL
from time import time
from twentyfour import Room as _Room, Eval, Solve, IsValid, twentyFourCmd as _cmd
from random import shuffle, choice, randint
from threading import Condition

class RoomPhase:
    idling = 0
    waiting = 1
    starting = 2
    guessing = 3
    explainvote = 4
    explainVote = 4
    explain = 5
    processing = 6
    done=7

class Player(object):
    def __init__(self, room, obj):
        self.obj = obj
        self.room = room
        self.score = 0
        self.pendingScore = 0
        self.lock = Lock()
        with self.room.lock:
            self.room.lastPlayerId += 1
            self.id = self.room.lastPlayerId
            self.room.waitings.append((obj, self))
            self.room.playersByObj[obj] = self
            self.room.playersById[self.id] = self
        
    def SendText(self, text):
        return self.room.SendText("@%s, %s" % (self.name, text))
        
    @property
    def name(self):
        return self.obj.name
    
    def Leave(self):
        with Acquire(self.lock, self.room.lock):
            if self not in self.room.leavings:
                self.room.leavings.append(self)
            self.SendText("You'll leave the next round. Type '/242 join' to cancel.")
            
        
    def Done(self, done=True):
        if self.room.phase != RoomPhase.guessing:
            self.SendText("It's not time yet")
            return CommandResult.Failed()
        with self.lock:
            if self.pendingScore:
                self.SendText("You have done-ed")
            else:
                with self.room.lock:
                    if len(self.room.losers) <= 1:
                        self.SendText("You're the last one")
                    elif self.pendingScore:
                        self.SendText("You have done-ed")
                    else:
                        self.pendingScore = max(0, round((self.room.end-time()) * self.room.winPoint))
                        if not self.pendingScore:
                            self.SendText("Time's up")
                        else:
                            if self in self.room.losers:
                                self.room.losers.remove(self)
                            if self not in self.room.winners:
                                self.room.winners.append(self)
                                self.room.winners.sort(key=lambda x: x.score, reverse=True)
                            self.room.SendText("%s says he knows the answer." % self.name)
                            if len(self.room.losers) <= 1:
                                with self.room.cond:
                                    self.room.cond.notifyAll()
                            return CommandResult.Done()
        return CommandResult.Failed()
                
        
rooms = {}

class Room(_Room):
    def __init__(self, creator, obj, top=None, bot=None, allowRevote=False, roundDuration=60, rounds = 5, voteDuration=30, explainDuration=15, winPoint=1, explainPoint=1, noSolutionPoint = 0.75, losePoint=0, failPoint=-2, quick=True):
        _Room.__init__(self, obj, top, bot, False)
        self.cond = Condition()
        self.quick = quick
        self.players = []
        self.playersByObj = {}
        self.playersById = {}
        self.end = time()
        self.roundDuration=roundDuration
        self.explainDuration = explainDuration
        self.voteDuration = voteDuration
        self.winPoint = winPoint
        self.explainPoint = explainPoint
        self.noSolutionPoint = noSolutionPoint
        self.losePoint = losePoint
        self.failPoint  = failPoint
        self.cantExplainPoint = failPoint
        self.allowRevote = allowRevote
        self.lastPlayerId = 0
        self.losers = []
        self.winners = []
        self.waitings = []
        self.leavings = []
        self.round = 0
        self.phase = RoomPhase.idling
        self.rounds = rounds
        self.votes = Vote(self)
        AddAtExit(self, self.__del__)
        self.waitingCommands = []
        self.explainer = None
        self.explainers = []
        buts = Buttons("TwentyFour2 game session created")
        buts.AddButton(
            "Join",
            "/242 join",
            "\nType '/242 join' to join"
        )
        buts.AddButton(
            "Leave",
            "/242 leave",
            "\nType '/242 leave' to leave"
        )
        buts.AddButton(
            "Force Start",
            "/242 forcestart",
            "\nType '/242 forcestart' to force start"
        )
        self.SendButtons(buts)
        self.Join(creator)
        
    def Stop(self, force=False):
        with self.lock:
            if self.nums:
                s = " ".join(FloatToStr(x) for x in self.nums)
                s2 = Solve(s)
                if s2:
                    self.SendText(s2)
                else:
                    send.SendText("Theres no solution to '%s'" % s)
            self.nums = None
            return CommandResult.Done()
        
    def ForceStart(self, sender):
        with self.lock:
            if sender not in self.playersByObj:
                self.SendText("%s, you havent joined and thus have no authority to forcestart the game" % sender.name)
                return CommandResult.Failed()
            return self.Start()
        
    def Start(self):
        with self.lock:
            if len(self.players) < 2:
                self.SendText("Need at least 2 players to start")
                return CommandResult.Failed()
            self.phase = RoomPhase.starting
            self.round = 0
            self.obj.client.Thread(self.RoundStart)
            return CommandResult.Done()
            
        
    def AddWaitingCommand(self, player):
        if not self.quick and self.allowRevote:
            return
        with self.lock:
            if player not in self.waitingCommands:
                self.waitingCommands.append(player)
                
    def ExtendWaitingCommand(self, players):
        if not self.quick and self.allowRevote:
            return
        with self.lock:
            for player in players:
                if player not in self.waitingCommands:
                    self.waitingCommands.append(player)
                
    def RemoveWaitingCommand(self, player):
        if not self.quick and self.allowRevote:
            return
        with self.lock:
            if player in self.waitingCommands:
                self.waitingCommands.remove(player)
            if len(self.waitingCommands) == 0:
                with self.cond:
                    self.cond.notifyAll()
        
    @property
    def running(self):
        return bool(self.nums)
        
    def Join(self, player):
        with self.lock:
            if player in self.playersByObj:
                player = self.playersByObj[player]
                if player in self.leavings:
                    self.leavings.remove(player)
                    player.SendText("You have canceled to leave the next round")
                    return CommandResult.Done()
                else:
                    player.SendText("Either you have already joined or waiting for the next round to join.")
                    return CommandResult.Failed()
            player = Player(self, player)
            if self.running:
                self.SendText("%s, the game is currently running. You will automatically join the next round if any." % player.name)
            else:
                self.AddWaitingPlayers()
            return CommandResult.Done()
        
    def Leave(self, player):
        with self.lock:
            if player not in self.playersByObj:
                self.SendText("@%s, You havent even joined" % player.name)
                return CommandResult.Failed()
            self.playersByObj[player].Leave()
            
    def AddWaitingPlayers(self):
        with self.lock:
            if len(self.waitings) > 0:
                for x in list(self.waitings):
                    k = x[0]
                    v = x[1]
                    if v not in self.players:
                        self.players.append(v)
                    if k not in self.playersByObj:
                        self.playersByObj[k] = v
                    if v.id not in self.playersById:
                        self.playersById[v.id] = v
                    self.SendText("%s has successfully joined" % v.name)
                self.waitings = []
                
    def RemoveLeavingPlayers(self):
        with self.lock:
            if len(self.leavings) > 0:
                for x in list(self.leavings):
                    k = x[0]
                    v = x[0]
                    if v in self.players:
                        self.players.remove(v)
                    if k in self.playersByObj:
                        del self.playersByObj[k]
                    if v.id in self.playersById:
                        del self.playersById[v.id]
                    self.SendText("%s has left the game" % v.name)
                self.leavings = []
                    
        
    def __del__(self):
        with self.lock:
            if self.phase < RoomPhase.done:
                self.SendText("Shutting down")
                if self.nums:
                    self.Stop(True)
                    DelAtExit(self)
                
    def SendText(self, text):
        self.obj.SendText("[TwentyFour2]\n%s" % text)
        
    def SendButtons(self, buttons):
        if not buttons.columnText.startswith("[TwentyFour2]"):
            buttons.SetColumnText("[TwentyFour2]\n%s" % buttons.columnText)
            buttons.SetAltTextHeader("[TwentyFour2]\n%s" % buttons.altTextHeader)
        return self.obj.SendButtons(buttons)
    
    def Done(self, sender, done=True):
        with self.lock:
            if sender not in self.playersByObj:
                self.SendText("%s, you're not even in the game" % sender.name)
                return CommandResult.Failed()
            return self.playersByObj[sender].Done(done)
                
    def Generate(self, top=None, bot=None):
        with self.lock:
            self.Set(top, bot)
            top = self.top
            bot = self.bot
            nums = [randint(bot, top), randint(bot, top), randint(bot, top), randint(bot, top)]
            nums.sort()
            self.nums = nums
            self.lastGenerated = time()
            self.end = time() + self.roundDuration
            return self.Send()
        
    def Send(self):
        if self.nums:
            s = "Round %d\n%s" % (self.round, '\n'.join(("%s : %d (%d)" % (player.name, player.score, player.pendingScore)) for player in self.players))
            self.SendText("Round%d\n%s\n%d seconds left.\nType '/242 done' if you figured it out\nPlayers who 'figured it out':%d\n%s\nPlayers who 'haven't figured it out':%d\n%s" % (
                self.round,
                " ".join("%g" % x for x in self.nums), 
                round(self.end-time()), 
                len(self.winners),
                '\n'.join(("%s : %d (%d)" % (x.name, x.score, x.pendingScore)) for x in self.winners),
                len(self.losers),
                '\n'.join(("%s : %d" % (x.name, x.score)) for x in self.losers)
            ))
            buts=Buttons("Have you figured it out?")
            buts.AddButton(
                "Yes",
                "/242 done",
                "\nIf so, type '/242 done'"
            )
            self.SendButtons(buts)
        else:
            buts = Buttons("TwentyFour2 is already running, but not started yet.")
            buts.AddButton(
                "Force Start",
                "/242 forcestart",
                "\nTo start it, type '/242 forcestart'"
            )
            self.SendButtons(buts)
        return CommandResult.Done()
    
    def RoundStart(self):
        self.round += 1
        self.AddWaitingPlayers()
        self.losers = list(self.players)
        self.winners = []
        self.Generate()
        self.phase = RoomPhase.guessing
        with self.cond:
            self.cond.wait(self.roundDuration)
        return self.GuessEnd()
    
    def FlushScores(self):
        s = "End of round %d\n" % self.round
        for player in self.players:
            with player.lock:
                if player.pendingScore == 0:
                    s = s + "\n%s : %d" % (player.name, player.score)
                elif player.pendingScore > 0:
                    s = s + "\n%s : %d + %d = %d" % (player.name, player.score, player.pendingScore, player.score+player.pendingScore)
                elif player.pendingScore < 0:
                    s = s + "\n%s : %d - %d = %d" % (player.name, player.score, -player.pendingScore, player.score+player.pendingScore)
                player.score += player.pendingScore
                player.pendingScore = 0
        self.players.sort(key=lambda x: x.score, reverse=True)
        self.SendText(s)
        
    
    def GuessEnd(self):
        s = " ".join("%g" % x for x in self.nums)
        s2 = Solve(s)
        if len(self.winners) == 0:
            if IsValid(s2):
                self.SendText("Yall suck\n%s == 24" % s2)
            else:
                point = round(self.roundDuration * self.noSolutionPoint)
                for x in self.losers:
                    x.pendingScore = point
                self.SendText("Well done. There is no 24 solution to '%s'. Yall get %d points" % (s, point))
            return self.RoundEnd()
        elif self.quick and not IsValid(s2):
            point = round(self.roundDuration * self.noSolutionPoint)
            for x in self.winners:
                x.pendingScore = round(x.pendingScore * self.failPoint)
            for x in self.losers:
                x.pendingScore = point
            self.SendText("There is no 24 solution to '%s'. Those who said they knew are obviously wrong and will be punished :). Others will get %d points" % (s, point))
            return self.RoundEnd()
        else:
            return self.ExplainVote()
        
    def Vote(self, voter, id):
        if voter not in self.playersByObj:
            self.SendText("%s, you havent even joined." % voter.name)
            return CommandResult.Failed()
        voter = self.playersByObj[voter]
        if self.phase != RoomPhase.explainVote:
            self.SendText("It's not time yet")
            return CommandResult.Failed()
        if voter not in self.losers:
            voter.SendText("You can't vote")
            return CommandResult.Failed()
        if id not in self.playersById:
            voter.SendText("Invalid ID : %d" % id)
        votee = self.playersById[id]
        ret = self.votes.Vote(voter, votee)
        if not self.allowRevote or self.quick and ret.type == CommandResultType.Done and len(self.votes.haventVoted) == 0:
            with self.cond:
                self.cond.notifyAll()
        return ret
        
    def ExplainVote(self):
        self.explainers = []
        self.explainer = None
        self.explained = False
        winners = list(self.winners)
        s = " ".join(("%g" % x) for x in self.nums)
        while True:
            if len(self.explainers) == 0 and len(winners) > 0:
                self.votes.Set(self.losers, self.winners)
                self.SendText("Losers : %s" % (', '.join(x.name for x in self.losers)))
                buts = Buttons("Yall losers can vote who will explain by typing '/242 vote=<id>' with the ids below", "Yall losers can vote who will explain")
                for w in self.winners:
                    buts.AddButton(
                        w.name,
                        "/242 vote=%d" % w.id,
                        "\n%d\t:%s" % (w.id, w.name)
                    )
                self.SendButtons(buts)
                with self.cond:
                    self.phase = RoomPhase.explainVote
                    self.cond.wait(self.voteDuration)
                self.phase = RoomPhase.processing

                voteds = self.votes.votees
                explainee = None
                if len(voteds) == 0:
                    self.SendText("Vote time runs out but yall didn't vote. So I'll just random it xd")
                    r = choice(winners)
                    winners.remove(r)
                    self.explainers.append(r)
                else:
                    voteds = [(v, k) for k, v in voteds.items() if v>0]
                    self.votes.Clear()
                    if len(voteds) == 0:
                        self.SendText("Vote time runs out but yall didn't vote. So I'll just random it xd")
                        r = choice(winners)
                        winners.remove(r)
                        self.explainers.append(r)
                    else:
                        voteds.sort(reverse=True)
                        m = voteds[0][0]
                        voteds = [x[1] for x in voteds if x[0] == m]
                        for v in voteds:
                            winners.remove(v)
                        shuffle(voteds)
                        self.explainers.extend(voteds)
            elif len(self.explainers) > 0:
                self.explainer = self.explainers.pop(0)
                with self.cond:
                    self.explainer.SendText("You have %d seconds to give the solution to '%s'" % (self.explainDuration, s))
                    self.phase = RoomPhase.explain
                    self.cond.wait(self.explainDuration)
                self.phase = RoomPhase.processing
                if self.explained:
                    point2 = round(self.explainer.pendingScore * (1+self.explainPoint))
                    self.explainer.SendText("You get %d points" % (point2-self.explainer.pendingScore))
                    self.explainer.pendingScore = point2
                    break
                self.explainer.pendingScore = round(self.explainer.pendingScore * self.failPoint)
                self.explainer.SendText("You have failed to explain so your score will be reduced by %d instead" % (-self.explainer.pendingScore))
                self.explainer = None
            else:
                break
        if not self.explained:
            s2 = Solve(s)
            if IsValid(s2):
                self.SendText("Answer:\n%s == 24" % s2)
            else:
                point = round(self.roundDuration * self.noSolutionPoint)
                for x in self.losers:
                    x.pendingScore = point
                self.SendText("There is no 24 solution to '%s'. Those who didnt answer will get %d points" % (s, point))
        self.explainer = None
        return self.RoundEnd()
    
    def Explain(self, obj, text):
        sender = obj
        with self.lock:
            if not self.phase == RoomPhase.explain:
                return CommandResult.Failed()
            if obj not in self.playersByObj:
                return CommandResult.Failed()
            explainer = self.playersByObj[obj]
            if explainer != self.explainer:
                return CommandResult.Failed()
            if not self.nums:
                return CommandResult.Failed()
            text = text.strip()
            if not IsValid(text):
                return CommandResult.Failed()
            mExRx = Room.exRx.match(text)
            if not mExRx:
                return CommandResult.Failed()
            nums = None
            try:
                nums = [float(mExRx.group(2)), float(mExRx.group(6)), float(mExRx.group(10)), float(mExRx.group(14))]
            except Exception as e:
                self.SendText("Error. Invalid numbers.\n%s" % (s, e))
                return CommandResult.Done()
            try:
                for i in range(0, 4):
                    x = nums[i]
                    if x < self.bot or x > self.top:
                        raise Exception("Only integers ranging from %d-%d are allowed. %g is not in range" % (self.bot, self.top, x))
                    y = int(x)
                    if x != y:
                        raise Exception("Only integers ranging from %d-%d are allowed. %g is not an integer" % (self.bot, self.top, x))
                    nums[i] = y
            except Exception as e:
                self.SendText("Error. Invalid numbers.\n%s" % (s, e))
                return CommandResult.Done()
            nums.sort()
            if nums != self.nums:
                self.SendText("Error. Invalid numbers.\n%s != %s" % (nums, self.nums))
                return CommandResult.Done()
            s = ''
            for i in range(1, 16):
                c = mExRx.group(i)
                if c:
                    s = s+c
            try:
                name = ''
                if explainer.name:
                    name = ", %s" % explainer.name
                ret = float(eval(text))
                if ret == 24:
                    rep = "Correct%s.\n%s == 24"
                    self.SendText(rep % (name, s))
                    self.explained = True
                    with self.cond:
                        self.cond.notifyAll()
                else:
                    rep = "Wrong%s.\n%s == %g"
                    self.SendText(rep % (name, s, ret))
            except Exception as e:
                self.SendText("Error. '%s' may not be a valid math expression.\n%s" % (s, e))
            return CommandResult.Done()
            
        
    def Remove(self):
        self.nums = None
        global rooms
        del rooms[self.obj]
        
    def RoundEnd(self):
        self.FlushScores()
        self.RemoveLeavingPlayers()
        if self.round < self.rounds and len(self.players) > 1:
            return self.RoundStart()
        else:
            return self.GameOver()
            
    def GameOver(self):
            m = self.players[0].score
            self.SendText("Game over.\n%s" % '\n'.join(("%s : %s" % (x.name, x.score)) for x in self.players))
            self.phase = RoomPhase.done
            self.nums = None
            self.Remove()
        
        
lock = Lock()


def TwentyFour2(message, options='', text='', continuous = CommandContinuousCallType.notContinuous, action = '', top=None, bot=None, allowrevote=False, roundtime=60, rounds = 5, votetime=30, explaintime=15, winpoint=1, explainpoint=1, nosolutionpoint = 0.75, losepoint=0, failpoint=-2, quick=True, done=None, vote=0, *args, **kwargs):
    sender = message.sender
    chatroom = message.chatroom
    client = message.client
    if continuous:
        if not sender:
            return CommandResult.Failed()
        if chatroom not in rooms:
            return CommandResult.Failed()
        room = rooms[chatroom]
        return room.Explain(sender, text)
    else:
        if IsEmpty(action):
            action = text
        sender = message.sender
        chatroom = message.chatroom
        client = message.client
        if not client.hasOA or not client.hasUser:
            message.ReplyText("Sorry TwentyFour2 needs both OAClient and UserClient")
            return CommandResult.Failed()
        elif not chatroom.hasUser:
            message.ReplyText("Please invite the UserClient here first")
            return CommandResult.Failed()
        elif not chatroom.hasOA:
            if client.oAClient.obj:
                client.oAClient.obj.InviteInto(chatroom)
                message.ReplyText("Please retry the command after the OAClient joined")
            else:
                message.ReplyText("Please invite the UserClient here first")
            return CommandResult.Failed()
        elif not sender or not sender.hasUser or (not sender.name and not sender.GetName()):
            message.ReplyText("Sorry we can't identify you.")
            return CommandResult.Failed()
        elif not sender.rObj:
            message.ReplyText("%s, please type '/robj' in a room consisting of only you, our UserClient, and our OAClient" % sender.name)
            #message.ReplyText("%s, please accept the group invitation" % sender.name)
            return CommandResult.Failed()
        elif action == 'create':
            with lock:
                if chatroom in rooms:
                    return rooms[chatroom].Send()
                else:
                    room = Room(sender, chatroom, top=top, bot=bot, allowRevote=allowrevote, roundDuration=roundtime, rounds = rounds, voteDuration=votetime, explainDuration=explaintime, winPoint=winpoint, explainPoint=explainpoint, noSolutionPoint = nosolutionpoint, losePoint=losepoint, failPoint=failpoint, quick=quick, *args, **kwargs)
                    rooms[chatroom] = room
        else:
            room = None
            with lock:
                if chatroom in rooms:
                    room = rooms[chatroom]
                else:
                    chatroom.SendText("No TwentyFour2 game session")
                    return CommandResult.Failed()
            if action == 'join':
                return room.Join(sender)
            elif action == 'leave':
                pass
            elif action == 'done'or done is not None:
                done = action=='done' or done
                return room.Done(sender, done)
            elif action == 'forcestart':
                return room.ForceStart(sender)
            elif vote:
                room.Vote(sender, vote)
            
            
            
        
            
            
            
                

twentyFour2Cmd = ContinuousTextCommand(
    "twentyfour2",
    TwentyFour2,
    desc="Use the 4 given numbers to form a math expression equal to 24. You can only use *+-/% operators. The number combinations are NOT guaranteed to have solution. If you figured it out, type '/242 done'. The loser would be the last one who haven't figured it out, or all of them who haven't figured it out when the time runs out. The loser wont get any point. The winners will get the remaining time (timeleft) point. The losers can then vote to ask the winners. If he can answer, he will double the point he just won. Else, he will lose 3*the point he just won, and losers can ask other winners. Note that you can change the points. You can use quick mode to make the point lost immediate for number combinations that have no solution. Just pass 'quick=True' when starting the game."
)