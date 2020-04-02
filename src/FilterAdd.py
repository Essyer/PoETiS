from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QTreeView, QPushButton, QLabel, QLineEdit
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QCompleter, QComboBox
import xml.etree.ElementTree as ElementTree
from src.utils import log_method_name, load_styles
from src.Constants import FILTERS_PATH, item_bases

NUM_OF_COLUMNS = 3


class FilterAddUI(object):

    def __init__(self):
        self.tree = None
        self.root = None
        self.treeView = None
        self.model = None

    def setup_ui(self, Widget):
        log_method_name()
        QWidget.__init__(self)
        self.setWindowFlags( Qt.WindowStaysOnTopHint)
        load_styles(self)
        string_list = item_bases

        self.comboItem = ExtendedComboBox()
        self.comboBase = ExtendedComboBox()

        self.comboItem.addItems(string_list)
        self.comboBase.addItems(string_list)
        self.tree = ElementTree.parse(FILTERS_PATH)
        self.root = self.tree.getroot()
        self.treeView = QTreeView()
        self.labelItem = QLabel('Item')
        self.editItem = QLineEdit('')
        self.labelBase = QLabel('Item Base')
        self.editBase = QLineEdit('')
        self.btn_close = QPushButton("Close")
        self.btn_add = QPushButton("Add")
        self.btn_remove = QPushButton("Remove")
        self.labelModList = QLabel('Mod list')
        self.model = QStandardItemModel()
        #self.model.itemChanged.connect(self._item_changed)
        self.model.setColumnCount(NUM_OF_COLUMNS)
        self.add_filters(self.model, self.root)
        self.treeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Value")])
        layoutItem = QVBoxLayout()
        layoutItem.addWidget(self.labelItem)
        layoutItem.addWidget(self.comboItem)
        #layoutItem.addWidget(self.editItem)
        layoutBase = QVBoxLayout()
        layoutBase.addWidget(self.labelBase)
        layoutBase.addWidget(self.comboBase)
        layoutItemBase = QHBoxLayout()
        layoutModList = QVBoxLayout()
        layoutMain = QVBoxLayout()
        layoutItemInfo = QHBoxLayout()
        layoutModList.addWidget(self.labelModList)
        layoutModList.addWidget(self.treeView)
        layoutModList.addWidget(self.btn_close)
        layoutItemInfo.addWidget(self.btn_add)
        layoutItemInfo.addWidget(self.btn_remove)
        layoutItemBase.addLayout(layoutItem)
        layoutItemBase.addLayout(layoutBase)
        layoutMain.addLayout(layoutItemBase)
        layoutMain.addLayout(layoutModList)
        layoutMain.addLayout(layoutItemInfo)

        self.treeView.setColumnWidth(0, 250)
        self.treeView.setColumnWidth(1, 50)
        self.setLayout(layoutMain)

    def add_filters(self, parent, filters):
        pass

    def close_btn(self):
        log_method_name()
        self.show_hide()


class FilterAdd(QWidget, FilterAddUI):
    """ Mod values main class """

    def __init__(self, parent=None):
        log_method_name()
        super(FilterAdd, self).__init__(parent)
        self.setup_ui(self)
        self.clicked = False
        self.btn_close.clicked.connect(self.close_btn)
        self.setWindowTitle('PoETis - mod values')
        self.setGeometry(200, 200, 390, 300)
        self.gui_state = False

    def show_hide(self):
        self.hide()

    def keyPressEvent(self, qkeyevent):
        pass

    def keyReleaseEvent(self, qkeyevent):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass


class ExtendedComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))

    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = FilterAdd()
    window.show()
    sys.exit(app.exec_())
