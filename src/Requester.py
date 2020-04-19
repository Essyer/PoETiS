import requests
import xml.etree.ElementTree as ET
from src.Constants import item_bases
from src.Item import Item


'''
To use Requester, pass xml mods configuration path in initialization.
Then you can execute run() method and retrieve items information from "items" list.
You can switch configuration file at any time with switch_mod_configuration() method.

'''


class Requester:
    def __init__(self, account_name, stash_name, league, session_id, mods_configuration_file):
        self.stash_name = stash_name
        self.league = league
        self.account_name = account_name
        self.mods_filter = self.load_mods_configuration(mods_configuration_file)
        self._items_data = []
        self.items = []
        self.stashes = {}
        self.session = None
        self.session_id = session_id

    def run(self):
        self.clear()
        if self.session_id and not self.session_id.isspace():
            try:
                self.request_data()
                self.process_items_data()
            except ValueError:
                # Either we could not find stash, got invalid session id or API failed completely (maintenance?)
                raise
            self.calculate_items_mods()

    def clear(self):
        self.items.clear()
        self.stashes.clear()
        self._items_data.clear()

    @staticmethod
    def load_mods_configuration(xml_path):
        filter_dict = {}
        root = ET.parse(xml_path).getroot()
        category1 = root.getchildren()  # weapon, accessory, armour...
        for cat1 in category1:
            mods1 = cat1.find('mods').getchildren()
            if mods1:
                mods1 = [(mod.find('text').text, mod.find('value').text) for mod in mods1]
                filter_dict[cat1.tag] = {mod[0]: float(mod[1]) for mod in mods1}

            category2 = cat1.getchildren()  # bow, claw, helmet, ring...
            for cat2 in category2:
                if cat2.tag == 'mods':
                    continue
                mods2 = cat2.find('mods').getchildren()
                if mods2:
                    mods2 = [(mod.find('text').text, mod.find('value').text) for mod in mods2]
                    filter_dict[cat2.tag] = {mod[0]: float(mod[1]) for mod in mods2}

        return filter_dict

    def switch_mod_configuration(self, xml_path):
        self.mods_filter = self.load_mods_configuration(xml_path)

    def debug_print_matches(self, only_with_matches):
        for item in self.items:
            if len(item.mods_matched) > 0 or not only_with_matches:
                print("{} - {}|{} {} {} {}".format(len(item.mods_matched), item.x, item.y, item.name,
                                                   item.base, list(item.mods_matched)))

    def get_stash_names(self):
        request_string = 'https://www.pathofexile.com/character-window/get-stash-items?league=' + self.league + \
                         '&tabIndex=0&accountName=' + self.account_name + '&tabs=1'

        response_json = self.session.get(request_string).json()
        tabs = response_json['tabs']
        for tab in tabs:
            if tab['type'] == 'QuadStash' or tab['type'] == 'NormalStash' or tab['type'] == 'PremiumStash':
                name = tab['n']
                index = tab['i']
                if name not in self.stashes:
                    self.stashes[name] = index
        return True

    def request_data(self):
        self.session = requests.Session()
        self.session.headers = {'Cookie': 'POESESSID=' + self.session_id}
        try:
            if not self.get_stash_names():
                return False  # API call failed
        except ValueError:
            raise ValueError('no connection')
        if self.stash_name not in self.stashes:
            raise ValueError('stash not found')
        stash_index = str(self.stashes[self.stash_name])
        request_string = 'https://www.pathofexile.com/character-window/get-stash-items?league=' + self.league + \
                         '&tabIndex=' + stash_index + '&tabs=0&accountName=' + self.account_name
        try:
            response_json = self.session.get(request_string).json()
        except ValueError:
            raise ValueError('invalid session id')
        for item in response_json['items']:
            self._items_data.append(item)

    def process_items_data(self):
        for item_data in self._items_data:
            item = Item()
            if 'explicitMods' in item_data and \
                    (item_data['frameType'] == 1  # magic item
                     or item_data['frameType'] == 2):  # rare item
                #  copy item information and mods
                self.copy_info(item_data, item)
                # determine item base and decide if we need it on our list of items
                self.determine_base(item_data, item)
                if item.base:
                    self.items.append(item)

    def calculate_items_mods(self):
        for item in self.items:
            item.calculate_mods(self.mods_filter)
        self.items = sorted(self.items, key=lambda i: len(i.mods_matched), reverse=True)

    @staticmethod
    def copy_info(item_data, item):
        item.x = item_data['x']
        item.y = item_data['y']
        item.height = item_data['h']
        item.width = item_data['w']
        item.ilvl = item_data['ilvl']
        if 'implicitMods' in item_data:
            item.implicits = str(item_data['implicitMods']).split(',')
        item.explicits = str(item_data['explicitMods']).lower().split(',')

    @staticmethod
    def determine_base(item_data, item):
        for category1 in item_bases:
            for category2 in item_bases[category1]:
                for base in item_bases[category1][category2]:
                    if str(item_data['typeLine']).lower() == base.lower():
                        item.category1 = category1.lower()
                        item.category2 = category2.lower()
                        item.base = base
                        item.name = item_data['name']
                        return
