from line2.models.command import ImageCommand, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty
from line2.models.content import Image
from re import compile, DOTALL
from requests import Session

lprx0 = compile("^http://([^/]+)/editor/.*", DOTALL)
lpimgurRx = compile(".*id *= *direct +name *= *direct +value *= *'([^']*)'", DOTALL)


lpColors = ['red', 'green', 'blue']
maxLpColorIndex=len(lpColors)-1
lpTransitions = ['interweave']
maxLpTransitionIndex=len(lpTransitions)-1

lpRandoms = ["sepia",
"mirror",
"mirror-copy",
"flip",
"blur",
"sharpen",
"shade",
"equalize",
"skin-smoother",
"tan",
"normalize",
"contrast",
"cartoon",
"legoz",
"thermal",
"lightning",
"flames",
"water",
"bubbles",
"implode",
"explode",
"lensflare",
"effect-emboss",
"color-sketch",
"effect-paint",
"line-effect",
"negative",
"tilt",
"newsprint",
"dissolve",
"reflection",
"droplet",
"snow",
"old-movie",
"groovy",
"groovy-color",
"sparkles",
"rain",
"blooddrops",
"hearts"]
maxLpRandomIndex = len(lpRandoms)-1

lpActions = ["sepia",
"tint",
"mirror",
"mirror-copy",
"flip",
"blur",
"sharpen",
"shade",
"equalize",
"effect-bw",
"skin-smoother",
"tan",
"normalize",
"contrast",
"lesscontrast",
"restore",
"polaroid",
"polaroid-pile",
"photo-spread",
"color-bars",
"cartoon",
"warhol",
"warhol-four",
"cube",
"photo-booth",
"legoz",
"thermal",
"lightning",
"flames",
"water",
"bubbles",
"effect-line",
"censored",
"implode",
"explode",
"lensflare",
"effect-charcoal",
"effect-emboss",
"sketch",
"color-sketch",
"effect-paint",
"raise",
"scan",
"line-effect",
"colorbook",
"negative",
"tilt",
"newsprint",
"cutout",
"dissolve",
"reflection",
"droplet",
"snow",
"old-movie",
"groovy",
"groovy-color",
"sparkles",
"rain",
"blooddrops",
"hearts",
"spin-blur",
"roll",
"filtering",
"contact-sheet"]

def LunaPic(message, options, text='', images=[]):
    link = images[0].imgurUrl

    splitArgs = text.split(' ')

    if splitArgs[0] == 'random':
        if len(splitArgs) < 1 or isEmpty(splitArgs[1]) or not splitArgs[1].isdigit():
            iterations = 1
        else:
            iterations = int(splitArgs[1])
        if iterations < 1:
            iterations = 1
        if iterations > 20:
            iterations = 20
        #l = list(lpRandoms)
        splitArgs = []
        for i in range(0, iterations):
            #splitArgs.append(l.pop(randint(0, len(l) - 1)))
            splitArgs.append(lpRandoms[randint(0,maxLpRandomIndex)])

    print(str(splitArgs))
    s = Session()
    r0 = s.get("http://lunapic.com/editor/?action=" + splitArgs[0] + "&url=" + link)
    if r0.status_code != 200:
        message.ReplyText("Error LP 1. LunaPic is probably down. Please try again later.")
        return
    lp0m = lprx0.match(r0.url)
    if lp0m is None:
        #print(r0.text)
        message.ReplyText("Error LP 2. LunaPic is probably down. Please try again later.")
        return

    lpurl = 'http://' + lp0m.group(1) + '/editor/'
    
    for arg0 in splitArgs:
        arg1 = arg0.split(':')
        arg = arg1[0]
        if arg not in lpActions:
            continue
        arg2 = None
        if len(arg1) > 1:
            arg2 = arg1[1]
        info = {'action':arg, 'url':link}
        if arg == 'tint' or arg == 'groovy-color':
            if arg2 is None:
                arg2 = lpColors[randint(0, maxLpColorIndex)]
            info['color'] = arg2
        if arg == 'transitions':
            if arg2 is None:
                arg2 = lpTransitions[randint(0, maxLpTransitionIndex)]
            info['type'] = arg2
        if arg == 'scan':
            if arg2 is None:
                arg2 = 1
            info['hoz'] = arg2
        r1 = s.post(lpurl, data=info)
        if r1.status_code != 200:
            message.ReplyText("Error LP 3. LunaPic is probably down\n" + "lpurl='" + lpurl + "'\ninfo='" + str(info) + "'")
            return CommandResult.Failed()
        r2a = s.get(lpurl + "?action=imgur")
        if r2a.status_code != 200:
            message.ReplyText("Error LP 4. LunaPic is probably down\n" + "lpurl='" + lpurl + "'\ninfo='" + str(info) + "'")
            return CommandResult.Failed()
        mLpimgurRx = lpimgurRx.match(r2a.text)
        if mLpimgurRx is None:
            message.ReplyText("Error LP 5. LunaPic is probably down or you submitted invalid action\n" + "lpurl='" + lpurl + "'\ninfo='" + str(info) + "'")
            return CommandResult.Failed()
        link = mLpimgurRx.group(1).replace("http:", "https:")

    img = Image(url=link)
    return CommandResult.Done(images=[img])

lunaPicCmd = ImageCommand(
    'lunapic',
    LunaPic,
    desc='LunaPic',
    images=['the image']
)
