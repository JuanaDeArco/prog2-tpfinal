from review import Review

class MenuItem:
    def __init__(self, descripcion, precio):
        self.descripcion = descripcion
        self.precio = precio
        self.avg_rating = 0
        self.reviews = []