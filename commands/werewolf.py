# -*- coding: utf-8 -*-
from line2.models.command import ContinuousHybridCommand, Parameter, ParameterType, CommandResult, CommandResultType,  CommandContinuousCallType
from line2.utils import IsEmpty, AddReverseDict, Lock, AddAtExit, DelAtExit, Acquire
from line2.models.messages import Buttons
from time import time, sleep
from threading import Timer, Condition
from random import randint, choice, shuffle

class RoomPhase:
    idling=0
    waiting=1
    starting = 2
    night=3
    day=4
    lynchVote=5
    hunter=6
    done = 7
    
    toString = {
        0:'idling',
        1:'waiting',
        2:'starting',
        3:'night',
        4:'day',
        5:'lynchVote',
        6:'hunter',
        7:'done'
    }
    
class ActionPhase:
    none=0
    night=RoomPhase.night
    day=RoomPhase.day
    hunter=RoomPhase.hunter
    firstNight=7
    anyday=8
    
class Role(object):
    none=None
    villager=None
    werewolf=None
    drunk=None
    seer=None
    harlot=None
    beholder=None
    gunner=None
    traitor=None
    guardianAngel=None
    cursed=None
    detective=None
    apprenticeSeer=None
    cultist=None
    cultistHunter=None
    wildChild=None
    fool=None
    mason=None
    doppelganger=None
    cupid=None
    hunter=None
    serialKiller=None
    tanner=None
    mayor=None
    prince=None
    sorcerer=None
    clumsy=None
    blacksmith=None
    alphaWolf=None
    wolfCub=None
    werewolves = []
    unconvertible = []
    visitorKillers = []
    needRoleModel = []
    rolesById={}
    rolesByName={}
    validRoles = []
    seers = []
    def __init__(self, id, name, team, actionPhase, initMsg):
        self.id = id
        if id:
            Role.validRoles.append(self)
        self.name = name
        self.team = team
        self.actionPhase = actionPhase
        self.initMsg = initMsg
        Role.rolesById[id] = self
        Role.rolesByName[name] = self
        
    def __eq__(self, rhs):
        return isinstance(rhs, Role) and rhs.id == self.id
    
    def __ne__(self, rhs):
        return not self.__eq__(rhs)
        
class Team:
    none=0
    village=1
    villager=1
    villagers=1
    werewolf=2
    werewolves=2
    cult=3
    cultist=3
    cultists=3
    doppelganger=4
    serialKiller=5
    tanner=6
    independant=7
    
    toString={
        0:"None",
        1:"Villager",
        2:"Werewolf",
        3:"Cult",
        4:"Doppelganger",
        5:"Serial Killer",
        6:"Tanner",
        7:"Independant"
    }

seerLine = "You're the Seer! Every night you can choose to look into someone's role."

Role.none = Role(0, "None", Team.none, ActionPhase.none, "None")
Role.villager = Role(1, "Villager", Team.villager, ActionPhase.none, "You're a Villager. Go plow some field you ugly")
Role.werewolf = Role(2, "Werewolf", Team.werewolf, ActionPhase.night, "You're an awoo")
Role.drunk = Role(3, "Drunk", Team.villager, ActionPhase.none, "You're the Drunk. Werewolves will go drunk and skip one turn if they eat you")
Role.seer = Role(4, "Seer", Team.villager, ActionPhase.night, seerLine)
Role.harlot = Role(5, "Harlot", Team.villager, ActionPhase.night, "You're the Harlot(slut). Every night, you can choose to sneak into someone's bed. If a werewolf tries to kill you, you'll be safe cuz ur not home. However if you sneak into a werewolf's house, you're dead meat. Also, if a werewolf kills the house owner which you snucked into, you'll also be killed.")
Role.beholder = Role(6, "Beholder", Team.villager, ActionPhase.none, "It's nothing special. It's just that you know who the Seer is.")
Role.gunner = Role(7, "Gunner", Team.villager, ActionPhase.day, "You're the Gunner. Every day, you can choose to shoot someone. Your shooting will be revealed to all, as well as your role. You only have two bullets.")
Role.traitor = Role(8, "Traitor", Team.werewolf, ActionPhase.none, "You're a Traitor. You're on the werewolves' side. You will turn into a werewolf if all werewolves die.")
Role.guardianAngel = Role(9, "Guardian Angel", Team.villager, ActionPhase.night, "Your Guardian ANgle. Every night, you can choose to protect someone's house from Werewolves. You can't protect yours, though.")
Role.cursed = Role(10, "Cursed", Team.werewolf, ActionPhase.none, "You're the Cursed. If a werewolf tries to kill you, you will turn into one! Until then, you're on their side from the beginning, though. The Seer will see you as a Werewolf even when you haven't transformed yet.")
Role.detective = Role(11, "Detective", Team.villager, ActionPhase.day, "You're a Detective. Every day, you can choose to investigate someone. However, there are 40% chance the werewolves will notice.")
Role.apprenticeSeer = Role(12, "Apprentice Seer", Team.villager, ActionPhase.none, "You're an Apprentice Seer. If the Seer dies, you carry on his duty")
Role.cultist = Role(13, "Cultist", Team.cultist, ActionPhase.night, "You're a Cultist. You can invite someone over to your cult. If at the end of the game everyone is a cult member, the cult wins")
Role.cultistHunter = Role(14, "Cultist Hunter", Team.villager, ActionPhase.night, "You're the Cultist Hunter. If a cultist tries to invite you, their cult's newest member will die. Every night, you can choose to hunt someone. If he's a cultist, he will die")
Role.wildChild = Role(15, "Wild Child", Team.villager, ActionPhase.firstNight, "You're a Wild Child. You can choose someone to be your role model. If he dies, you'll turn into a Werewolf.")
Role.fool = Role(16, "Fool", Team.villager, ActionPhase.night, seerLine)
Role.mason = Role(17, "Mason", Team.villager, ActionPhase.none, "You're a Mason. All Mason knows all Masons")
Role.doppelganger = Role(18, "Doppelganger", Team.doppelganger, ActionPhase.firstNight, "Your ancestors had the ability to metamorph into others... while you don't have their full abilities, you can pick a player at the start of the game. If that player dies, you will become what they were.\nNote: If they were Wild Child and their role model died, you will become a wolf. Otherwise, you will inherit their role model.\nThe cult cannot convert the Doppelgänger (but can after the doppelganger switches roles). Also - the Doppelgänger can NOT win unless they have transformed. If at the end of the game, the Doppelgänger is still the same, they lose (exception: lover)")
Role.cupid = Role(19, "Cupid", Team.villager, ActionPhase.firstNight, "Love is in the air. As Cupid, you will choose two players at the start of the game. These two players will become madly in love! If one of them dies, the other will die of sorrow :(\nNote: Lovers will know who each other are, but not be told their roles. If the lovers are the last two alive, they win, regardless of teams. If the lovers are on different teams (villager + wolf), and one team wins (wolf), the lover (villager) wins as well. TL;DR if at least one of the lovers was on the winning team, they both win together.")
Role.hunter = Role(20, "Hunter", Team.villager, ActionPhase.hunter, "A trigger happy, vindictive player. As the hunter, you try to keep to yourself. However, when others come to visit you, they may find themselves dead, as your paranoia takes hold and you shoot. If the wolves attack you, you have a chance to take one of them with you. Otherwise, if you die, you will get a chance to shoot someone as you die.\nNote: For wolf attacks, the chance starts at 30%. If there is one wolf, the hunter has a 30% chance to kill the wolf (and survive). For each additional wolf, add 20% (2 wolves = 50%, 3 = 70%, etc). However - if there are multiple wolves, while you may kill one of them, you will still be outnumbered and killed.\nIf the cult tries to convert you, they have a 50% chance to fail. If they fail, you have a 50% chance to kill one of them!")
Role.serialKiller = Role(21, "Serial Killer", Team.serialKiller, ActionPhase.night, "That asylum was silly anyways. What a joke. You are free now however, back to business as usual - killing! The serial killer is a lone player, on their own team. They can win only if they are the last player alive (exception: lovers). As the serial killer, you can kill ANYONE - wolves, hunters, gunners, guardian angels, whatever. If the wolves try to attack you, you will kill one of them (random), and live.")
Role.tanner = Role(22, "Tanner", Team.tanner, ActionPhase.none, "The Tanners goal is simple: Get Lynched. If the Tanner gets lynched, he wins, period. Everyone else loses.")
Role.mayor = Role(23, "Mayor", Team.villager, ActionPhase.anyday, "As mayor, you are a lowly villager, until you reveal yourself. Then you are given twice the vote count for lynching (meaning that your vote is twice as powerful as everyone else's). Use that power wisely to help the Village Team.")
Role.prince = Role(24, "Prince", Team.villager, ActionPhase.none, "Once the prince gets lynched, their role as Prince is revealed, and they survive. However, this can only happen once: if the village insists on lynching them, they will die.")
Role.sorcerer = Role(25, "Sorcerer", Team.werewolf, ActionPhase.night, "Do you remember the good old seer? Well now, it has its Wolf Team counterpart. The sorcerer is the Wuff's Seer. They can only see if someone is Wolf or Seer, and they win with the Wolves.")
Role.clumsy = Role(26, "Clumsy", Team.villager, ActionPhase.none, "You are the Clumsy Guy. Maybe you should not have had so much alcohol for breakfast. You can't see a damn thing. Can you even vote for the person you want to? (You have a 50% chance to vote for someone random.)")
Role.blacksmith = Role(27, "Blacksmith", Team.villager, ActionPhase.anyday, "You are the BlackSmith. Through the years, no blades nor swords gave you as much satisfaction as the Silver Blades the elves ordered.\nYou might have some silverdust left. Who knows ? It might *prevent Wolves from eating tonight*")
Role.alphaWolf = Role(28, "Alpha Wolf", Team.werewolf, ActionPhase.night, "You are the Alpha Wolf, the origin of the curse, the bane of banes. Every night, there's 20% chance that you will bite your pack's meal, and they will join your ranks instead of dying!")
Role.wolfCub = Role(29, "Wolf Cub", Team.werewolf, ActionPhase.night, "What a cuuuute little wuff. _tickles tickles_ -cough cough- As i was saying, you are the Wolf Cub and you _drops the mic_ -I just can't resist that. I think if anyone killed you, I'd give the wuffs two victims. You're too cute to die. I wouldn't be able to tickle you anymore-")

