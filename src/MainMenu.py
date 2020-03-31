from PyQt5.QtWidgets import QApplication, QWidget
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QRadioButton, QVBoxLayout, QHBoxLayout, QCheckBox, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from src.utils import log_method_name, prepare_cfg, CONFIG_PATH
import os

CURRENT_LEAGUE = 'Delve'
LEAGUES = [CURRENT_LEAGUE, CURRENT_LEAGUE + ' HC', 'SSF ' + CURRENT_LEAGUE, 'SSF ' +
           CURRENT_LEAGUE + ' HC', 'Standard', 'Hardcore', 'SSF Hardcore', 'SSF Standard']


class MenuUI(object):

    def setupUi(self, Widget):
        log_method_name()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
        .QWidget, QWidget {
            background-color: #565352;
        }
        QLineEdit{
            border-style: solid;
            border-width: 2px;
            border-color: #3E3E3E;
            border-radius: 5px;
            background-color: #908C8A;
        }       
        QPushButton{
            border-style: solid;
            border-width: 2px;
            border-color: #3E3E3E;
            border-radius: 5px;
            background-color: #908C8A;
            height: 15%
        }            
        QComboBox{
            border-style: solid;
            border-width: 2px;
            border-color: #3E3E3E;
            border-radius: 5px;
            background-color: #908C8A;
        }
        
        QRadioButton:indicator:checked, QCheckBox:indicator:unchecked {
            image: url(./src/img/checkbox_checked.png);
        }
        
        QRadioButton:indicator:unchecked, QCheckBox:indicator:checked {
            image: url(./src/img/checkbox_unchecked.png);
        }
        
        QComboBox::drop-down 
        {
            border: 1px;
        }
        """)
        layoutV = QVBoxLayout()
        layoutM = QVBoxLayout()
        layoutH = QVBoxLayout()
        layoutH1 = QVBoxLayout()

        # Buttons
        self.btn_exec = QPushButton("Execute")
        self.btn_showhide = QPushButton("Close")

        # Labels/Edit boxes
        self.labelID = QLabel('Account ID')
        self.labelSN = QLabel('Stash Name')
        self.labelLE = QLabel('League')
        self.labelSID = QLabel('Session ID')
        self.editID = QLineEdit('')
        self.editSN = QLineEdit('')
        self.comboLE = QComboBox()
        self.editSID = QLineEdit('')

        # RadioButton ###
        self.layoutR = QHBoxLayout()
        self.radio_normal = QRadioButton('Normal')
        self.radio_quad = QRadioButton('Quad')
        self.layoutR.addWidget(self.radio_normal)
        self.layoutR.addWidget(self.radio_quad)
        self.layoutR.itemAt(0).widget().setChecked(True)

        #CheckBox
        self.layoutMP = QHBoxLayout()
        self.labelMP = QLabel('Multiple queries')
        self.check_multi = QCheckBox()
        self.layoutMP.addWidget(self.check_multi)
        self.layoutMP.setAlignment(Qt.AlignLeft)
        self.layoutMP.addWidget(self.labelMP)

        # Adding all to layout
        layoutH.addWidget(self.labelID)
        layoutH.addWidget(self.editID)
        layoutH.addWidget(self.labelSN)
        layoutH.addWidget(self.editSN)
        layoutH.addWidget(self.labelLE)
        layoutH.addWidget(self.comboLE)
        layoutH.addWidget(self.labelSID)
        layoutH.addWidget(self.editSID)
        layoutM.addWidget(self.check_multi)
        layoutH1.addWidget(self.btn_exec)
        layoutH1.addWidget(self.btn_showhide)

        layoutV.addLayout(layoutH)
        layoutV.addLayout(self.layoutMP)
        layoutV.addLayout(self.layoutR)
        layoutV.addLayout(layoutH1)
        self.setLayout(layoutV)


class MainMenu(QWidget, MenuUI):
    """ Main menu UI main class """
    signal_rects_created = pyqtSignal()
    signal_rects_processing = pyqtSignal()

    def __init__(self, rect_printer, parent=None):
        log_method_name()
        super(MainMenu, self).__init__(parent)

        self.setupUi(self)
        self.account_id = None
        self.stash_name = None
        self.stash_type = None
        self.league = None
        self._set_combo()
        self.session_id = None
        self._load_cfg()
        self.rect_printer = rect_printer
        self.processor = None
        for i in range(self.layoutR.count()):
            self.layoutR.itemAt(i).widget().toggled.connect(self.rb_quad_normal)

        self.btn_exec.clicked.connect(self.execute_clicked)
        self.btn_showhide.clicked.connect(self.show_hide)

        self.setWindowTitle('PoETis')
        self.gui_state = False
        self.threads = []

    def _set_combo(self,):
        log_method_name()
        for i in range(len(LEAGUES)):
            self.comboLE.insertItem(i,LEAGUES[i])

    def rb_quad_normal(self):
        log_method_name()
        if self.radio_normal.isChecked():
            self.stash_type = 'Normal'
        else:
            self.stash_type = 'Quad'

    def execute_clicked(self):
        log_method_name()
        try:
            self.session_id = self.editSID.text()
            self.signal_rects_processing.emit()
            self.hide()
            #processor = DataProcessor(self.editID.text(), self.editSN.text(), self.comboLE.currentText(), self.check_multi.isChecked(), self.session_id)
            #processor.data_computed.connect(self.on_data_ready)
            #self.threads.append(processor)
            #processor.start()
            self._save_cfg()
        except Exception as e:
            print(e)

    def on_data_ready(self, processor):
        log_method_name()
        try:
            self.rect_printer.define_rects(processor.get_items(), self.stash_type)
        except Exception as e:
            print(e)
        self.signal_rects_created.emit()
        pass

    def show_hide(self):
        log_method_name()
        self.hide()

    def _load_cfg(self):
        log_method_name()
        if not os.path.isfile(CONFIG_PATH):
            prepare_cfg(CONFIG_PATH)
        tree = ET.parse(CONFIG_PATH)
        root = tree.getroot()
        self.account_id = root.findall('account_id')[0].text
        self.stash_name = root.findall('stash_name')[0].text
        self.league = root.findall('league')[0].text
        self.session_id = root.findall('session_id')[0].text

        self.editID.setText(self.account_id)
        self.editSN.setText(self.stash_name)
        self.comboLE.setCurrentText(self.league)
        self.editSID.setText(self.session_id)

        if root.findall('stash_type')[0].text == 'Normal':
            self.radio_normal.setChecked(True)
            self.stash_type = "Normal"
        else:
            self.radio_quad.setChecked(True)
            self.stash_type = "Quad"

        if root.findall('multiple_query')[0].text == 'true':
            self.check_multi.setChecked(True)

    def _save_cfg(self):
        log_method_name()
        tree = ET.parse(CONFIG_PATH)
        root = tree.getroot()

        for account_id in root.iter('account_id'):
            new_id = self.editID.text()
            account_id.text = str(new_id)
            account_id.set('updated', 'yes')
        for stash_name in root.iter('stash_name'):
            new_sn = self.editSN.text()
            stash_name.text = str(new_sn)
        root.findall('league')[0].text = self.comboLE.currentText()
        root.findall('session_id')[0].text = self.editSID.text()

        root.findall('stash_type')[0].text = self.stash_type
        if self.check_multi.isChecked():
            root.findall('multiple_query')[0].text = 'true'
        else:
            root.findall('multiple_query')[0].text = 'false'

        tree.write(CONFIG_PATH)

    def keyPressEvent(self, QKeyEvent):
        pass

    def keyReleaseEvent(self, QKeyEvent):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
