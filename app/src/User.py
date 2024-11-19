from .Id import Id
from .Roles import Roles
class Usuario:
    def __init__(self, 
                 user_first_name: str,
                 user_last_name: str,
                 date_of_birth: str,
                 gender: str,
                 user_phone_number: str,
                 user_document_type: str,
                 user_document: str,
                 user_email: str,
                 user_username: str,
                 password: str,
                 user_type: str = "person",
                 is_verified: bool = False,
                  # TODO: Agregar logica para evitar roles conflictivos (persona/resto). Singleton.
                 roles: list = [Roles.PersonRole]) -> None:
        self.id = Id().asignar_id()
        self.user_first_name = user_first_name
        self.user_last_name = user_last_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.user_phone_number = user_phone_number
        self.user_document_type = user_document_type
        self.user_document = user_document
        self.user_email = user_email
        self.user_username = user_username
        self.password_hash = self.hash_password(password)
        self.user_type = user_type
        self.is_verified = is_verified
        self.bio = ""
        self.roles = roles

    def hash_password(self, password: str) -> str:
        # TODO: Implementa un mecanismo seguro para hashear contraseñas, como bcrypt
        return password

    def add_role(self, role):
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role):
        if role in self.roles:
            self.roles.remove(role)

    def __str__(self):
        return f"Usuario {self.user_username}"