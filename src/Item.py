import re
from src.Constants import get_mod_text_from_value
'''
Class for storing item statistics and processing mod filters.
calculate_mods method takes a dictionary as parameter, example:
filters = {
            'weapon': {
                supported_mods['increased cold damage']: 60
            }
            'wand': {
                supported_mods['increased cast speed']: 10,
                supported_mods['fire damage to spells']: 48
                supported_mods['increased critical strike chance for spells']: 60
            }
        }
Example value in mods_matched for Item being wand with stats: 
    - 68% increased cold damage, 
    - added 35-62 fire damage to spells
    - 14% increased global accuracy rating
    - 18% increased cast speed
    - 58 % increased critical strike chance for spells

self.mods_matched = {
    'X% increased cold damage': 68.0,
    'X to X fire damage to spells': 48.5,
    'X% increased cast speed': 18.0
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
        self.mods_matched = {}

    def calculate_mods(self, filters):
        if not filters or not isinstance(filters, dict):  # We need at least one mod filter
            return False
        for mod in self.explicits:
            for filter_category in filters:  # 'weapon', 'armour', 'coral ring', 'vaal mask' etc.
                if filter_category != self.category1 and filter_category != self.category2:
                    # We want to run regular expressions only if the item category or base is on our search list
                    continue

                for mod_filter in filters[filter_category]:
                    mod_value = re.findall(mod_filter, mod)
                    if not mod_value:
                        continue
                    mod_value = mod_value[0]  # Initially it is a list returned from regex
                    if isinstance(mod_value, tuple):  # For mods like "Adds X to X fire damage to spells"
                        mod_value = sum(tuple(map(int, mod_value))) / float(len(mod_value))
                    if float(mod_value) >= filters[filter_category][mod_filter]:
                        self.mods_matched[get_mod_text_from_value(mod_filter)] = float(mod_value)

