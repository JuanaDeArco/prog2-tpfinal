import User as User
import Folder 

class PersonalUser(User):
    def __init__(self):
        super().__init__()
        self.folders = list[Folder] # type: ignore
        self.following = []

