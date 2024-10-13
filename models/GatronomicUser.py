import User as User

class GatronomicUser(User):
        def __init__(self):
            super().__init__()
            self.Menu = []
            self.rating = int
