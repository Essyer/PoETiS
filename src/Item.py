import re
from collections import defaultdict
from src.Constants import get_mod_text_template, supported_mods

'''
Class for storing item statistics and processing mod filters.
calculate_mods method takes a dictionary as parameter, example:
filters = {
    'accessory': {
        'x% to fire resistance': 40
    },
    'leather belt': {
        'x% to fire resistance': 50
    },
    'wand': {
        'x% increased projectile speed': 40,
        'x% increased spell damage': 72,
        'x% increased fire spell damage': 100,
        'x% increased critical strike chance for spells': 50
    },
    'weapon': {
        'x to maximum mana': 100
    }
}
Example value in mods_matched for item being wand with stats: 
    - 105 to maximum mana, 
    - 90% increased spell damage
    - 20% increased fire damage
    - 43% increased projectile speed
    - 58% increased critical strike chance for spells

self.mods_matched = {
    'x to maximum mana': 105.0,
    'x% increased spell damage': 90.0,
    'x% increased fire spell damage': 110.0,
    'x% increased projectile speed': 43.0,
    '% increased critical strike chance for spells': 58.0
}

Leather belts would have match for values >= 50% to fire resistance, any other accessory >= 40%
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

    def calculate_mods(self, filters):
        if not filters or not isinstance(filters, dict):
            return
        if not self.base:
            print('Found item with not filled base, name: {}'.format(self.name))
            return  # Not supported item base
        if self.base.lower() not in filters.keys() and self.category1 not in filters.keys()\
                and self.category2 not in filters.keys():
            return
        self.calculate_basic_explicits(filters)

    def calculate_basic_explicits(self, filters):
        for explicit in self.explicits:
            explicit = explicit.replace("'", "").replace("[", "").replace("]", "").replace("+", "").strip()
            mod = get_mod_text_template(explicit)
            mod_regex = supported_mods.get(mod)

            if not mod_regex:
                print("Found unsupported mod: " + mod)
                continue
            else:
                mod_regex = mod_regex[0]

            expected_value, mod_is_total = self.determine_expected_value(filters, mod)
            if not expected_value:
                continue

            mod_value = re.findall(mod_regex, explicit)
            if not mod_value:
                continue
            mod_value = mod_value[0]
            if not mod_value:
                continue

            if isinstance(mod_value, tuple):  # For mods like "Adds X to X fire damage to spells"
                mod_value = sum(tuple(map(int, mod_value))) / float(len(mod_value))

            if 0 < expected_value['base'] <= float(mod_value):
                self.mods_matched[mod] = float(mod_value)

            if mod_is_total:
                for total in expected_value:
                    if total != 'base':
                        self.totals[total] += float(mod_value)
                        if self.totals[total] >= expected_value[total]:
                            self.mods_matched[total] += self.totals[total]

    def determine_expected_value(self, filters, mod):
        expected_mods_cat1 = filters.get(self.category1)
        expected_mods_cat2 = filters.get(self.category2)
        expected_mods_base = filters.get(self.base.lower())
        is_total = False  # Until proven otherwise
        expected_value = {}

        # First check if we are looking for this specific mod
        # Filters are prioritized base > category2 > category1
        if expected_mods_base and expected_mods_base.get(mod):
            expected_value['base'] = expected_mods_base.get(mod)
        elif expected_mods_cat2 and expected_mods_cat2.get(mod):
            expected_value['base'] = expected_mods_cat2.get(mod)
        elif expected_mods_cat1 and expected_mods_cat1.get(mod):
            expected_value['base'] = expected_mods_cat1.get(mod)
        else:
            expected_value['base'] = 0

        # Now check if mod part of any "total" mods we are looking for
        mod_totals = supported_mods.get(mod)
        if not mod_totals:
            expected_value = None  # We are not looking for this mod
        else:
            is_total = True
            mod_totals = mod_totals[1]  # mod_totals is second element of supported_mods, first is regex
            for total in mod_totals:
                if expected_mods_base and expected_mods_base.get(total):
                    expected_value[total] = expected_mods_base.get(total)
                elif expected_mods_cat2 and expected_mods_cat2.get(total):
                    expected_value[total] = expected_mods_cat2.get(total)
                elif expected_mods_cat1 and expected_mods_cat1.get(total):
                    expected_value[total] = expected_mods_cat1.get(total)

        return expected_value, is_total
