from database import get_sessions_collection


def get_next_session_number(user_id, section):
    return get_sessions_collection().count_documents({"user_id": str(user_id), "section": section}) + 1
