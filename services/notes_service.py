from database import get_users_collection


def update_note_status(user_id, note_id, section, status):
    get_users_collection().find_one_and_update(
        {"_id": user_id, "notes._id": note_id},
        {"$set": { f"notes.$.status.{section}": status }}
    )