Role.werewolves.append(Role.werewolf)
Role.werewolves.append(Role.alphaWolf)
Role.werewolves.append(Role.wolfCub)

Role.unconvertible.extend(Role.werewolves)
Role.unconvertible.append(Role.doppelganger)
Role.unconvertible.append(Role.serialKiller)
Role.unconvertible.append(Role.cultistHunter)

Role.visitorKillers.extend(Role.werewolves)
Role.visitorKillers.append(Role.hunter)
Role.visitorKillers.append(Role.serialKiller)

Role.needRoleModel.append(Role.wildChild)
Role.needRoleModel.append(Role.doppelganger)

Role.seers.append(Role.seer)
Role.seers.append(Role.fool)
Role.seers.append(Role.sorcerer)

class Alive:
    notPlaying = None
    dead=False
    alive=True
    
    toString={
        None:'not playing',
        False:'dead',
        True:'alive'
    }
    

class Player(object):
    def __init__(self, obj, room):
        with room.lock:
            self.lock = Lock()
            with self.lock:
                self._1role = None
                self.obj = obj
                self.room = room
                self.room.lastPlayerId+=1
                self.id = self.room.lastPlayerId
                room.players.append(self)
                room.playersById[self.id] = self
                room.playersByObj[obj] = self
                self.room.playersByObj[obj] = self
                rObj = self.obj.rObj
                self.originalRole = None
                self.alive = Alive.notPlaying
                self.lover = None
                self.ammo = 0
                self.protection=0
                self.drunk=False
                self.dayLastSeen=0
                self.canAct=False
                self.houseOwner = self
                self.harlot = None
                self.cultistId = 0
                self.killerRole = None
                self.mayorRevealed = False
                self.princeRevealed = False
                self.master = None
                self.apprentices = []
                self.freeloader = None
                self.done = False
                self.dayRoleSet = 0
                self.getRole = None
                self.kill = None
            
    def Remove(self):
        with Acquire(self.lock, self.room.lock):
            if self.room.lastPlayerId - self.id == 1:
                self.room.lastPlayerId-=1
            if self in self.room.players:
                self.room.players.remove(self)
            if self.id in self.room.playersById:
                del self.room.playersById[self.id]
            if self.obj in self.room.playersByObj:
                del self.room.playersByObj[self.obj]
            return CommandResult.Done()
        
    @property
    def role(self):
        return self._1role
    
    def GetTeamNames(self, group):
        group = list(group)
        if len(group) == 0:
            return ''
        name = group[0].role.name
        if self in group:
            group.remove(self)
            groupLen = len(group)
            if groupLen < 1:
                return "You are a lone %s" % name
            elif groupLen == 1:
                return "You and %s are %ss" % (group[0].name, name)
            else:
                return "You, %s and %s are %ss" % (', '.join([x.name for x in group[:groupLen-1]]), group[-1].name, name)
        else:
            groupLen = len(group)
            if groupLen < 1:
                return "There is no %s" % name
            elif groupLen == 1:
                return "%s is a lone %s" % (group[0].name, name)
            elif groupLen == 2:
                return "%s and %s are %ss" % (group[0].name, group[1].name, name)
            else:
                return "%s and %s are %ss" % (', '.join([x.name for x in group[:groupLen-1]]), group[-1].name, name)
            
            
    def SendTeamNames(self, group):
        return self.SendText(self.GetTeamNames(group))
    
    @role.setter
    def role(self, value):
        if value == self.role:
            return
        if self._1role:
            if self._1role == Role.alphaWolf or self._1role == Role.wolfCub:
                if self in self.room.playersByRole[Role.werewolf]:
                    self.room.playersByRole[Role.werewolf].remove(self)
            if self in self.room.playersByRole[self._1role]:
                self.room.playersByRole[self._1role].remove(self)
        self._1role = value
        if self._1role not in self.room.playersByRole:
            self.room.playersByRole[self._1role] = []
        self.room.playersByRole[self._1role].append(self)
        
        if not value:
            return
        if value == Role.cultist:
            with self.room.lock, self.lock:
                self.room.lastCultistId += 1
                self.cultistId = self.room.lastCultistId
                self.room.cultists.append(self)
                if not self.room.hasCultist:
                    self.room.hasCultist = True
                    if Role.cultist.id not in self.room.votes:
                        self.room.votes[Role.cultist.id] = Vote(self.room)
        elif value == Role.gunner:
            self.ammo = 2
        elif value == Role.harlot:
            self.room.harlots.append(self)
        elif value == Role.beholder:
            self.room.beholders.append(self)
        elif value in Role.werewolves:
            self.room.werewolves.append(self)
            self.room.hasWerewolf = True
        elif value == Role.seer:
            self.room.seers.append(self)
        elif value == Role.mason:
            self.room.masons.append(self)
        elif value == Role.cupid:
            self.room.lovers[self] = []
        elif value == Role.traitor:
            self.room.traitors.append(self)
        elif value == Role.apprenticeSeer:
            self.room.apprenticeSeers.append(self)
        elif value == Role.guardianAngel:
            self.room.guardianAngels.append(self)
            
        self.dayRoleSet = self.room.day
        if self.room.realPhase == RoomPhase.night:
            self.dayRoleSet += 1
                
    def Tell(self, to):
        s = "%s is now a %s" % (self.name, self.role.name)
        for x in to:
            if x != self:
                x.SendText(s)
                
    def TellBeholders(self):
        self.Tell(self.room.beholders)
        self.room.shouldTellBeholders = True
                
    def TellWerewolves(self):
        self.Tell(self.room.werewolves)
        self.room.shouldTellWerewolves = True
                
    def TellMasons(self):
        self.Tell(self.room.masons)
        self.room.shouldTellMasons = True
                
    def TellCultists(self):
        self.Tell(self.room.cultists)
        self.room.shouldTellCultists = True
        
    def TryTell(self, to):
        if self.room.phase > RoomPhase.starting:
            self.Tell(to)
            return True
            
    def TryTellBeholders(self):
        self.TryTell(self.room.beholders)
        self.room.shouldTellBeholders=True
    def TryTellWerewolves(self):
        self.TryTell(self.room.werewolves)
        self.room.shouldTellWerewolves=True
    def TryTellMasons(self):
        self.TryTell(self.room.masons)
        self.room.shouldTellMasons=True
    def TryTellCultists(self):
        self.TryTell(self.room.cultists)
        self.room.shouldTellCultists=True
        
    def Die(self, killerRole=Role.none):
        print("DIE")
        if self.alive == Alive.alive:
            print("WAS ALIVE")
            self.alive = Alive.dead
            self.killerRole = killerRole
            self.room.playersByRole[self.role].remove(self)
            with self.room.lock:
                if self in self.room.alives:
                    self.room.alives.remove(self)
                if self not in self.room.deads:
                    self.room.deads.append(self)
                
            if self.role == Role.cultist:
                with self.room.lock:
                    if self in self.room.cultists:
                        self.room.cultists.remove(self)
                    if len(self.room.cultists) == 0:
                        self.room.hasCultist = False
            elif self.role == Role.hunter:
                self.room.deadHunters.append(self)
            elif self.role == Role.harlot:
                with self.room.lock:
                    if self in self.room.harlots:
                        self.room.harlots.remove(self)
            elif self.role in Role.werewolves:
                with self.room.lock:
                    if self in self.room.werewolves:
                        self.room.werewolves.remove(self)
                    if len(self.room.werewolves) == 0:
                        if len(self.room.traitors) == 0:
                            self.room.hasWerewolf = False
                        else:
                            for x in self.room.traitors:
                                x.Inherit(self)
            elif self.role == Role.seer:
                with self.room.lock:
                    if self in self.room.seers:
                        self.room.seers.remove(self)
                    if len(self.room.seers) == 0:
                        for x in self.room.apprenticeSeers:
                            x.Inherit(self)
                    self.room.shouldTellBeholders = True
            elif self.role == Role.mason:
                with self.room.lock:
                    if self in self.room.masons:
                        self.room.masons.remove(self)
            elif self.role == Role.traitor:
                with self.room.lock:
                    if self in self.room.traitors:
                        self.room.traitors.remove(self)
            elif self.role == Role.beholder:
                with self.room.lock:
                    if self in self.room.beholders:
                        self.room.beholders.remove(self)
            elif self.role == Role.apprenticeSeer:
                with self.room.lock:
                    if self in self.room.apprenticeSeers:
                        self.room.apprenticeSeers.remove(self)
            elif self.role == Role.guardianAngel:
                with self.room.lock:
                    if self in self.room.guardianAngels:
                        self.room.guardianAngels.remove(self)
            if killerRole == Role.villager:
                self.room.SendText("Yall lynched %s the %s" % (self.name, self.role.name))
            elif killerRole == self:
                self.room.SendText("%s just can't live without %s", (self.name, self.lover.name))
            elif killerRole == Role.none:
                self.room.SendText("%s has been away for too long and considered dead" % self.name)
            else:
                k = "???"
                if killerRole:
                    k = killerRole.name
                self.room.SendText("%s the %s was killed by %s" % (self.name, self.role.name, k))
            if len(self.apprentices) > 0:
                for x in self.apprentices:
                    x.Inherit(self)
            if self.lover and self.lover.alive:
                self.lover.Die(self.lover)
                
    def Inherit(self, master):
        if not self.alive:
            return
        role = self.role
        if self.role == Role.apprenticeSeer:
            role = Role.seer
            with self.room.lock:
                if self in self.room.apprenticeSeers:
                    self.room.apprenticeSeers.remove(self)
        elif self.role == Role.traitor:
            role = Role.werewolf
            with self.room.lock:
                if self in self.room.traitors:
                    self.room.traitors.remove(self)
        elif self.role == Role.wildChild:
            role = Role.werewolf
        elif self.role == Role.doppelganger:
            role = master.role
        if role == Role.wildChild:
            if master.master:
                self.Inherit(master.master)
            else:
                role = Role.werewolf
        if role == Role.doppelganger:
            if master.master:
                return self.Inherit(master.master)
        if role == Role.seer:
            self.room.shouldTellBeholders = True
        self.role = role
        self.InitRole()
                    
    def SendText(self, text):
        if text.startswith("[WW #"):
            return self.rObj.SendText(text)
        return self.rObj.SendText("[WW #%d : %s]\n%s" % (self.room.id, self.room.name, text))
    
    def SendButtons(self, buttons):
        if not buttons.columnText.startswith("[WW #"):
            buttons.SetColumnText("[WW #%d : %s]\n%s" % (self.room.id, self.room.name, buttons.columnText))
            buttons.SetAltTextHeader("[WW #%d : %s]\n%s" % (self.room.id, self.room.name, buttons.altTextHeader))
        return self.rObj.SendButtons(buttons)
    
    @property
    def name(self):
        return self.obj.name
        
    @property
    def rObj(self):
        return self.obj.rObj
    
    
    
    def InitRole(self):
        role = self.role
        if role == Role.fool:
            role = Role.seer
            
        self.SendText("Role #%d : %s\nTeam : %s\n%s" % (role.id, role.name, Team.toString[role.team], role.initMsg))
                          
        if role == Role.cupid:
            self.room.AddWaitingCommand(self)
            buts = Buttons("Choose who to pair up as lovers by typing '/ww room=%d pair=<id>' using the ids below" % self.room.id, "Choose who to pair up")
            options = list(self.room.alives)
            for option in options:
                buts.AddButton(
                    option.name,
                    "/ww room=%d pair=%d" % (self.room.id, option.id),
                    "\n%s\t : %s" % (option.id, option.name)
                )
            self.SendButtons(buts)
        elif role in Role.needRoleModel:
            self.room.AddWaitingCommand(self)
            buts = Buttons("Choose your role model by typing '/ww room=%d master=<id>' using the ids below" % self.room.id, "\nChoose your role model")
            options = [x for x in self.room.alives if x != self]
            for option in options:
                buts.AddButton(
                    option.name,
                    "/ww room=%d master=%d" % (self.room.id, option.id),
                    "\n%s\t : %s" % (option.id, option.name)
                )
            self.SendButtons(buts)
        elif role == Role.mason:
            self.TryTellMasons()
        elif role == Role.werewolf:
            self.TryTellWerewolves()
        elif role == Role.seer:
            self.TryTellBeholders()
        elif role == Role.cultist:
            self.TryTellCultists()
            
            
            
    def HandleCommand(self, action='', eat=0, kill=0, convert=0, shoot=0, pair=0, see=0, master=0, protect=0, lynch=0, *args, **kwargs):
        self.dayLastSeen = self.room.day
        if eat:
            return self.Eat(eat)
        elif kill:
            return self.Kill(kill)
        elif convert:
            return self.Convert(convert)
        elif shoot:
            if self.role == Role.gunner:
                return self.ShootGunner(shoot)
            elif self.role == Role.hunter:
                return self.ShootHunter(shoot)
            elif self.role == Role.cultistHunter:
                return self.ShootCH(shoot)
            else:
                self.SendText("You're neither a Gunner, a Hunter, nor a Cultist Hunter.")
                return CommandResult.Failed()
        elif pair:
            return self.Pair(pair)
        elif see:
            if self.role == Role.detective:
                return self.Investigate(see)
            else:
                return self.SeeRole(see)
        elif master:
            return self.ChooseMaster(master)
        elif protect:
            return self.Protect(protect)
        elif lynch:
            return self.Lynch(lynch)
        elif action == 'reveal':
            return self.Reveal()
        elif action == 'silver':
            return self.SpreadDust()
        self.SendText("Invalid command")
        return CommandResult.Failed()
    
    def Lynch(self, lynchId):
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if self.room.phase != RoomPhase.lynchVote:
            self.SendText("It's not time to lynch")
            return CommandResult.Failed()
        if lynchId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        if self not in self.room.votes[Role.villager.id].haventVoted and not self.room.allowRevote:
            self.SendText("Either you have already choosen who to lynch or it's not your turn")
            return CommandResult.Failed()
        
        lynch = self.room.playersById[lynchId]
        if lynch == self:
            self.SendText("You can't lynch yourself")
            return CommandResult.Failed()
        if not lynch.alive:
            self.SendText("The one you want to lynch is already dead")
            return CommandResult.Failed()
        if self.role == Role.clumsy or self.originalRole == Role.clumsy:
            return self.room.votes[Role.villager.id].VoteRandom()
        voteCount=1
        if self.mayorRevealed:
            voteCount=2
        ret = self.room.votes[Role.villager.id].Vote(self, lynch, voteCount)
        self.room.SendText("%s voted to lynch %s" % (self.name, lynch.name))
        return ret
            
    def Reveal(self):
        if self.role != Role.mayor:
            self.SendText("You're not a Mayor")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if self.mayorRevealed:
            self.SendText("You already revealed that you're a Mayor")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        self.mayorRevealed = True
        self.room.SendText("%s has revealed that he is a Mayor! His votes will count twice from now on." % self.name)
        self.SendText("You have revealed that you are a Mayor")
        return CommandResult.Done()
    
    def Eat(self, eatId):
        if self.role not in Role.werewolves:
            self.SendText("You're not a Werewolf")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if self.drunk:
            self.SendText("Go home you're drunk")
            return CommandResult.Failed()
        if eatId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        if self not in self.room.votes[Role.werewolf.id].haventVoted and not self.room.allowRevote:
            self.SendText("You have already choosen who to eat or it's not your turn.")
            return CommandResult.Failed()
        
        eat = self.room.playersById[eatId]
        if eat == self:
            self.SendText("You can't eat yourself")
            return CommandResult.Failed()
        if eat.role in Role.werewolves:
            self.SendText("You can't eat fellow Werewolf")
            return CommandResult.Failed()
        if not eat.alive:
            self.SendText("The one you want to eat is already dead")
            return CommandResult.Failed()
        
        if self.originalRole == Role.clumsy:
            return self.room.votes[Role.werewolf.id].VoteRandom()
        return self.room.votes[Role.werewolf.id].Vote(self, eat)
        
    
    def Kill(self, killId):
        if self.role != Role.serialKiller:
            self.SendText("You're not a Serial Killer")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if killId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        if self.kill and not self.room.allowRevote:
            self.SendText("You have already choosen who to kill.")
            return CommandResult.Failed()
        
        kill = self.room.playersById[killId]
        if kill == self:
            self.SendText("You can't kill yourself")
            return CommandResult.Failed()
        if not kill.alive:
            self.SendText("The one you want to kill is already dead")
            return CommandResult.Failed()
        if kill == self.kill:
            self.SendText("It's the same guuuyyyyyyyyy")
            return CommandResult.Failed()
        
        self.kill = kill
        self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
        
        
    def Convert(self, convertId):
        if self.role != Role.cultist:
            self.SendText("You're not a Cultist")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if convertId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        if self not in self.room.votes[Role.cultist.id].haventVoted and not self.room.allowRevote:
            self.SendText("Either you have already choosen who to convert or it's not your turn.")
            return CommandResult.Failed()
        
        convert = self.room.playersById[convertId]
        if convert == self:
            self.SendText("You can't convert yourself")
            return CommandResult.Failed()
        if convert.role == Role.cultist:
            self.SendText("You can't convert fellow Cultist")
            return CommandResult.Failed()
        if not convert.alive:
            self.SendText("The one you want to convert is already dead")
            return CommandResult.Failed()
        
        if self.originalRole == Role.clumsy:
            return self.room.votes[Role.cultist.id].VoteRandom()
        return self.room.votes[Role.cultist.id].Vote(self, convert)
        
        
    def ShootGunner(self, shootId):
        if self.role != Role.gunner:
            self.SendText("You're not a Gunner")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if self.ammo < 1:
            self.SendText("You're out of bullets")
            return CommandResult.Failed()
        if self.done:
            self.SendText("You've already shot someone")
            return CommandResult.Failed()
        if shootId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        
        shoot = self.room.playersById[shootId]
        if shoot == self:
            self.SendText("You can't shoot yourself")
            return CommandResult.Failed()
        if not shoot.alive:
            self.SendText("The one you want to shoot is already dead")
            return CommandResult.Failed()
        with self.lock:
            shoot.Die(self.role)
            self.ammo -= 1
            self.done = True
            self.room.SendText("%s the Gunner shot %s" % (self.name, shoot.name))
        self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
        
    def ShootHunter(self, shootId):
        if self.role != Role.hunter:
            self.SendText("You're not a Hunter")
            return CommandResult.Failed()
        if self.alive:
            self.SendText("You're not dying")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if shootId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        
        shoot = self.room.playersById[shootId]
        if shoot == self:
            self.SendText("You can't shoot yourself. It will all be over soon anyway")
            return CommandResult.Failed()
        if not shoot.alive:
            self.SendText("The one you want to shoot is already dead")
            return CommandResult.Failed()
        
        if not shoot.role.team != Team.cultist:
            return CommandResult.Failed()
        
        self.kill = shoot
        self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
        
    def ShootCH(self, shootId):
        if self.role != Role.cultistHunter:
            self.SendText("You're not a Cultist Hunter")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if self.kill and not self.room.allowRevote:
            self.SendText("You have choosen who to hunt")
            return CommandResult.Failed()
        if shootId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        
        shoot = self.room.playersById[shootId]
        if shoot == self:
            self.SendText("You can't shoot yourself")
            return CommandResult.Failed()
        if not shoot.alive:
            self.SendText("The one you want to shoot is already dead")
            return CommandResult.Failed()
        if shoot == self.kill:
            self.SendText("It's the same guuuyyyyyyyyy")
            return CommandResult.Failed()
        
        self.kill = shoot
        self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
        
    def SpreadDust(self):
        if self.role != Role.blacksmith:
            self.SendText("You're not a Blacksmith")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if self.ammo < 1:
            self.SendText("You're out of silver dust")
            return CommandResult.Failed()
        for x in self.room.alives:
            x.protection = 1
        self.room.SendText("%s the Blacksmith spread Silver Dust all over the village!\nEveryone should be safe from Werewolves tonight as long as they don't do anything dangerous" % self.name)
        self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
        
    def PairLovers(self, loverId):
        if self.role != Role.cupid:
            self.SendText("You're not a Cupid")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if loverId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        pair = self.room.lovers[self]
        if len(pair) > 1:
            if self.room.allowRevote:
                self.room.AddWaitingCommand(self)
                self.room.lovers[self] = []
            else:
                self.SendText("You have already set a pair of lovers")
                return CommandResult.Failed()
        
        lover = self.room.playersById[loverId]
        if not lover.alive:
            self.SendText("The one you want to pair as Lovers is already dead")
            return CommandResult.Failed()
        if lover in pair:
            self.SendText("You have already choosen %s" % lover.name)
        if lover.lover:
            self.SendText("%s already has someone he loves" % lover.name)
            
        pair.append(lover)
        if len(pair) == 1:
            self.SendText("Please choose the second person")
        else:
            pair[0].lover = pair[1]
            pair[1].lover = pair[0]
            self.SendText("You have set %s and %s to be lovers!" % (pair[0].name, pair[1].name))
            self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
            
        
    def SleepSomewhereElse(self, otherId):
        if self.role != Role.harlot:
            self.SendText("You're not a Harlot")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if self.houseOwner != self and not self.room.allowRevote:
            self.SendText("You are already at someone else's house")
            return CommandResult.Failed()
        if otherId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        
        other = self.room.playersById[otherId]
        if other == self:
            self.SendText("You can't shoot yourself")
            return CommandResult.Failed()
        if not other.alive:
            self.SendText("Ya can't sleep with a dead body ya sicko")
            return CommandResult.Failed()
        if other == self.houseOwner:
            self.SendText("It's the same guuuyyyyyyyyy")
            return CommandResult.Failed()
        
        self.houseOwner = other
        other.freeloader = self
        self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
    
    def Protect(self, otherId):
        if self.role != Role.guardianAngel:
            self.SendText("You're not a Guardian Angel")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if self.houseOwner != self and not self.room.allowRevote:
            self.SendText("You are already protecting someone else's house")
            return CommandResult.Failed()
        if otherId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        
        other = self.room.playersById[otherId]
        if other == self:
            self.SendText("You can't protect yourself")
            return CommandResult.Failed()
        if not other.alive:
            self.SendText("You can't protect a dead person.")
            return CommandResult.Failed()
        if other == self.houseOwner:
            self.SendText("It's the same guuuyyyyyyyyy")
            return CommandResult.Failed()
            
        
        if self.houseOwner and self.houseOwner.protection==2:
            self.houseOwner.protection = 0
        self.houseOwner = other
        other.protection = 2
        self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
        
    def ChooseMaster(self, masterId):
        if self.role not in [Role.wildChild, Role.doppelganger]:
            self.SendText("You're neither a Wild Child nor a Doppelganger")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if self.master and not self.room.allowRevote:
            self.SendText("You have already choosen %s" % self.master.name)
            return CommandResult.Failed()
        if masterId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        
        master = self.room.playersById[masterId]
        if master == self:
            self.SendText("You can't choose yourself")
            return CommandResult.Failed()
        if not master.alive:
            self.SendText("The one you want to choose is already dead")
            return CommandResult.Failed()
        if master == self.master:
            self.SendText("It's the same guuuyyyyyyyyy")
            return CommandResult.Failed()
        
        self.master = master
        self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
        
    def SeeRole(self, seeId):
        if self.role not in Role.seers:
            self.SendText("You're neither a Seer nor a Sorcerer")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if self.getRole != self and not self.room.allowRevote:
            self.SendText("You've already choosen someone to see through")
            return CommandResult.Failed()
        if seeId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        
        see = self.room.playersById[otherId]
        if see == self:
            self.SendText("You can't see through yourself")
            return CommandResult.Failed()
        if not see.alive:
            self.SendText("The one you want to see through is already dead")
            return CommandResult.Failed()
        if see == self.getRole:
            self.SendText("It's the same guuuyyyyyyyyy")
            return CommandResult.Failed()
        
        self.getRole = see
        self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
        
    def Investigate(self, suspectId):
        if self.role != Role.detective:
            self.SendText("You're not a Detective")
            return CommandResult.Failed()
        if not self.alive:
            self.SendText("You're dead")
            return CommandResult.Failed()
        if not self.myTurn:
            self.SendText("It's not your turn")
            return CommandResult.Failed()
        if self.getRole != self and not self.room.allowRevote:
            self.SendText("You've already choosen someone to investigate")
            return CommandResult.Failed()
        if suspectId not in self.room.playersById:
            self.SendText("Invalid ID")
            return CommandResult.Failed()
        
        suspect = self.room.playersById[otherId]
        if suspect == self:
            self.SendText("You can't investigate yourself")
            return CommandResult.Failed()
        if not suspect.alive:
            self.SendText("The one you want to investigate is already dead")
            return CommandResult.Failed()
        if suspect == self.getRole:
            self.SendText("It's the same guuuyyyyyyyyy")
            return CommandResult.Failed()
        
        self.getRole = suspect
        self.room.RemoveWaitingCommand(self)
        return CommandResult.Done()
        
        
    def GetRole(self):
        if self.getRole:
            if not self.alive or not self.getRole.alive:
                self.getRole = None
                return 
            if self.role in [Role.fool, Role.seer]:
                if self.room.phase == RoomPhase.day:
                    if self.role == Role.seer:
                        role = self.getRole.role
                    else:
                        role = choice(Role.validRoles)
                    
                    self.SendText("You have seen through %s and found out that he's a %s" % (self.getRole.name, role.name))
            elif self.role == Role.sorcerer:
                if self.room.phase == RoomPhase.day:
                    role = self.getRole.role
                    if role == Role.seer or role in Role.werewolves:
                        self.SendText("You have seen through %s and found out that he's a %s" % (self.getRole.name, role.name))
                    else:
                        self.SendText("You couldn't see through %s. At least, you know that he's neither a Werewolf nor a Seer" % self.getRole.name)
            elif self.role == Role.detective:
                if self.room.phase == RoomPhase.lynchVote:
                    role = self.getRole.role
                    if role != Role.hunter and role in Role.visitorKillers:
                        tell = randint(0, 9)
                        #if tell < 1 and role != Role.werewolf:
                        #    self.Die(role)
                        #    return True
                        if tell < 4:
                            self.getRole.SendText("%s seems to be sneaking around you very much. What's his problem?" % self.name)
                    self.SendText("You have investigated %s and found out that he's a %s" % (self.getRole.name, self.getRole.role.name))
                    
            self.getRole = None
        
    def DoKill(self):
        if self.kill:
            if not self.kill.alive:
                self.kill = None
                return
            if self.role == Role.serialKiller:
                self.kill.Die(self.role)
            elif self.role == Role.cultistHunter:
                if self.kill.role.team == Team.cultist:
                    self.SendText("%s is a Cultist" % self.kill.name)
                    self.kill.Die(self.role)
                else:
                    self.SendText("%s is not a Cultist" % self.kill.name)
            self.kill = None
            
    @property
    def myTurn(self):
        if self.role.actionPhase == ActionPhase.firstNight:
            return self.room.phase == RoomPhase.night and self.room.day - self.dayRoleSet == 1
        elif self.role.actionPhase == ActionPhase.anyday:
            return True
        else:
            return self.role.actionPhase == self.room.phase
            
        
        
        
