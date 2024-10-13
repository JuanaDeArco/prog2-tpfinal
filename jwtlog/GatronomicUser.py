from usuario import Usuario

class UsuarioGastronomico(Usuario):
        def __init__(self, username, password, email):
            super().__init__(username, password, email)
            self.Menu = []
            self.rating = int

