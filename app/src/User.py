from src.Id import Id
import src.Roles as Roles


class Usuario:
        def __init__(self, username, password, email, role=[Roles.PersonRole]) -> None:
            self.id = Id().asignar_id()
            self.username = username
            self.password = password
            self.email = email
            # TODO: Agregar logica para evitar roles conflictivos (persona/resto). Singleton.
            self.roles = role
        
        # def __str__(self):
        #       return self.username
        
        def add_role(self, role):
             self.roles.append(role)
        
        def remove_role(self, role):
             self.roles.remove(role)
