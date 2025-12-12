from database.database import db
from datetime import datetime

def save_visit(owner_email, visitor_email, token):
    db.users.update_one(
        {"email": owner_email},
        {"$push": {
            "visits": {
                "visitor_email": visitor_email,
                "oauth_token": token,
                "timestamp": datetime.now()
            }
        }},
        upsert=True
    )
