from id import Id
class Usuario:
    def __init__(self, username, password, email) -> None:
        self.id = Id().asignar_id()
        self.username = username
        self.password = password
        self.email = email

