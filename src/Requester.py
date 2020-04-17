import requests
from src.Constants import item_bases
from src.Item import Item


'''
To use Requester, after creating object add some values from item_bases to one of filter lists: 
"requested_category1" (accessory, armour...) , "requested_category2" (amulet,belt...) 
or "requested_base" (Coral Amulet...)
Only items that are specified in those lists will be added to list "items".
Then you can execute run() method and retrieve items information from "items" list.
'''


class Requester:
    def __init__(self, account_name, stash_name, league, session_id):
        self.stash_name = stash_name
        self.league = league
        self.account_name = account_name
        self.filters = []
        self._items_data = []
        self.items = []
        self.stashes = {}
        self.session = None
        self.session_id = session_id

    def run(self):
        if self.session_id and not self.session_id.isspace():
            try:
                self.request_data()
                self.process_items_data()
            except ValueError:
                # Either we could not find stash, got invalid session id or API failed completely (maintenance?)
                raise

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
