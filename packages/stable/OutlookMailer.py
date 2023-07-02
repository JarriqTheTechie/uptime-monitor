import os

import win32com.client as win32

class OutlookMailer:
    def __init__(self, subject: str, body: str, recipient: list, attachments: list):
        self.recipient: list = recipient
        self.subject: str = subject
        self.body: str = body
        self.attachments = attachments
        self.olApp = win32.Dispatch('Outlook.Application')
        self.olNS = self.olApp.GetNameSpace('MAPI')
        self.mailItem = self.olApp.CreateItem(0)
        self.mailItem.Display()
        self.signature = self.mailItem.HTMLbody
        self.mailItem.Close(1)
        self.mailItem.Display()

    def recipients_to_string(self) -> str:
        recipient_semicolon_delimited: str = ""
        for recipient in self.recipient:
            recipient_semicolon_delimited += recipient + ";"
        return recipient_semicolon_delimited.lstrip().rstrip(";")

    def load_attachments(self):
        for attachment in self.attachments:
            self.mailItem.Attachments.Add(os.path.join(os.getcwd(), f"UPLOADS/{attachment}"))

    def build(self) -> None:
        self.mailItem.Subject = self.subject
        self.mailItem.BodyFormat = 2
        self.mailItem.HTMLBody = self.body + self.signature
        self.mailItem.To = self.recipients_to_string()
        self.mailItem.BCC = "statements@equitybahamas.com"
        self.oRecipients = self.mailItem.ReplyRecipients
        self.oRecipient = self.oRecipients.Add("noreply@equitybahamas.com")
        self.load_attachments()
        self.mailItem.Sensitivity = 3
        # optional (account you want to use to send the email)
        # mailItem._oleobj_.Invoke(*(64209, 0, 8, 0, olNS.Accounts.Item('<email@gmail.com')))
        self.mailItem.Display()
        # mailItem.Save()

    def send(self) -> bool:
        self.build()
        self.mailItem.Send()
        return True



#OutlookMailer("Test", "omg", ['jrolle@equitybahamas.com', 'bottombeatz@gmail.com']).send()