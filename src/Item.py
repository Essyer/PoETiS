class Item:
    def __init__(self):
        self.x = None
        self.y = None
        self.height = None
        self.width = None
        self.ilvl = None
        self.category1 = None  # eg. weapons (constants.py)
        self.category2 = None  # eg. onesword (constants.py)
        self.base = None  # item base name
        self.name = None
        self.score = 0
        self.explicits = []
        self.implicits = []
