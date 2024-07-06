import threading

from YutaRobot import dispatcher
from YutaRobot.modules.sql import BASE, SESSION
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    UnicodeText,
    UniqueConstraint,
    func,
    JSON
)

class Whispers(BASE):
    __tablename__ = "whispers"
    WhisperId = Column(String, primary_key= True)  # inline_message_id
    whisperData = Column(JSON)

    def __init__(self, WhisperId, whisperData):
        self.WhisperId = WhisperId
        self.whisperData = whisperData

    def __repr__(self):
        return "<Whispers {} ({})>".format(self.WhisperId, self.whisperData)


Whispers.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()

def add_whisper(WhisperId, WhisperData):
    with INSERTION_LOCK:
        whisper = Whispers(WhisperId, WhisperData)
        SESSION.add(whisper)
        SESSION.commit()


def del_whisper(WhisperId):
    with INSERTION_LOCK:
        whisper = SESSION.query(Whispers).filter_by(WhisperId=WhisperId).first()
        SESSION.delete(whisper)
        SESSION.commit()

def get_whisper(WhisperId):
    try:
        whisper = SESSION.query(Whispers).filter_by(WhisperId=WhisperId).first()
        return whisper.whisperData
    finally:
        SESSION.close()
