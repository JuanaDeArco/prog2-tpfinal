from .User import Usuario
from .Folder import Folder
class UsuarioPersonal(Usuario):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
        self.folders = {str: Folder}
        self.following = []

        self.agregar_carpetas_base()

    def agregar_carpetas_base(self) -> None:
        self.folders["Por Visitar"] = Folder()
        self.folders["Visitados"] = Folder()
