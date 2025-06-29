from flask import current_app

class UserRepository:
    def __init__(self):
        pass  # No necesitas db.session

    def get_by_id(self, user_id):
        return current_app.db.user.find_one({"_id": user_id})

    def get_by_email(self, email):
        return current_app.db.user.find_one({"email": email})

    def add(self, user_dict):
        current_app.db.user.insert_one(user_dict)

    def all(self):
        return list(current_app.db.user.find())