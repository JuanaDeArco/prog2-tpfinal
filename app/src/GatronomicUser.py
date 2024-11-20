from .User import Usuario
from .MenuItem import MenuItem

class UsuarioGastronomico(Usuario):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
        self.menu = []
        self.rating = int
    
    def create_menu_item(self, descrpcion, precio):
        item = MenuItem(descripcion= descrpcion, precio = precio)
        self.menu.append(item)


