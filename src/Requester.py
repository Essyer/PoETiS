import requests
from PyQt5.QtCore import *
from src.ModsContainer import item_bases, ModsContainer
from src.Item import Item
from src.SettingsWidget import SettingsWidget
from src.PainterWidget import PainterWidget


# Handles requesting GGG API for stash and items data
class Requester(QObject):
    finished = pyqtSignal()
    failed = pyqtSignal(Exception)

    def __init__(self, settings_widget: SettingsWidget, painter_widget: PainterWidget):
        super(Requester, self).__init__()
        self._items_data = []
        self.items = []
        self.stashes = {}
        self.session = None
        self.mods_filter = ModsContainer.mods
        # Instance of SettingsWidget is used to load settings on program initialization and to connect signal.
        # Then new values are sent from SettingsWidget to our _reload_settings()
        self._reload_settings(settings_widget.get_settings_for_requester())
        settings_widget.configuration_changed.connect(self._reload_settings)

        # We need to send new item data to the painter after we finish working on it
        self.painter_widget = painter_widget

    def run(self) -> None:
        self.clear()
        self.mods_filter = ModsContainer.mods  # Refresh values, they could be modified
        try:
            self.request_data()
            self.process_items_data()
            self.calculate_items_mods()
            self.painter_widget.items = self.items
            # self.debug_print_matches()
        except Exception as e:
            self.failed.emit(e)
        else:
            self.finished.emit()

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

        response_json = self.session.get(request_string).json()
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
        self.session.headers = {'Cookie': 'POESESSID=' + self.session_id}
        self.get_stash_names()
        if self.stash_name not in self.stashes:
            raise ValueError('Stash not found')
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
            if 'explicitMods' in item_data and \
                    (item_data['frameType'] == 1  # magic item
                     or item_data['frameType'] == 2):  # rare item
                #  copy item information and mods
                self.copy_info(item_data, item)
                # determine item base and decide if we need it on our list of items
                self.determine_categories(item_data, item)
                if item.base:
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
        item.explicits = str(item_data['explicitMods']).lower().split(',')

    #  GGG API returns only item base, we need to find out what category of item it is, e.g. cat1 = weapon, cat2 = wand
    #  Hopefully we will get this functionality soon so I can remove this method and item_bases:
    #  https://www.pathofexile.com/forum/view-thread/2784742/page/1#p22948552
    @staticmethod
    def determine_categories(item_data: dict, item: Item) -> None:
        for category1 in item_bases:
            for category2 in item_bases[category1]:
                for base in item_bases[category1][category2]:
                    if str(item_data['typeLine']).lower() == base.lower():
                        item.category1 = category1.lower()
                        item.category2 = category2.lower()
                        item.base = base
                        item.name = item_data['name']
                        return