class Pending(object):
    def __init__(self, method, args, kwargs, requireAlive=None, *args2, **kwargs2):
        args.extend(args2)
        kwargs.update(kwargs2)
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.requireAlive = requireAlive
        
        
    def Call(self):
        if self.requireAlive and not self.requireAlive.alive:
            return
        return self.method(*self.args, **self.kwargs)
        
lastRoomId = 0
roomIdByObj = {}
roomByObj = {}
roomById = {}

lock = Lock()

class Room(object):
    def __init__(self, obj, creator, nightDuration=90, dayDuration=90, lynchVoteDuration=60, hunterDeathDuration = 30, allowRevote=False, noVillager=True, autostart=300, quick=True, *args, **kwargs):
        global lock
        with lock:
            if obj in roomIdByObj:
                self.id = roomIdByObj[self]
            else:
                global lastRoomId
                lastRoomId += 1
                self.id = lastRoomId
            global roomById
            roomById[self.id] = self
            global roomByObj
            roomByObj[obj] = self
            global roomIdByObj
            roomIdByObj[obj] = self.id
        self.lock = Lock()
        self.obj = obj
        self.players = []
        self.playersByObj = {}
        self.day=0
        self._1phase = RoomPhase.waiting
        self.realPhase = RoomPhase.waiting
        self.votes = {}
        self.lovers = {}
        self.nightDuration=nightDuration
        self.dayDuration=dayDuration
        self.lynchVoteDuration=lynchVoteDuration
        self.hunterDeathDuration = hunterDeathDuration
        self.werewolfKill = 1
        self.lastCultistId = 0
        self.lastPlayerId = 0
        self.playersByRole = {}
        self.cultists = []
        self.werewolves = []
        self.deadHunters = []
        self.harlots = []
        self.guardianAngels = []
        self.seers = []
        self.traitors = []
        self.beholders = []
        self.apprenticeSeers = []
        self.masons = []
        self.kickeds = []
        self.cond = Condition()
        self.allowRevote = allowRevote
        self.noVillager = noVillager
        self.playersById = {}
        self.playersByObj = {}
        self.shouldTellBeholders = False
        self.shouldTellWerewolves = False
        self.shouldTellMasons = False
        self.shouldTellCultists = False
        self.quick = quick
        self.hasCultist = False
        self.waitingCommands = []
        self.room = self
        AddAtExit(self, self.__del__)
        buts = Buttons("Werewolf game created", "Werewolf game created")
        buts.AddButton("Join", "/ww join", "\nType '/ww join' to join")
        buts.AddButton("Leave", "/ww leave", "\nType '/ww leave' to leave")
        buts.AddButton("Force Start", "/ww forcestart", "\nType '/ww forcestart' to force start")
        self.SendButtons(buts)
        self.AddPlayer(creator)
        if autostart:
            self.DelayedStart(autostart, autostart)
            
    def __del__(self):
        with self.lock:
            if self.phase > RoomPhase.idling and self.phase < RoomPhase.done:
                self.phase = RoomPhase.idling
                self.SendText("Shutting down")
                DelAtExit(self)
            
    @property
    def name(self):
        return self.obj.name
        
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
        
        
    def DelayedStart(self, delay, autostart):
        return self.obj.client.Thread(self._1DelayedStart, [delay, autostart])
        
    def _1DelayedStart(self, delay, autostart):
        if self.phase != RoomPhase.waiting:
            return CommandResult.Failed()
        with self.cond:
            self.StartCountdown(time()+delay)
            self.cond.wait(delay)
        if self.phase == RoomPhase.waiting:
            return self.Start(autostart)
        
    def StartCountdown(self, end, s="Werewolf starting in %s", phase=RoomPhase.waiting):
        return self.obj.client.Thread(self.Countdown, [end, s, phase])
        
    def Countdown(self, end, s="Werewolf starting in %s", phase=RoomPhase.waiting):
        if self.phase != phase:
            return
        delay = end-time()
        delay+=5
        if delay > 60:
            mins = delay//60
            sec = delay%60
            sec -= 5
            delay-=5
            if mins > 1:
                if sec > 0:
                    si = "%d minutes and %d seconds" % (mins, sec)
                else:
                    si = "%d minutes" % mins
            else:
                if sec > 0:
                    si = "a minute and %d seconds" % sec
                else:
                    si = "a minute"
            self.SendText(s % si)
            with self.cond:
                if delay >= 120:
                    self.cond.wait(60)
                elif delay > 60:
                    self.cond.wait(delay-60)
                else:
                    self.cond.wait(30)
        else:
            delay -= 5
            self.SendText(s % ("%d seconds" % delay))
            with self.cond:
                if delay > 30:
                    self.cond.wait(30)
                elif delay > 20:
                    self.cond.wait(20)
                elif delay > 5:
                    self.cond.wait(delay)
        if self.phase == phase and (end-time()) > 5:
            return self.Countdown(end, s, phase)
        
        
        
        
    def HandleCommand(self, message, action='', eat=0, kill=0, convert=0, shoot=0, pair=0, see=0, master=0, protect=0, lynch=0, *args, **kwargs):
        sender = message.sender
        chatroom = message.chatroom
        client = message.client
        if not client.hasOA or not client.hasUser:
            message.ReplyText("Sorry Werewolf needs both OAClient and UserClient")
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
            message.ReplyText("%s, please accept the group invitation" % sender.name)
            return CommandResult.Failed()
        elif action == 'join':
            self.AddPlayer(sender)
            return CommandResult.Done()
        elif sender not in self.playersByObj:
            message.ReplyText("Please join the game first.")
            return CommandResult.Failed()
        elif action == 'forcestart':
            return self.ForceStart(sender)
        elif action == 'leave':
            return CommandResult.Done()
        else:
            return self.playersByObj[sender].HandleCommand(action=action, eat=eat, kill=kill, convert=convert, shoot=shoot, pair=pair, see=see, master=master, protect=protect, lynch=lynch, *args, **kwargs)
            
    def Remove(self):
        with self.lock:
            self.phase = RoomPhase.idling
            del roomByObj[self.obj]
            del roomById[self.id]
            del roomIdByObj[self.obj]
            
        
    def Tell(self, about, to=None):
        if not to:
            to = about
        for x in to:
            x.SendTeamNames(about)
        
    @property
    def phase(self):
        return self._1phase
    
    @phase.setter
    def phase(self, value):
        self._1phase = value
        self.realPhase = value
        
    def TellBeholders(self):
        self.Tell(self.seers, self.beholders)
        self.shouldTellBeholders=False
        
    def TellWerewolves(self):
        self.Tell(self.werewolves)
        self.shouldTellWerewolves=False
        
    def TellMasons(self):
        self.Tell(self.masons)
        self.shouldTellMasons=False
        
    def TellCultists(self):
        self.Tell(self.cultists)
        self.shouldTellCultists=False
            
    def TryTellBeholders(self):
        if self.shouldTellBeholders:
            self.TellBeholders()
            
    def TryTellWerewolves(self):
        if self.shouldTellWerewolves:
            self.TellWerewolves()
            
    def TryTellMasons(self):
        if self.shouldTellMasons:
            self.TellMasons()
            
    def TryTellCultists(self):
        if self.shouldTellCultists:
            self.TellCultists()
            
    def TryTellAll(self):
        self.TryTellBeholders()
        self.TryTellWerewolves()
        self.TryTellMasons()
        self.TryTellCultists()
        
    def AddPlayer(self, obj):
        if self.phase != RoomPhase.waiting:
            self.SendText("%s, the game already started" % obj.name)
            return 
        if obj in self.playersByObj:
            self.SendText("%s, You have already joined" % obj.name)
            return
        p = Player(obj, self)
        p.SendText("You have just joined")
        self.SendText("%s have successfully joined" % p.name)
        return p
    
    def Leave(self, obj):
        if self.phase != RoomPhase.waiting:
            self.SendText("%s, the game has already begun" % obj.name)
            return 
        if obj not in self.playersByObj:
            self.SendText("%s, You haven't even joined" % obj.name)
            return
        p = self.playersByObj[obj]
        self.SendText("%s has left the game" % p.name)
        return p.Remove()
        
        
    def SendText(self, text):
        if text.startswith("[WW #"):
            return self.obj.SendText(text)
        return self.obj.SendText("[WW #%d]\n%s" % (self.id, text))
    
    def SendButtons(self, buttons):
        if not buttons.columnText.startswith("[WW #"):
            buttons.SetColumnText("[WW #%d]\n%s" % (self.id, buttons.columnText))
            buttons.SetAltTextHeader("[WW #%d]\n%s" % (self.id, buttons.altTextHeader))
        return self.obj.SendButtons(buttons)
            
    def FreeloaderDie(self):
        for harlot in list(self.harlots):
            if harlot.houseOwner != harlot:
                if harlot.houseOwner.alive:
                    if harlot.houseOwner.role in Role.visitorKillers:
                        harlot.Die(None)
                        self.SendText("%s the Harlot's dead body was found outside this morning. What could've happened?" % harlot.name)
                        harlot.houseOwner.SendText("The Harlot visited you last night. Defend yourself." % harlot.name)
                else:
                    self.SendText("%s the Harlot was also in %s's house last night. Guess what?" % harlot.name)
                    harlot.Die(harlot.houseOwner.killerRole)
        for angel in list(self.guardianAngels):
            if angel.houseOwner != angel:
                if angel.houseOwner.role in Role.werewolves:
                    tell = randint(0, 4)
                    if tell < 2:
                        angel.houseOwner.SendText("%s the Guardian Angel tried to protect you lol" % angel.name)
                        if tell < 1:
                            self.SendText("%s the Guardian Angel unknowingly tried to protect a Werewolf! The Werewolf found out and killed him" % angle.name)
                            angel.Die(Role.werewolves)
                elif angel.houseOwner.alive:
                    angel.houseOwner.SendText("A Guardian Angel protected your house from Werewolves last night")
                    
                    
                    
        
    def InitRoles(self):
        for player in self.alives:
            player.InitRole()
        self.TryTellAll()
        
    def Eat(self):
        eats = self.votes[Role.werewolf.id].votees
        if len(eats) == 0:
            print("EATS IS EMPTY")
            return
        print("EATS0 %s" % eats.items())
        eats = [(v, k) for k, v in eats.items() if v>0 and k.alive]
        print("EATS1 %s" % eats)
        self.votes[Role.werewolf.id].Clear()
        if len(eats) == 0:
            print("EATS IS EMPTY 2 ")
            return
        eats.sort(reverse=True)
        m = eats[0][0]
        eatsMost = [x for x in eats if x[0] == m]
        lenEatsMost = len(eatsMost)
        if lenEatsMost < self.werewolfKill:
            eats2 = eats[len(eatsMost)]
            m = eats2[0][0]
            eats2 = [x for x in eats2 if x[0] == m]
            eatsMost.append(choice(eats2))
        self.werewolfKill=1
        for werewolf in self.werewolves:
            werewolf.drunk = False
            
        hasAlpha = len([x for x in self.werewolves if x.alive and x.role == Role.alphaWolf]) > 0
        
        for eat in eatsMost:
            eat = eat[1]
            if eat.protection:
                self.SendText(eat.name + " was about to be attacked by a werewolf, but he got some protection")
                s = "Yall went to %s's home to eat her but he got some protection lol go home." % eat.name
                for ww in self.werewolves:
                    ww.SendText(s)
                continue
            elif eat.role == Role.harlot and eat.houseOwner and eat.houseOwner != eat:
                s = "Yall went to %s's home to eat her but she wasn't home." % eat.name
                for ww in self.werewolves:
                    ww.SendText(s)
                continue
            elif eat.role == Role.cursed:
                eat.role = Role.werewolf
                eat.SendText('The Werewolf tried to kill you! You, who were a Cursed, are now a Werewolf!')
                eat.InitRole()
                s = "Yall tried to eat %s who is actually the Cursed!\nHe is now a fellow Werewolf." % eat.name
                for ww in self.werewolves:
                    ww.SendText(s)
                continue
            elif eat.role == Role.hunter:
                wwLen = len(self.werewolves)
                if randint(0, 9) < 3 + (wwLen-1)*2:
                    randomWw = self.werewolves.pop(randint(0, wwLen-1))
                    randomWw.Die(eat.role)
                    if wwLen > 1:
                        eat.Die(Role.werewolf)
                        s = 'The Werewolf attacked %s the Hunter! He managed to get %s, one of them, down, but he was outnumbered' % (eat.name, randomWw.name)
                        self.SendText(s)
                        continue
                    else:
                        self.SendText('%s the werewolf tried to attack the Hunter! However, he had the [Quickdraw] ability not on cooldown. Death to Werewolves!' % randomWw.name)
                        continue
                else:
                    eat.Die(Role.werewolf)
                    
                    s = "Yall ate %s who is actually the Hunter!\nFortunately, his [Quickdraw] ability is on cooldown." % eat.name
                    for ww in self.werewolves:
                        ww.SendText(s)
                    continue
                continue
            elif eat.role == Role.serialKiller:
                randomWw = self.werewolves.pop(randint(0, len(self.werewolves)-1))
                randomWw.Die(eat.role)
                self.SendText("The Werewolves tried to attack the Serial Killer! That was a bad move. %s the Werewolf got killed instead." % randomWw.name)
                continue
            elif hasAlpha and randint(0,4) < 1:
                add = ''
                if eat.role == Role.drunk:
                    add = '\nBtw he was the Drunk so yall will skip one turn'
                    for ww in self.werewolves:
                        ww.drunk = True
                        
                eat.role = Role.werewolf
                eat.SendText("You were bitten by the Alpha Wolf, and thus, turned into a Werewolf!")
                eat.InitRole()
                s = "%s was bitten by the Alpha Wolf and turned into a fellow Werewolf.%s" % (eat.name, add)
                for ww in self.werewolves:
                    ww.SendText(s)
                continue
            else:
                eat.Die(Role.werewolf)
                if eat.role == Role.drunk:
                    s = "Yall ate %s the Drunk so now you're all drunk and will skip one turn" % eat.name
                    for ww in self.werewolves:
                        ww.drunk = True
                        ww.SendText(s)
                continue
                
    def GetRole(self):
        for player in list(self.alives):
            player.GetRole()
                
    def DoKill(self):
        for player in list(self.alives):
            player.DoKill()
                
        
                
    def Lynch(self):
        print("LYNCH")
        lynches = self.votes[Role.villager.id].votees
        if len(lynches) == 0:
            self.SendText("Vote lah kampret")
            return
        print("LYNCH0 %s" % lynches)
        lynches = [(v, k) for k, v in lynches.items() if v>0 and k.alive]
        print("LYNCH1 %s" % lynches)
        self.votes[Role.villager.id].Clear()
        lynchesLen = len(lynches)
        if lynchesLen == 0:
            self.SendText("Somehow people yall voted for are dead")
            return
        elif lynchesLen > 1:
            lynches.sort(reverse=True)
            if lynches[0][0] == lynches[1][0]:
                self.SendText("MICIN")
                return
        lynch = lynches[0][1]
        
        if lynch.role == Role.prince:
            if not lynch.princeRevealed:
                self.SendText("Yall were gonna lynch %s but then he revealed that he's the Prince! Yall can rethink your decision" % lynch.name)
                lynch.princeRevealed = True
                return
        elif lynch.role == Role.tanner:
            self.SendText("YALL LYNCHED %s THE TANNER" % lynch.name.upper())
            return self.Win(Team.tanner)
            
        
        lynch.Die(Role.villager)
        print("LYNCHDONE")
        return
                
        
    def Convert(self):
        converts = self.votes[Role.cultist.id].votees
        if len(converts) == 0:
            return
        converts = [(v, k) for k, v in converts.items() if v>0 and k.alive]
        self.votes[Role.cultist.id].Clear()
        if len(converts) == 0:
            return
        converts.sort(reverse=True)
        converts = [x for x in converts if x[0] == converts[0][0]]
        convert = choice(converts)[1]

        cultistLen = len(self.cultists)
        if convert.role == Role.cultistHunter:
            if cultistLen > 0:
                newestCultist = None
                newestCultist = self.cultists[-1]
                for cultist in self.cultists:
                    if cultist.cultistId > newestCultist.cultistId:
                        newestCultist = cultist
                newestCultist.Die(convert.role)
                self.SendText(newestCultist.name + " was killed by a Cultist Hunter because the cult unknowingly tried to convert the Cultist Hunter lol")
                return
        elif convert.role == Role.hunter and cultistLen > 0 and randint(0,3) < 1:
            randomCultist = self.cultists.pop(randint(0, cultistLen-1))
            randomCultist.Die(convert.role)
            self.SendText("The cult tried to convert the Hunter. They failed and even got %s, one of their members, down." % randomCultist.name)
            return
        elif convert.role not in Role.unconvertible:
            convert.role = Role.cultist
            convert.SendText("You have been converted into a Cultist.")
            convert.InitRole()
            msg = convert.name + " is now a fellow Cultist."
            for cultist in self.cultists:
                cultist.SendText(msg)
            return
        
        
    def Status(self):
        #alives = [x for x in self.players if x.alive]
        #deads = [x for x in self.players if x.alive == False]
        alives = self.alives
        deads = self.deads
        s = 'Day : %d\nPhase : %s\nPlayers:' % (self.day, RoomPhase.toString[self.phase].title())
        for x in alives:
            s = s + "\n%s, alive" % x.obj.name
        for x in deads:
            s = s + "\n%s, %s, dead" % (x.obj.name, x.role.name)
        self.SendText(s)
        return CommandResult.Done()
        
        
    def Win(self, winningTeam):
        #alives = [x for x in self.players if x.alive]
        #deads = [x for x in self.players if x.alive == False]
        alives = self.alives
        deads = self.deads
        if winningTeam:
            aliveWinners = [x for x in alives if x.role.team == winningTeam]
            aliveLosers = [x for  x in alives if x.role.team != winningTeam]
            deadWinners = [x for x in deads if x.role.team == winningTeam]
            deadLosers = [x for x in deads if x.role.team != winningTeam]
            
            s = 'Game over\nDay : %d\nPhase : %s\nWinners:' % (self.day, RoomPhase.toString[self.phase].title())
            for x in aliveWinners:
                s = s + "\n%s, %s, alive, won" % (x.obj.name, x.role.name)
            for x in deadWinners:
                s = s + "\n%s, %s, dead, won" % (x.obj.name, x.role.name)
            s = s + "\nLosers:"
            for x in aliveLosers:
                s = s + "\n%s, %s, alive, lost" % (x.obj.name, x.role.name)
            for x in deadLosers:
                s = s + "\n%s, %s, dead, lost" % (x.obj.name, x.role.name)
            self.SendText(s)
        else:
            s = 'Game over\nDay : %d\nPhase : %s\nLosers:' % (self.day, RoomPhase.toString[self.phase])
            for x in alives:
                s = s + "\n%s, %s, alive, lost" % (x.obj.name, x.role.name)
            for x in deads:
                s = s + "\n%s, %s, dead, lost" % (x.obj.name, x.role.name)
            self.SendText(s)
            
        for x in self.kickeds:
            self.x.obj.InviteInto(self.obj) 
        self.phase = RoomPhase.done
        self.Remove()
        return True
            
            
    def HunterDeathVote(self):
        if len(self.deadHunters) == 0:
            return
        realPhase = self.phase
        self._1phase = RoomPhase.hunter
        with self.cond:
            self.cond.notifyAll()
        #something2
        players = list(self.deadHunters)
        self.deadHunters = []
        self.room.ExtendWaitingCommand(players)
        for player in players:
            buts = Buttons("You can choose shoot someone by typing '/ww room=%d shoot=<id>' with the ids below." % self.id, "You can choose to shoot someone.")
            candidates = [x for x in self.alives if x != player]
            for x in candidates:
                buts.AddButton(
                    x.name,
                    "/ww room=%d shoot=%d" % (self.id, x.id),
                    "\n%s\t : %s" % (x.id, x.name)
                )
            player.SendButtons(buts)
        
        with self.cond:
            self.SendText("Some hunters are gonna die! They have %g seconds to shoot as death comes closer" % self.hunterDeathDuration)
            self.StartCountdown(time()+self.hunterDeathDuration, "Dying hunters have %s left", RoomPhase.hunter)
            self.cond.wait(self.hunterDeathDuration)
        self.DoKill()
        self.phase = realPhase
        return True
        
    def Night(self):
        with self.lock:
            self.phase = RoomPhase.night
            self.waitingCommands = []
            with self.cond:
                self.cond.notifyAll()
            if self.hasCultist:
                self.room.ExtendWaitingCommand(self.cultists)
                candidates = [x for x in self.alives if x.role != Role.cultist]
                self.votes[Role.cultist.id].Set(self.cultists, candidates)
                buts = Buttons("You can vote to convert someone into a cultist by typing '/ww room=%d convert=<id>' with the ids below" % self.id, "You can vote to convert someone into a cultist")
                for x in candidates:
                    buts.AddButton(
                        x.name,
                        "/ww room=%d convert=%d" % (self.id, x.id),
                        "\n%s\t : %s" % (x.id, x.name)
                    )
                for x in self.cultists:
                    x.SendButtons(buts)
            if self.hasWerewolf:
                self.room.ExtendWaitingCommand(self.werewolves)
                candidates = [x for x in self.alives if x.role not in Role.werewolves]
                self.votes[Role.werewolf.id].Set(self.werewolves, candidates)
                buts = Buttons("You can vote to eat someone by typing '/ww room=%d eat=<id>' with the ids below" % self.id, "You can vote to eat someone")
                for x in candidates:
                    buts.AddButton(
                        x.name,
                        "/ww room=%d eat=%d" % (self.id, x.id),
                        "\n%s\t : %s" % (x.id, x.name)
                    )
                for x in self.werewolves:
                    x.SendButtons(buts)
            for player in self.alives:
                player.getRole = None
                player.done = False
                if player.myTurn:
                    if player.role == Role.cultist:
                        pass
                    elif player.role == Role.guardianAngel:
                        self.room.AddWaitingCommand(player)
                        buts = Buttons("You can choose to protect someone's house from Werewolves by typing '/ww room=%d protect=<id>' with the ids below" % self.id, "You can choose to protect someone's house from Werewolves")
                        candidates = [x for x in self.alives if x != player]
                        for x in candidates:
                            buts.AddButton(
                                x.name,
                                "/ww room=%d protect=%d" % (self.id, x.id),
                                "\n%s\t : %s" % (x.id, x.name)
                            )
                        player.SendButtons(buts)
                    elif player.role == Role.harlot:
                        self.room.AddWaitingCommand(player)
                        buts = Buttons("You can choose to sleep in someone's house by typing '/ww room=%d sleep=<id>' with the ids below" % self.id, "You can choose to sleep in someone's house")
                        if self.allowRevote:
                            candidates = [x for x in self.alives]
                        else:
                            candidates = [x for x in self.alives if x != player]
                        for x in candidates:
                            buts.AddButton(
                                x.name,
                                "/ww room=%d sleep=%d" % (self.id, x.id),
                                "\n%s\t : %s" % (x.id, x.name)
                            )
                        player.SendButtons(buts)
                    elif player.role == Role.cultistHunter:
                        self.room.AddWaitingCommand(player)
                        buts = Buttons("You can choose hunt someone by typing '/ww room=%d shoot=<id>' with the ids below. If he's a cultist, he will die." % self.id, "You can choose to hunt someone. If he's a cultist, he will die.")
                        candidates = [x for x in self.alives if x != player]
                        for x in candidates:
                            buts.AddButton(
                                x.name,
                                "/ww room=%d shoot=%d" % (self.id, x.id),
                                "\n%s\t : %s" % (x.id, x.name)
                            )
                        player.SendButtons(buts)
                    elif player.role == Role.serialKiller:
                        self.room.AddWaitingCommand(player)
                        buts = Buttons("You can choose kill someone by typing '/ww room=%d kill=<id>' with the ids below" % self.id, "You can choose to kill someone")
                        candidates = [x for x in self.alives if x != player]
                        for x in candidates:
                            buts.AddButton(
                                "\n%s\t : %s" % (x.id, x.name),
                                x.name,
                                "/ww room=%d kill=%d" % (self.id, x.id)
                            )
                        player.SendButtons(buts)
                    elif player.role in Role.seers:
                        self.room.AddWaitingCommand(player)
                        buts = Buttons("You can choose see through someone's role by typing '/ww room=%d see=<id>' with the ids below" % self.id, "You can choose to see through someone's role")
                        candidates = [x for x in self.alives if x != player]
                        for x in candidates:
                            buts.AddButton(
                                x.name,
                                "/ww room=%d see=%d" % (self.id, x.id),
                                "\n%s\t : %s" % (x.id, x.name)
                            )
                        player.SendButtons(buts)
                    elif player.role in Role.werewolves:
                        pass
                    else:
                        self.SendText("MISSED NIGHT ROLE %s" % player.role.name)
            self.Status()
            with self.cond:
                self.cond.notifyAll()
        
        with self.cond:
            self.SendText("Yall night players have %g seconds to do your stuff" % self.nightDuration)
            self.StartCountdown(time()+self.nightDuration, "Night players have %s left", RoomPhase.night)
            self.cond.wait(self.nightDuration)
        if self.phase == RoomPhase.night:
            with self.lock:
                self.Eat()
                self.DoKill()
                if self.CheckWin():
                    return True
                self.Convert()
                self.GetRole()
                self.DoKill()
                if self.CheckWin():
                    return True
                while len(self.deadHunters) > 0:
                    if self.HunterDeathVote() and self.CheckWin():
                        return True
            return self.Day()
    
    def Day(self):
        with self.lock:
            self.phase = RoomPhase.day
            self.day+=1
            self.waitingCommands = []
            with self.cond:
                self.cond.notifyAll()
            for player in list(self.alives):
                player.protection = 0
                if self.day - player.dayLastSeen > 2:
                    player.Die(Role.none)
                    continue
                if player.role == Role.harlot:
                    player.houseOwner = player
                    player.freeloader = None
                elif player.myTurn:
                    if player.role == Role.mayor and not player.mayorRevealed:
                        self.room.AddWaitingCommand(player)
                        buts = Buttons("You can choose to reveal your role as a Mayor by typing '/ww room=%d action=reveal'" % self.id, "You can choose to reveal your role as a Mayor")
                        buts.AddButton(
                            "Reveal",
                            "/ww room=%d action=reveal" % self.id,
                            ""
                        )
                        player.SendButtons(buts)
                    elif player.role == Role.blacksmith:
                        if player.ammo:
                            self.room.AddWaitingCommand(player)
                            player.done = False
                            buts = Buttons("You can choose to spread silver dust all over the village by typing '/ww room=%d action=silver'. You can do it %d times" % (self.id, player.ammo), "You can choose to spread silver dust all over the village. You can do it %d times" % player.ammo)
                            buts.AddButton(
                                "Reveal",
                                "/ww room=%d action=silver" % self.id,
                                ""
                            )
                            player.SendButtons(buts)
                    elif player.role == Role.gunner:
                        if player.ammo:
                            self.room.AddWaitingCommand(player)
                            player.done = False
                            buts = Buttons("You can choose shoot someone by typing '/ww room=%d shoot=<id>' with the ids below. You have %d bullets" % (self.id, player.ammo), "You can choose to shoot someone. You have %d bullets" % player.ammo)
                            candidates = [x for x in self.alives if x != player]
                            for x in candidates:
                                buts.AddButton(
                                    x.name,
                                    "/ww room=%d shoot=%d" % (self.id, x.id),
                                    "\n%s\t : %s" % (x.id, x.name)
                                )
                            player.SendButtons(buts)
                    elif player.role == Role.detective:
                        self.room.AddWaitingCommand(player)
                        buts = Buttons("You can choose investigate someone's role by typing '/ww room=%d see=<id>' with the ids below" % self.id, "You can choose to investigate someone's role")
                        candidates = [x for x in self.alives if x != player]
                        for x in candidates:
                            buts.AddButton(
                                x.name,
                                "/ww room=%d see=%d" % (self.id, x.id),
                                "\n%s\t : %s" % (x.id, x.name)
                            )
                        player.SendButtons(buts)
                    else:
                        print("MISSED DAY ROLE %s" % player.role.name)

            self.Status()
        with self.cond:
            self.SendText("Yall day players have %g seconds to do your stuff" % self.dayDuration)
            self.StartCountdown(time()+self.dayDuration, "Day players have %s left", RoomPhase.day)
            self.cond.wait(self.dayDuration)
        if self.phase == RoomPhase.day:
            with self.lock:
                self.DoKill()
                if self.CheckWin():
                    return True
                self.GetRole()
                self.DoKill()
                if self.CheckWin():
                    return True
                while len(self.deadHunters) > 0:
                    if self.HunterDeathVote() and self.CheckWin():
                        return True
            return self.LynchVote()
        
        
    def LynchVote(self):
        with self.lock:
            self.phase = RoomPhase.lynchVote
            self.waitingCommands = []
            with self.cond:
                self.cond.notifyAll()
            self.votes[Role.villager.id].Set(self.alives, self.alives)
            buts = Buttons("You can vote to lynch someone by typing '/ww room=%d lynch=<id>' with the ids below.  Though you can't be dumb enough to vote for yourself, right?" % self.id, "You can vote to lynch someone. Though you can't be dumb enough to vote for yourself, right?")
            for x in self.alives:
                buts.AddButton(
                    x.name,
                    "/ww room=%d lynch=%d" % (self.id, x.id),
                    "\n%s\t : %s" % (x.id, x.name)
                )
            for x in self.alives:
                x.SendButtons(buts)
            self.Status()
        with self.cond:
            self.SendText("Yall have %g seconds to vote to lynch someone" % self.lynchVoteDuration)
            self.StartCountdown(time()+self.lynchVoteDuration, "Yall have %s left", RoomPhase.lynchVote)
            self.cond.wait(self.lynchVoteDuration)
        if self.phase == RoomPhase.lynchVote:
            with self.lock:
                self.Lynch()
                self.DoKill()
                if self.CheckWin():
                    return True
                self.GetRole()
                self.DoKill()
                if self.CheckWin():
                    return True
                while len(self.deadHunters) > 0:
                    if self.HunterDeathVote() and self.CheckWin():
                        return True
            return self.Night()
        
    def ForceStart(self, starter):
        with self.lock:
            if starter not in self.playersByObj:
                starter.SendText("%s, you haven't joined, thus, have no authority to force start the game" % starter.name)
                return CommandResult.Failed()
            return self.Start(False)
        
    def Start(self, autostart=True):
        with self.lock:
            if self.phase == RoomPhase.idling:
                self.SendText("No Werewolf game session")
                return CommandResult.Failed()
            elif self.phase != RoomPhase.waiting:
                self.SendText("Werewolf game already started")
                return CommandResult.Failed()

            count = len(self.players)
            if count < 5 and autostart:
                self.SendText('Need at least 5 players to start')
                return CommandResult.Failed()
            if count < 1:
                self.SendText("No players. I should've removed the room though. Removing it.")
                self.phase = RoomPhase.idling
                return CommandResult.Failed()
            self.phase = RoomPhase.starting
            with self.cond:
                self.cond.notifyAll()
            self.SendText('Starting werewolf game')

            roles = list(Role.validRoles)
            roles.extend([Role.mason, Role.mason])
            roles.remove(Role.alphaWolf)
            roles.remove(Role.wolfCub)
            if self.noVillager:
                roles.remove(Role.villager)
            else:
                roles.extend([Role.villager, Role.villager, Role.villager, Role.villager, Role.mason])
            shuffle(roles)
            self.alives = list(self.players)
            self.deads = []
            players = list(self.players)
            shuffle(players)
            wwCount = int(count//7)+1
            hasSeer = False
            hasCultist = False
            specialWW = [Role.alphaWolf, Role.wolfCub]
            specialWWLen = 2
            wwTeamNonWWCount = int(count//6)
            mason = 0
            for player in players:
                player.alive = Alive.alive
                role = Role.villager
                arg = 0
                if wwCount > 0:
                    role = Role.werewolf
                    if specialWWLen > 2:
                        a = randint(0, 14)
                        if a < 2:
                            if specialWWLen == 1:
                                role = specialWW[0]
                            else:
                                role = specialWW.pop(randint (0, 1))
                            specialWWLen -= 1
                    wwCount -= 1
                else:
                    rlen = len(roles)
                    if rlen == 0:
                        if self.noVillager:
                            role = Role.mason
                        else:
                            role = choice([Role.mason, Role.villager])
                    else:
                        role = roles[randint(0,rlen-1)]
                        if role.team == Team.werewolf:
                            if wwTeamNonWWCount>1:
                                wwTeamNonWWCount -= 1
                            else:
                                roles = [x for x in roles if x.team != Team.werewolf]
                                rlen = len(roles)
                                if rlen == 0:
                                    if self.noVillager:
                                        role = Role.mason
                                    else:
                                        role = choice([Role.mason, Role.villager])
                                while role.team == Team.werewolf:
                                    role = choice(roles)

                    if mason==1:
                        role=Role.mason

                    if role==Role.mason:
                        mason+=1
                    if role==Role.beholder and not hasSeer:
                        role=Role.seer
                    if role==Role.seer:
                        hasSeer=True
                    if role==Role.cultistHunter and not hasCultist:
                        role=Role.cultist
                    if role==Role.cultist:
                        hasCultist=True

                    if rlen > 0:
                        roles.remove(role)

                player.role = role
                player.originalRole = role
            self.hasCultist = self.hasCultist or hasCultist
            self.day = 0
            self.votes[Role.villager.id] = Vote(self)
            self.votes[Role.werewolf.id] = Vote(self)
            self.room.votes[Role.cultist.id] = Vote(self)
            self.InitRoles()
            self.obj.client.Thread(self.Night)
            return CommandResult.Done()
        
    def CheckWin(self):
        ww = len(self.werewolves)
        nonww = len(self.alives) - ww
        if ww == 0:
            wwteamnonww = len([x for x in self.alives if x.role.team == Team.werewolf and x.role not in Role.werewolves])
            if nonww == 0:
                if wwteamnonww == 0:
                    return self.Win(Team.none)
                else:
                    return self.Win(Team.werewolf)
            elif wwteamnonww > 0:
                return False
            else:
                teams = list(set(x.role.team for x in self.alives))
                if len(teams) == 1:
                    if teams[0] == Team.doppelganger or teams[0] == Team.tanner:
                        return self.Win(Team.none)
                    return self.Win(teams[0])
                hasSK = False
                for team in teams:
                    if team == Team.serialKiller:
                        hasSK = True
                        break
                if hasSK:
                    if nonww < 3:
                        for alive in self.alive:
                            if alive.role != Role.serialKiller:
                                alive.SendText("You're left alone with the Serial Killer. You know what comes next, right?")
                                alive.Die(Role.serialKiller)
                        return self.Win(Team.serialKiller)
                    return False
                if len(self.cultists) == nonww:
                    return self.Win(Team.cultist)
                else:
                    return self.Win(Team.villager)
            return True
        if nonww - ww < 1:
            if ww == 1:
                nonwwteam = [x for x in self.alives if x.role.team != Team.werewolf]
                
                if len(nonwwteam) == 0:
                    return self.Win(Team.werewolf)
                role = nonwwteam[0].role
                if role == Role.hunter:
                    for alive in list(self.alives):
                        alive.SendText("Only a Hunter and a Werewolf is left. Yall engaged in a deadly battle, which brought death to both of you.")
                        if alive.role == Role.hunter:
                            alive.Die(Role.werewolf)
                        else:
                            alive.Die(Role.hunter)
                    self.SendText("The werewolf attacks the Hunter! However, the Hunter doesn't let go of his gun and keep on shooting him. Both eventually dies.")
                    return self.Win(Team.none)
                elif role == Role.serialKiller:
                    cur.execute("UPDATE WerewolfPlayers SET alive=FALSE WHERE roomId=%s AND role!=21 and alive RETURNING lineId", (roomId,))
                    deads = cur.fetchall()
                    conn.commit()
                    cur.execute("SELECT lineId FROM WerewolfPlayers WHERE roomId=%s AND alive", (roomId,))
                    alives = cur.fetchall()
                    for alive in list(self.alives):
                        if alive.role == Role.serialKiller:
                            alive.SendText("ONE STEP TOWARDS WORLD PEACE")
                        else:
                            alive.SendText("THE KILLER KILLER WILL RID THE WORLD OF MURDER")
                            alive.Die(Role.serialKiller)
                            
                    self.SendText("THE KILLER KILLER WILL RID THE WORLD OF MURDER")
                    return self.Win(Team.serialKiller)
                elif role == Role.gunner and nonwwteam[0].ammo and self.realPhase == RoomPhase.day:
                    cur.execute("UPDATE WerewolfPlayers SET alive=FALSE WHERE roomId=%s AND role!=7 and alive RETURNING lineId", (roomId,))
                    deads = cur.fetchall()
                    conn.commit()
                    for alive in list(self.alives):
                        if alive.role == Role.gunner:
                            alive.SendText("You are left alone with someone whom you are very sure to be a Werewolf. You are really lucky that it's daytime and you still have some bullets")
                        else:
                            alive.SendText("You were left alone with the Gunner. It was obvious to him that you were the Werewolf. Lucky for him that he still have some bullets and it was the day.")
                    self.SendText("The Gunner is our hero now.")
                    return self.Win(Team.villager)

            if len([x for x in self.alives if x.role == Role.serialKiller]) > 0:
                return False
            
            for alive in list(self.alives):
                if alive.role not in Role.werewolves:
                    alive.SendText("You're all out of time, and number.")
                    alive.Die(Role.werewolf)

            return self.Win(Team.werewolf)
        return False
        
class Vote(object):
    def __init__(self, room):
        self.canVote = []
        self.haventVoted = []
        self.candidates = []
        self.voters = {}
        self.votees = {}
        self.room = room
        self.lock = Lock()
        
    @property
    def allowRevote(self):
        return self.room.allowRevote
    
    def VoteRandom(self, voter):
        return self.Vote(voter, choice(self.candidates))
        
    def Vote(self, voter, votee, voteCount=1):
        with self.lock:
            if voter not in self.canVote:
                voter.SendText("You have no authority to vote this one")
                return CommandResult.Failed()
            if votee not in self.candidates:
                voter.SendText("You can't vote for %s" % votee.name)
                return CommandResult.Failed()
            elif voter in self.voters:
                if self.voters[voter] == votee:
                    voter.SendText("It's the same guuuyyyyyyyyy")
                    return CommandResult.Failed()
                elif self.allowRevote:
                    self.votees[self.voters[voter]] -= voteCount
                else:
                    voter.SendText("You have already voted for %s" % self.voters[voter].name)
                    return CommandResult.Failed()
            self.voters[voter] = votee
            self.votees[votee] += voteCount
            if voter in self.haventVoted:
                self.haventVoted.remove(voter)
                self.room.RemoveWaitingCommand(voter)
            voter.SendText("You chose %s" % votee.name)
            return CommandResult.Done()
            
    @property
    def everyoneVoted(self):
        return len(self.haventVoted) == 0
        
    def Clear(self):
        with self.lock:
            self.voters.clear()
            self.votees.clear()
            self.haventVoted = []
            self.canVote = []
            self.candidates = []
            
    def Set(self, voters, candidates):
        with self.lock:
            self.Clear()
            self.haventVoted = list(voters)
            self.canVote = list(voters)
            self.candidates = list(candidates)
            for x in self.candidates:
                self.votees[x] = 0
            self.room.ExtendWaitingCommand(voters)
            
    
        

def Werewolf(message, options, continuous=CommandContinuousCallType.notContinuous, images=None, text='', room=0, action='', start=True, night=90, day=90, lynchvote=60, hunter=30, revote=False, villager=False, quick=True, autostart=300, eat=0, kill=0, convert=0, shoot=0, pair=0, see=0, master=0, protect=0, lynch=0, *args, **kwargs):
    if continuous == CommandContinuousCallType.notContinuous:
        if IsEmpty(action):
            action = text
        sender = message.sender
        chatroom = message.chatroom
        client = message.client
        if not client.hasOA or not client.hasUser:
            message.ReplyText("Sorry Werewolf needs both OAClient and UserClient")
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
        if action == 'create':
            if chatroom in roomByObj:
                room = roomByObj[chatroom]
                if room.phase == RoomPhase.waiting:
                    room.SendText("WW already created. To forcestart, type '/ww forcestart'")
                    return CommandResult.Done()
                elif room.phase > RoomPhase.waiting and room.phase < RoomPhase.done:
                    room.SendText("WW is running")
                    return CommandResult.Done()
            room = Room(message.chatroom, message.sender, nightDuration=night, dayDuration=day, lynchVoteDuration=lynchvote, hunterDeathDuration=hunter, allowRevote=revote, noVillager=not villager, autostart=autostart, quick=quick, *args, **kwargs)
            return CommandResult.Done()
        elif room:
            if room not in roomById:
                message.ReplyText("Invalid room id")
                return CommandResult.Failed()
            else:
                return roomById[room].HandleCommand(message=message, action=action, eat=eat, kill=kill, convert=convert, shoot=shoot, pair=pair, see=see, master=master, protect=protect, lynch=lynch, *args, **kwargs)
        else:
            if chatroom not in roomByObj:
                message.ReplyText("No Werewolf game session or you need to provide 'room' argument")
                return CommandResult.Failed()
            room = roomByObj[chatroom]
            if action == 'join':
                room.AddPlayer(sender)
                return CommandResult.Done()
            elif action == 'leave':
                room.Leave(sender)
                return CommandResult.Done()
            elif action == 'forcestart':
                return room.ForceStart(sender)
            elif action == 'status':
                return room.Status()
            else:
                message.ReplyText("Invalid command or you need to provide 'room' argument")
                return CommandResult.Failed()
    else:
        return CommandResult.Failed()
        
    

werewolfCmd = ContinuousHybridCommand(
    'ww',
    Werewolf,
    desc='Awoo',
    images=['the image']
)
