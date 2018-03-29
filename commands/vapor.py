# -*- coding: utf-8 -*-
from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random, randint
from line2.utils import IsEmpty, AddReverseDict

vaporDict = {
    'a' : 'ａ',
    'b' : 'ｂ',
    'c' : 'ｃ',
    'd' : 'ｄ',
    'e' : 'ｅ',
    'f' : 'ｆ',
    'g' : 'ｇ',
    'h' : 'ｈ',
    'i' : 'ｉ',
    'j' : 'ｊ',
    'k' : 'ｋ',
    'l' : 'ｌ',
    'm' : 'ｍ',
    'n' : 'ｎ',
    'o' : 'ｏ',
    'p' : 'ｐ',
    'q' : 'ｑ',
    'r' : 'ｒ',
    's' : 'ｓ',
    't' : 'ｔ',
    'u' : 'ｕ',
    'v' : 'ｖ',
    'w' : 'ｗ',
    'x' : 'ｘ',
    'y' : 'ｙ',
    'z' : 'ｚ',
    'A' : 'Ａ',
    'B' : 'Ｂ',
    'C' : 'Ｃ',
    'D' : 'Ｄ',
    'E' : 'Ｅ',
    'F' : 'Ｆ',
    'G' : 'Ｇ',
    'H' : 'Ｈ',
    'I' : 'Ｉ',
    'J' : 'Ｊ',
    'K' : 'Ｋ',
    'L' : 'Ｌ',
    'M' : 'Ｍ',
    'N' : 'Ｎ',
    'O' : 'Ｏ',
    'P' : 'Ｐ',
    'Q' : 'Ｑ',
    'R' : 'Ｒ',
    'S' : 'Ｓ',
    'T' : 'Ｔ',
    'U' : 'Ｕ',
    'V' : 'Ｖ',
    'W' : 'Ｗ',
    'X' : 'Ｘ',
    'Y' : 'Ｙ',
    'Z' : 'Ｚ',
    #' ' : ' ',
    "'" : '＇',
    '-' : '－',
    '@' : '＠',
    '*' : '＊',
    '+' : '＋',
    '<' : '＜',
    '>' : '＞',
    '=' : '＝',
    ':' : '：',
    '#' : '＃',
    '(' : '（',
    ')' : '）',
    '&' : '＆',
    '[' : '［',
    ']' : '］',
    '$' : '＄',
    '?' : '？',
    '"' : '＂',
    '\%' : '％',
    '/' : '／',
    ';' : '；',
    '\\' : '＼',
    '^' : '＾',
    '_' : '＿',
    '`' : '｀',
    '|' : '｜',
    '{' : '｛',
    '}' : '｝',
    '~' : '～'
}
vaporDictReverse = {v:k for k, v in vaporDict.iteritems()}

def Vapor(message, options, text=''):
    if IsEmpty(text):
        message.ReplyText("Please specify 'text' argument.")
        return

    l = []
    
    for c in text:
        if c in vaporDict:
            l.append(vaporDict[c])
        else:
            l.append(c + ' ')
            
    ret = ''.join(l)
    
    return CommandResult(type=CommandResultType.done, texts=[ret])

vaporCmd = Command(
    'vapor',
    Vapor,
    desc='V a p o r'
)
AddReverseDict(vaporDictReverse)
