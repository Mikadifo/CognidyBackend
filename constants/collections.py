from enum import Enum


class Collection(Enum):
    USERS = "users"
    FLASHCARDS = "flashcards"
    PUZZLES = "puzzles"
    ROADMAP_GOALS = "roadmap_goals"
    THESAURUS = "thesaurus"
    QUIZZES = "quizzes"
    SESSIONS = "sessions"

    @classmethod
    def list(cls):
        return [item.value for item in cls]

