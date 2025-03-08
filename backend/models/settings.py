from pydantic import BaseModel
from typing import List

# Validé
class KeywordSettings(BaseModel):
    text: str
    notificationTimes: List[int]

# Validé
class SMSNotificationSettings(BaseModel):
    agendaFields: List[str]
    phoneNumber: str
    keywords: List[KeywordSettings]