from line2.models.types import Type, EventType, ChatroomType, MessageType, Receiver, ContentType
from line2.utils import IsEmpty
from linebot.models import TemplateSendMessage, CarouselTemplate, MessageTemplateAction, ButtonsTemplate, CarouselColumn

class OAOnlyMessage(object):
    pass
        
class Buttons(OAOnlyMessage):
    def __init__(self, altTextHeader = '', columnText = ''):
        self.buttons = []
        if IsEmpty(columnText):
            self.SetColumnText(altTextHeader)
        else:
            self.SetColumnText(columnText)
        if IsEmpty(altTextHeader):
            self.SetAltTextHeader(columnText)
        else:
            self.SetAltTextHeader(altTextHeader)
            
    def SetColumnText(self,columnText):
        self.columnText = columnText[:120]
            
    def SetAltTextHeader(self,altTextHeader):
        self.altTextHeader = altTextHeader[:400]
            
    def AddButton(self, label, text, altTextEntry = ''):
        self.buttons.append(Button(label, text, altTextEntry))
        
    def AddAltText(self, altText):
        self.altTextHeader = (self.altTextHeader + altText)[:400]
        
    
    def Build(self):
        bLen = len(self.buttons)
        if bLen == 0:
            return ([], None)
        carousels = []
        while bLen > 15:
            carousels.append(
                TemplateSendMessage(
                    alt_text=self.altTextHeader,
                    template=CarouselTemplate(
                        columns=[]
                    )
                )
            )
            car = carousels[-1]
            for k in range(1, 16):
                button = self.buttons.pop(0)
                colLen = len(car.template.columns)
                if colLen == 0:
                    car.template.columns.append(
                        CarouselColumn(
                            text=self.columnText,
                            actions=[]
                        )
                    )
                elif len(car.template.columns[-1].actions) == 3:
                    car.template.columns.append(
                        CarouselColumn(
                            text=self.columnText,
                            actions=[]
                        )
                    )
                car.template.columns[-1].actions.append(
                    MessageTemplateAction(
                        label=button.label,
                        text=button.text
                    )
                )
                car.alt_text = (car.alt_text + button.altTextEntry)[:400]
            bLen = bLen - 15
            
            
        cbLen = 0
        cols = 0
        rows = 0
        if bLen > 4:
            for i in range(1, 5):
                div = bLen//i
                if div > 3:
                    continue
                if cbLen < div*i: 
                    cbLen = div*i
                    cols = i
                    rows = div
                elif cbLen == div*i and div > rows:
                    cbLen = div*i
                    cols=i
                    rows=div
        
        bbLen = bLen-cbLen
        
        if cbLen > 0:
            carousels.append(
                TemplateSendMessage(
                    alt_text=self.altTextHeader,
                    template=CarouselTemplate(
                        columns=[]
                    )
                )
            )
            count = 0
            for button in self.buttons:
                count = count+1
                if count > cbLen:
                    break
                car = carousels[-1]
                colLen = len(car.template.columns)
                if colLen == 0:
                    car.template.columns.append(
                        CarouselColumn(
                            text=self.columnText,
                            actions=[]
                        )
                    )
                elif len(car.template.columns[-1].actions) == rows:
                    if colLen == cols:
                        carousels.append(
                            TemplateSendMessage(
                                alt_text=self.altTextHeader,
                                template=CarouselTemplate(
                                    columns=[]
                                )
                            )
                        )
                        car = carousels[-1]
                    car.template.columns.append(
                        CarouselColumn(
                            text=self.columnText,
                            actions=[]
                        )
                    )
                car.template.columns[-1].actions.append(
                    MessageTemplateAction(
                        label=button.label,
                        text=button.text
                    )
                )
                car.alt_text = (car.alt_text + button.altTextEntry)[:400]

            car = carousels[-1]
            colLen = len(car.template.columns)
            if colLen==0 or (colLen == 1 and len(car.template.columns[-1].actions) == 0):
                carousels.remove(car)
            elif len(car.template.columns[-1].actions) == 0:
                car.template.columns.remove(car.template.columns[-1])
        
        but = None
        if bbLen > 0:
            but = TemplateSendMessage(
                alt_text=self.altTextHeader,
                template=ButtonsTemplate(
                    text=self.columnText,
                    actions=[]
                )
            )
            for val in self.buttons[cbLen:]:
                but.template.actions.append(
                    MessageTemplateAction(
                        label=val.label,
                        text=val.text
                    )
                )
                but.alt_text = (but.alt_text + val.altTextEntry)[:400]
        return [carousels, but]
    
        
    
class Button(object):
    def __init__(self, label, text, altTextEntry = ''):
        self.label=label
        self.text=text
        if IsEmpty(altTextEntry):
            self.altTextEntry = '\n' + label + ":'" + text + "'"
        else:
            self.altTextEntry = altTextEntry

    
    
    