import uuid
from passlib.hash import pbkdf2_sha256

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def register_user(self, email, username, password):
        if self.user_repository.get_by_email(email):
            return False, "El correo ya está registrado"
        user_dict = {
            "_id": uuid.uuid4().hex,
            "email": email,
            "username": username,
            "password": pbkdf2_sha256.hash(password),
            "role": "estudiante"
        }
        self.user_repository.add(user_dict)
        return True, "Usuario registrado correctamente"

    def authenticate(self, email, password):
        user = self.user_repository.get_by_email(email)
        if not user or not pbkdf2_sha256.verify(password, user["password"]):
            return None
        return user