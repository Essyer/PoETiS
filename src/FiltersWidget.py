from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import xml.etree.ElementTree as ElementTree
from src.DragWidget import DragWidget
from src.utils import load_styles, xml_indent, log_method_name
from src.ModsContainer import ModsContainer, DEFAULT_FILTER_PATH
from src.SettingsWidget import SettingsWidget

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
DEFAULT_MOD_TEXT = "Add your new mod here..."


# Allows to get mod text before modification is done
class ItemDelegate(QItemDelegate):
    def createEditor(self, parent: QWidget, option: "QStyleOptionViewItem", index: QModelIndex) -> QWidget:
        if index.data():
            FiltersWidget.mod_text_before_change = index.data()

        return QItemDelegate.createEditor(self, parent, option, index)


# Allows to load and modify XML mods values
class FiltersWidget(DragWidget):
    # Not going to use more than one instance so it is safe, need to somehow store mod text before it is modified
    mod_text_before_change = ""

    def __init__(self, settings_widget: SettingsWidget):
        super(FiltersWidget, self).__init__(None, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        log_method_name()
        load_styles(self)
        self.xml_root = None

        # Setup layout
        self.treeView = QTreeView()
        layout = QVBoxLayout()
        layout.addWidget(self.treeView)
        btn_hide = QPushButton("Close")
        btn_hide.clicked.connect(self.hide)
        layout.addWidget(btn_hide)
        self.setLayout(layout)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._init_tree()

        # this isn't requester, but same data works
        self._reload_settings(settings_widget.get_settings_for_requester())
        settings_widget.configuration_changed.connect(self._reload_settings)

    def _init_tree(self) -> None:
        # full reinit every time we switch mod lists for now
        self.model = QStandardItemModel()
        self.treeView.setModel(self.model)
        self.treeView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.treeView.setHeaderHidden(True)

        # Set delegate to grab mod value before it is changed, need it to modify xml and dictionary values
        self.treeView.setItemDelegate(ItemDelegate())
        self.model.itemChanged.connect(self.process_item_changed)

    def _reload_settings(self, d: dict) -> None:
        self._init_tree()
        self.xml_path = d["mod_file"]
        # this is double work right now - consider singleton instance for modcontainer
        ModsContainer.load_mods_config(d["mod_file"])
        self.xml_root = None
        self.load_mods(self.xml_path)

    def load_mods(self, xml_path: str) -> None:
        log_method_name()
        self.xml_root = ElementTree.parse(xml_path).getroot()
        root = self.model.invisibleRootItem()
        category1 = list(self.xml_root)  # weapon, accessory, armour...
        for cat1 in category1:
            cat1_item = QStandardItem(cat1.tag)
            cat1_item.setEditable(False)
            root.appendRow(cat1_item)

            category2 = list(cat1)  # bow, claw, helmet, ring...
            for cat2 in category2:
                if cat2.tag == "mod":
                    continue
                cat2_item = QStandardItem(cat2.tag)
                cat2_item.setEditable(False)
                cat1_item.appendRow(cat2_item)
                mods2 = list(cat2)
                if mods2:
                    for mod in mods2:
                        cat2_item.appendRow(QStandardItem(mod.text))
                cat2_item.appendRow(QStandardItem(DEFAULT_MOD_TEXT))

            # Mods of category1 are added after subcategories because adding new mod or modifying existing one
            # makes it to go to the end of elements list
            mods1 = cat1.findall("mod")
            if mods1:
                for mod in mods1:
                    cat1_item.appendRow(QStandardItem(mod.text))
            cat1_item.appendRow(QStandardItem(DEFAULT_MOD_TEXT))

    def process_item_changed(self, item1: QStandardItem) -> None:
        log_method_name()
        parent = item1.parent()
        parents = []
        while parent:
            parents.append(parent.text())
            parent = parent.parent()

        if item1.text() == "":  # Deleting mod
            if FiltersWidget.mod_text_before_change == DEFAULT_MOD_TEXT:
                # Minor bug (not affecting XML file): If someone adds some characters after default mod text and then
                # removes them, there will be additional entry in mod list with default mod text, resets after program
                # reboot.
                item1.setText(DEFAULT_MOD_TEXT)
            else:
                self.delete_mod_xml(parents[::-1], FiltersWidget.mod_text_before_change)
                self.model.removeRow(item1.index().row(), item1.index().parent())
        elif any(c.isdigit() for c in item1.text()):
            if (FiltersWidget.mod_text_before_change == DEFAULT_MOD_TEXT  # Adding mod
                    or not any(c.isdigit() for c in FiltersWidget.mod_text_before_change)):
                self.add_mod_xml(parents[::-1], item1.text())
                item1.parent().appendRow(QStandardItem(DEFAULT_MOD_TEXT))
            else:  # Modifying mod
                self.delete_mod_xml(parents[::-1], FiltersWidget.mod_text_before_change)
                self.add_mod_xml(parents[::-1], item1.text())

    def add_mod_xml(self, parents: list, mod: str) -> None:
        log_method_name()
        if mod == DEFAULT_MOD_TEXT:
            return

        # Add entry to currently used dictionary
        parent_dict = ModsContainer.mods
        for p in parents:
            if p not in parent_dict:
                parent_dict[p] = {}
            parent_dict = parent_dict[p]
        parent_dict[ModsContainer.get_mod_key(mod)] = ModsContainer.get_mod_value(mod)

        # Save entry in mod filter file
        parent_xml = self.xml_root
        for parent in parents:
            node = parent_xml.find(parent)
            if node is not None:
                parent_xml = node
        if parent_xml != self.xml_root:
            element = ElementTree.Element("mod")
            element.text = mod
            parent_xml.append(element)
            xml_indent(self.xml_root)
            tree = ElementTree.ElementTree(self.xml_root)
            tree.write(self.xml_path)

    def delete_mod_xml(self, parents: list, mod: str) -> None:
        log_method_name()
        parent_xml = self.xml_root
        # Remove entry from currently used dictionary
        parent_dict = ModsContainer.mods
        for p in parents:
            parent_dict = parent_dict[p]
        del parent_dict[ModsContainer.get_mod_key(mod)]

        for parent in parents:
            node = parent_xml.find(parent)
            if node:
                parent_xml = node
        if parent_xml != self.xml_root:
            elements = parent_xml.findall("mod")
            for element in elements:
                if element.text == mod:
                    parent_xml.remove(element)
                    xml_indent(self.xml_root)
                    tree = ElementTree.ElementTree(self.xml_root)
                    tree.write(self.xml_path)
