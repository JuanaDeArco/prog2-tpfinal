from usuario import Usuario

class UsuarioPersonal(Usuario):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
        self.folders = []
        self.following = []

