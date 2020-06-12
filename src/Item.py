import re
from collections import defaultdict
from src.ModsContainer import ModsContainer

'''
Class for storing item statistics and processing mod filters.
calculate_mods method takes a dictionary as parameter, example:
filters = {
    'accessory': {
        'belt': {
            'x% to fire resistance': 50 # belts will require at least 50% fire res
        },
        'x% to fire resistance': 40 # all other accessory only 40%
    },        
    'weapon': {
        'wand': {
            'x% increased projectile speed': 40,
            'x% increased spell damage': 72,
            'x% increased fire spell damage': 100,
            'x% increased critical strike chance for spells': 50
        },
        'x to maximum mana': 100
    }
}
Example value in mods_matched for item being wand with stats: 
    - 105 to maximum mana, 
    - 90% increased spell damage
    - 20% increased fire damage
    - 37% increased projectile speed
    - 58% increased critical strike chance for spells

self.mods_matched = {
    'x to maximum mana': 105.0,
    'x% increased spell damage': 90.0,
    'x% increased fire spell damage': 110.0,
    '% increased critical strike chance for spells': 58.0
}

'''


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
        self.totals = defaultdict(float)
        self.mods_matched = defaultdict(float)
        self.unsupported_mods = []

    def calculate_mods(self, filters: dict) -> None:
        if not self.base:
            print('Found item with not filled base, name: {}'.format(self.name))
            return  # Not supported item base
        if self.base.lower() not in filters.keys() and self.category1 not in filters.keys()\
                and self.category2 not in filters.keys():
            return
        self.calculate_basic_explicits(filters)

    def calculate_basic_explicits(self, filters: dict) -> None:
        for explicit in self.explicits:
            explicit = explicit.replace("'", "").replace("[", "").replace("]", "").replace("+", "").strip()
            mod = ModsContainer.get_mod_key(explicit)

            expected_value = self.determine_expected_value(filters, mod)
            if expected_value == 0:
                continue

            mod_value = ModsContainer.get_mod_value(explicit)

            if 0 < expected_value <= float(mod_value):
                self.mods_matched[mod] = float(mod_value)

    def determine_expected_value(self, filters: dict, mod: str) -> float:
        expected_mods_cat1 = filters.get(self.category1)
        expected_mods_cat2 = expected_mods_cat1.get(self.category2)
        expected_value = 0.0

        # Check if we are looking for this specific mod
        # Filters are prioritized category2 > category1
        if expected_mods_cat2 and expected_mods_cat2.get(mod):
            expected_value = expected_mods_cat2.get(mod)
        elif expected_mods_cat1 and expected_mods_cat1.get(mod):
            expected_value = expected_mods_cat1.get(mod)

        return expected_value
