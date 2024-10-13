import User

class PersonalUser(User):
    def __init__(self):
        super().__init__()
        self.folders = None
        self.following = []

