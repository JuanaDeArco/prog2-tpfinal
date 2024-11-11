from src.Folder import Folder
from src.MenuItem import MenuItem

class Rol:
    def __init__(self,name) -> None:
        self.name = name


class PersonRole(Rol):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
        self.folders = {str: Folder}
        self.following = []

        self.agregar_carpetas_base()

    def agregar_carpetas_base(self) -> None:
        self.folders["Por Visitar"] = Folder()
        self.folders["Visitados"] = Folder()

class GastroRole(Rol):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
        self.menu = []
        self.rating = int
    
    def create_menu_item(self, descrpcion, precio):
        item = MenuItem(descripcion= descrpcion, precio = precio)
        self.menu.append(item)

