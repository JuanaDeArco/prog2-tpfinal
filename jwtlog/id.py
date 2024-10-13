class Id:
    _instancia = None
    _counter = 0

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(Id, cls).__new__(cls)
        return cls._instancia

    def asignar_id(self):
        Id._counter += 1
        return Id._counter
