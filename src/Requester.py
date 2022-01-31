import requests
import copy
from collections import OrderedDict
from PyQt5.QtCore import *
from src.ModsContainer import item_bases, ModsContainer, items_categories, one_handed, two_handed
from src.Item import Item
from src.SettingsWidget import SettingsWidget
from src.PainterWidget import PainterWidget

VERSION = "2.0"


# Handles requesting GGG API for stash and items data
class Requester(QThread):
    finished = pyqtSignal()
    failed = pyqtSignal(Exception)
    finished_counting_chaos = pyqtSignal(object)

    def __init__(self, settings_widget: SettingsWidget, painter_widget: PainterWidget):
        super(Requester, self).__init__()
        self._items_data = []
        self.items = []
        self.stashes = {}
        self.session = None
        self.settings_widget = settings_widget
        self.mods_filter = ModsContainer.mods
        self.mode = "chaos_recipe"
        # Instance of SettingsWidget is used to load settings on program initialization and to connect signal.
        # Then new values are sent from SettingsWidget to our _reload_settings()
        self._reload_settings(settings_widget.get_settings_for_requester())
        settings_widget.configuration_changed.connect(self._reload_settings)

        # We need to send new item data to the painter after we finish working on it
        self.painter_widget = painter_widget

        self.chaos_sets = []
        self.allow_identified = False
        self.fill_greedy = True
        self.chaos_sets_goal = 0

    def run(self) -> None:
        self.clear()
        self._reload_settings(self.settings_widget.get_settings_for_requester())
        self.mods_filter = ModsContainer.mods  # Refresh values, they could be modified
        try:
            self.chaos_sets = []
            self.request_data()
            self.process_items_data()
            if self.mode == "rare_scanner":
                self.calculate_items_mods()
                self.painter_widget.items = self.items
                # self.debug_print_matches()
            else:
                self.create_chaos_sets()
                self.painter_widget.chaos_sets = self.chaos_sets
        except Exception as e:
            self.failed.emit(e)
        else:
            self.finished.emit()

    def count_chaos_items(self):
        if self.mode == "chaos_recipe":
            self.clear()
            self._reload_settings(self.settings_widget.get_settings_for_requester())
            try:
                chaos_counters = {"weapon": [0, 0], "helmet": [0, 0], "chest": [0, 0], "gloves": [0, 0],
                                  "boots": [0, 0], "belt": [0, 0], "amulet": [0, 0], "ring": [0, 0]}
                self.request_data()
                self.process_items_data()
                items_regal, items_chaos = self.split_items_to_dicts()
                for category in chaos_counters:
                    if category in items_chaos:
                        chaos_counters[category][0] = len(items_chaos[category])
                    if category in items_regal:
                        chaos_counters[category][1] = len(items_regal[category])
            except Exception as e:
                self.failed.emit(e)
            else:
                self.finished_counting_chaos.emit(chaos_counters)

    def clear(self) -> None:
        self.stashes.clear()
        self.items.clear()
        self._items_data.clear()

    def _validate_data_exists(self) -> None:
        if not self.session_id:
            raise ValueError('Session ID setting is empty')
        if not self.account_name:
            raise ValueError('Account name setting is empty')
        if not self.league:
            raise ValueError('League setting is empty')
        if not self.stash_name:
            raise ValueError('Stash name setting is empty')

    def _reload_settings(self, d: dict) -> None:
        self.account_name = d["account_name"]
        self.session_id = d["session_id"]
        self.stash_name = d["stash_name"]
        self.league = d["league"]
        ModsContainer.load_mods_config(d["mod_file"])
        self.mode = d["mode"]
        self.allow_identified = d["allow_identified"]
        self.fill_greedy = d["fill_greedy"]

    def debug_print_matches(self, num_of_matches=1) -> None:
        print("Item base - Mods - Item name")
        for item in self.items:
            if len(item.mods_matched) >= num_of_matches:
                out_string = item.base + " "
                # Replace all x characters with mod value, at the end strip zeros
                out_string += str([mod.replace('x to x', str(item.mods_matched[mod])).
                                  replace('x ', str(item.mods_matched[mod]) + ' ').
                                  replace('x%', str(item.mods_matched[mod]) + '%')
                                   for mod in list(item.mods_matched)]).replace('.0 ', ' ').replace('.0%', '%')
                out_string += " " + item.name
                print(out_string)

    def get_stash_names(self) -> None:
        request_string = 'https://www.pathofexile.com/character-window/get-stash-items?league=' + self.league + \
                         '&tabIndex=0&accountName=' + self.account_name + '&tabs=1'

        response_json = self.session.get(request_string)
        if response_json.status_code < 200 or response_json.status_code > 299:
            raise ValueError("Stash request failed with code ", response_json.status_code)
        else:
            response_json = response_json.json()

        if 'error' in response_json:
            raise ValueError('No connection or invalid settings')
        tabs = response_json['tabs']
        for tab in tabs:
            if tab['type'] == 'QuadStash' or tab['type'] == 'NormalStash' or tab['type'] == 'PremiumStash':
                name = tab['n']
                index = tab['i']
                if name not in self.stashes:
                    self.stashes[name] = index

    def request_data(self) -> None:
        self._validate_data_exists()
        self.session = requests.Session()
        self.session.headers = {'Cookie': 'POESESSID=' + self.session_id,
                                'User-Agent': 'github.com/Essyer/PoETiS v' + VERSION + ' poetis.tool@gmail.com'}
        self.get_stash_names()
        if self.stash_name not in self.stashes:
            raise ValueError('Stash ' + self.stash_name + ' not found')
        stash_index = str(self.stashes[self.stash_name])
        request_string = 'https://www.pathofexile.com/character-window/get-stash-items?league=' + self.league + \
                         '&tabIndex=' + stash_index + '&tabs=0&accountName=' + self.account_name
        try:
            response_json = self.session.get(request_string).json()
        except ValueError:
            raise ValueError('Invalid session id')
        for item in response_json['items']:
            self._items_data.append(item)

    def process_items_data(self) -> None:
        for item_data in self._items_data:
            item = Item()
            if self.mode == "rare_scanner":
                if 'explicitMods' in item_data and \
                        ((item_data['frameType'] == 1 and self.mode == "rare_scanner")  # magic item
                         or item_data['frameType'] == 2):  # rare item
                    #  copy item information and mods
                    self.copy_info(item_data, item)
                    # determine item base and decide if we need it on our list of items
                    self.determine_categories(item_data, item)
                    if item.base:
                        self.items.append(item)
                    elif 'map' not in item_data['baseType'].lower():
                        print('Found item with not filled base, baseType: {}'.format(item_data['baseType']))
            else:
                if item_data['frameType'] == 2:  # rare item
                    if not item_data['identified'] or self.allow_identified:
                        #  copy item information
                        self.copy_info(item_data, item)
                        # determine item base and decide if we need it on our list of items
                        self.determine_categories(item_data, item)
                        self.items.append(item)

    def calculate_items_mods(self) -> None:
        for item in self.items:
            item.calculate_mods(self.mods_filter)
        self.items = sorted(self.items, key=lambda i: len(i.mods_matched), reverse=True)

    @staticmethod
    def copy_info(item_data: dict, item: Item) -> None:
        item.x = item_data['x']
        item.y = item_data['y']
        item.height = item_data['h']
        item.width = item_data['w']
        item.ilvl = item_data['ilvl']
        if 'implicitMods' in item_data:
            item.implicits = str(item_data['implicitMods']).split(',')
        if 'explicitMods' in item_data:
            item.explicits = str(item_data['explicitMods']).lower().split(',')

    @staticmethod
    def determine_categories(item_data: dict, item: Item) -> None:
        for category1 in item_bases:
            for category2 in item_bases[category1]:
                for base in item_bases[category1][category2]:
                    if base.lower() in str(item_data['typeLine']).lower():
                        item.category1 = category1.lower()
                        item.category2 = category2.lower()
                        item.base = base
                        item.name = item_data['name']
                        return

    # two-handed weapon (including bow) OR 1h + shield OR 2 one-handed OR 2 shields
    # helmet, chest, gloves, boots, belt, amulet, 2x ring

    def split_items_to_dicts(self) -> [dict, dict]:
        items_chaos = {}
        items_regal = {}
        for item in self.items:
            if item.ilvl < 60:
                self.items.remove(item)
                continue
            elif 60 <= item.ilvl <= 74:
                items = items_chaos
            else:
                items = items_regal

            if item.category2 in one_handed or item.category2 in two_handed:
                items.setdefault('weapon', []).append(item)
            elif item.category2 == 'helmet':
                items.setdefault('helmet', []).append(item)
            elif item.category2 == 'chest':
                items.setdefault('chest', []).append(item)
            elif item.category2 == 'gloves':
                items.setdefault('gloves', []).append(item)
            elif item.category2 == 'boots':
                items.setdefault('boots', []).append(item)
            elif item.category2 == 'belt':
                items.setdefault('belt', []).append(item)
            elif item.category2 == 'amulet':
                items.setdefault('amulet', []).append(item)
            elif item.category2 == 'ring':
                items.setdefault('ring', []).append(item)

        items_regal = OrderedDict(sorted(items_regal.items(), key=lambda x: len(x[1])))
        items_chaos = OrderedDict(sorted(items_chaos.items(), key=lambda x: len(x[1])))
        return items_regal, items_chaos

    # Creates sets of items for chaos recipe. At least one item has to be 60 < ilvl < 75, others can be ilvl >= 75
    def create_chaos_sets(self) -> None:
        items_regal, items_chaos = self.split_items_to_dicts()
        set_tmp = {'weapon': [], 'ring': [], 'helmet': [], 'chest': [], 'gloves': [], 'boots': [],
                   'belt': [], 'amulet': []}

        while len(items_chaos.values()) > 0:
            # Fill set with regal items
            regal_tmp = list(items_regal.items())
            for key, values in regal_tmp:
                if not set_tmp[key] and len(items_regal[key]) > 0:
                    set_tmp[key].append(values[0])
                    items_regal[key].remove(values[0])
                    if key == 'ring':
                        if len(items_regal[key]) > 0:
                            set_tmp[key].append(values[0])
                            items_regal[key].remove(values[0])
                    if key == 'weapon' and set_tmp[key][0].category2 in one_handed and items_regal[key]:
                        weapon_tmp_one = next(x for x in iter(items_regal[key]) if x.category2 in one_handed)
                        if weapon_tmp_one:
                            set_tmp[key].append(weapon_tmp_one)
                            items_regal[key].remove(weapon_tmp_one)

            # Fill in with chaos items
            chaos_added = 0
            for key in set_tmp:
                if key in items_chaos:
                    if not set_tmp[key]:
                        if len(items_chaos[key]) > 0:
                            item_tmp = items_chaos[key][-1]
                            set_tmp[key].append(item_tmp)
                            items_chaos[key].pop(-1)
                            chaos_added += 1
                            if item_tmp.category2 == "ring":
                                if len(items_chaos[key]) > 0:
                                    item_tmp = items_chaos[key][-1]
                                    set_tmp[key].append(item_tmp)
                                    items_chaos[key].pop(-1)
                                    chaos_added += 1
                                else:
                                    return
                            elif item_tmp.category2 in one_handed and items_chaos[key]:
                                weapon_tmp_one = next(x for x in iter(items_chaos[key]) if x.category2 in one_handed)
                                if weapon_tmp_one:
                                    set_tmp[key].append(weapon_tmp_one)
                                    items_chaos[key].remove(weapon_tmp_one)
                                    chaos_added += 1
                                else:
                                    return
                        else:
                            return
                    elif key == 'ring' and len(set_tmp[key]) < 2:
                        if len(items_chaos[key]) > 0:
                            set_tmp[key].append(items_chaos[key][-1])
                            items_chaos[key].pop(-1)
                            chaos_added += 1
                        else:
                            return
                    elif key == 'weapon' and len(set_tmp[key]) < 2 \
                            and set_tmp[key][0].category2 in one_handed:
                        if len(items_chaos[key]) > 0:
                            weapon_tmp_one = next(x for x in iter(items_chaos[key]) if x.category2 in one_handed)
                            if weapon_tmp_one:
                                set_tmp[key].append(weapon_tmp_one)
                                items_chaos[key].remove(weapon_tmp_one)
                                chaos_added += 1
                            else:
                                return
                        else:
                            return

            # If all items are from regal recipe replace one of them with chaos recipe item
            if chaos_added == 0:
                most_common_chaos = list(items_chaos.keys())[-1]
                if items_chaos[most_common_chaos]:
                    items_regal[most_common_chaos].append(set_tmp[most_common_chaos][0])
                    set_tmp[most_common_chaos][0] = items_chaos[most_common_chaos][-1]
                    items_chaos[most_common_chaos].pop(-1)
                    chaos_added += 1
                else:
                    return

            if chaos_added > 1 and not self.fill_greedy:
                return

            # Do not add set if there is any item missing
            if any(value == [] for value in set_tmp.values()):
                return

            self.chaos_sets.append(copy.deepcopy(set_tmp))
            set_tmp = {'weapon': [], 'ring': [], 'helmet': [], 'chest': [], 'gloves': [], 'boots': [],
                       'belt': [], 'amulet': []}
