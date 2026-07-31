from enum import Enum


class EventType(str, Enum):
    CONVERSATION = "conversation"
    HELP = "help"
    TRADE = "trade"
    QUEST = "quest"
    COMBAT = "combat"
    BETRAYAL = "betrayal"
    DISCOVERY = "discovery"


class Emotion(str, Enum):
    JOY = "joy"
    GRATITUDE = "gratitude"
    TRUST = "trust"
    FEAR = "fear"
    ANGER = "anger"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"


class MemoryState(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    ARCHIVED = "archived"
    
class MemoryCategory(str, Enum):
    PERSONAL_FACT = "personal_fact"
    PREFERENCE = "preference"
    RELATIONSHIP = "relationship"
    GOAL = "goal"
    EVENT = "event"
    SKILL = "skill"
    LOCATION = "location"
    OTHER = "other"