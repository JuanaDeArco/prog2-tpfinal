class Usuario:
    def __init__(self, id, username, password, email) -> None:
        self.id = id # y esto tiene que ir aumentando de a uno al crear usuarios
        self.username = username
        self.password = password
        self.email = email
