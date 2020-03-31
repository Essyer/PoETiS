from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QTreeView, QPushButton
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QPoint, Qt
from src.regular_expressions import get_mod_text
import xml.etree.ElementTree as ElementTree
from src.DataProcessor import WEIGHTS_PATH, DataProcessor
from src.utils import log_method_name
import os

COLUMN_1 = 1
COLUMN_0 = 0
NUM_OF_COLUMNS = 2


class ModValueUI(object):

    def __init__(self):
        self.tree = None
        self.root = None
        self.treeView = None
        self.model = None

    def setup_ui(self, Widget):
        log_method_name()
        QWidget.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
        .QWidget, QWidget {
            background-color: #565352;
        }
        QHeaderView::section{
            Background-color:#908C8A;
            border-radius:1;
        }
            
        QScrollBar:vertical {
            Background-color:#908C8A;
        }
        QTreeView{
            background-color:#908C8A;
        }
        QTreeView::item:open {
            background-color: #565352;
        }
        
        QPushButton{
            border-style: solid;
            border-width: 2px;
            border-color: #3E3E3E;
            border-radius: 5px;
            background-color: #908C8A;
            height: 15%;
        }            
            
        """)
        if not os.path.isfile(WEIGHTS_PATH):
            DataProcessor.prepare_weights_xml()
        self.tree = ElementTree.parse(WEIGHTS_PATH)
        self.root = self.tree.getroot()
        self.treeView = QTreeView()
        self.btn_close = QPushButton("Close")
        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self._item_changed)
        self.model.setColumnCount(NUM_OF_COLUMNS)
        self.add_items(self.model, self.root)
        self.treeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Value")])
        layout = QVBoxLayout()
        layout.addWidget(self.treeView)
        layout.addWidget(self.btn_close)
        self.treeView.setColumnWidth(0,300)
        self.treeView.setColumnWidth(1, 20)
        self.setLayout(layout)

    def _item_changed(self, item):
        log_method_name()

        # (signal) update items values in xml if data changed in UI
        # refresh values for items if default mod value changed

        if item.parent():
            mod_name = item.parent().text()
            item_type = item.parent().child(item.row(), COLUMN_0).text()
            multiplier = item.parent().child(item.row(), COLUMN_1).text()

            findstr = './' + mod_name + '/' + item_type

            for mod in self.root.findall(findstr):
                try:
                    float(multiplier)
                except Exception as e:
                    item.setText(mod.text)
                    continue
                mod.text = multiplier
                self.tree.write(WEIGHTS_PATH)
        else:
            it = self.model.item(item.row())
            mod_name = it.text()
            multiplier = item.text()
            value_is_float = True

            findstr = './' + mod_name + '/'
            sh = self.root.find(mod_name)
            prev_value = sh.attrib['default']

            try:
                float(multiplier)
            except Exception as e:
                value_is_float = False
                item.setText(prev_value)

            if value_is_float:

                sh.set('default', multiplier)

                i = 0
                for mod in self.root.findall(findstr):
                    if mod.text == prev_value:

                        mod.text = multiplier
                        self.tree.write(WEIGHTS_PATH)
                        child = it.child(i, COLUMN_1)
                        child.setText(multiplier)
                    i += 1

    def add_items(self, parent, elements):
        log_method_name()
        # add items from xml to UI on app startup

        for mod_name in elements:
            have_child = True if len(list(mod_name)) > 0 else False
            name = None

            if have_child:
                name = QStandardItem(get_mod_text(mod_name.tag))
                name.setEditable(False)
                default = QStandardItem(mod_name.attrib['default'])
                parent.appendRow([name, default])
            else:
                name = QStandardItem(mod_name.tag)
                name.setEditable(False)
                value = QStandardItem(mod_name.text)
                parent.appendRow([name, value])
            if have_child:
                self.add_items(name, mod_name)

    def close_btn(self):
        log_method_name()
        self.show_hide()


class ModValueMain(QWidget, ModValueUI):
    """ Mod values main class """

    def __init__(self, parent=None):
        log_method_name()
        super(ModValueMain, self).__init__(parent)
        self.setup_ui(self)
        self.clicked = False
        self.btn_close.clicked.connect(self.close_btn)
        self.setWindowTitle('PoETis - mod values')
        self.setGeometry(200,200,390,300)
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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = ModValueMain()
    window.show()
    sys.exit(app.exec_())
