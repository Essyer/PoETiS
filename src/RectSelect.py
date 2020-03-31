from PyQt5.QtWidgets import QApplication, QWidget
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout,QCheckBox
from PyQt5.QtCore import QRect, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QColor
from src.RectProcess import RECT_COLOR
from src.utils import log_method_name, CONFIG_PATH, prepare_cfg
import os

FIXED_SIZE = [250, 100]


class RectSelect(QWidget):
    """ Main menu UI main class """
    signal_rects_selected = pyqtSignal(list)

    def __init__(self, parent=None):
        log_method_name()
        super(RectSelect, self).__init__(parent)
        self.setupUi()
        self._load_cfg()
        self.btn_acc.clicked.connect(self.save_btn)

    def setupUi(self):
        log_method_name()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(FIXED_SIZE[0], FIXED_SIZE[1])
        self.setStyleSheet("""
        .QWidget, QWidget {
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
        layoutV = QVBoxLayout()
        self.layoutMP = QHBoxLayout()
        self.layoutA = QHBoxLayout()

        self.check_1 = QCheckBox()
        self.check_2 = QCheckBox()
        self.check_3 = QCheckBox()
        self.check_4 = QCheckBox()
        self.check_5 = QCheckBox()
        self.btn_acc = QPushButton("Save/Close")
        self.layoutMP.addWidget(self.check_1)
        self.layoutMP.addWidget(self.check_2)
        self.layoutMP.addWidget(self.check_3)
        self.layoutMP.addWidget(self.check_4)
        self.layoutMP.addWidget(self.check_5)
        self.layoutA.addWidget(self.btn_acc)
        self.layoutMP.setAlignment(Qt.AlignCenter)
        self.layoutMP.setSpacing(FIXED_SIZE[0]/10)
        layoutV.addLayout(self.layoutMP)
        layoutV.addLayout(self.layoutA)
        self.setLayout(layoutV)

    def paintEvent(self, r):

        self.qp = QPainter()
        self.qp.begin(self)
        self.draw_colors()
        self.qp.end()

    def draw_colors(self):
        log_method_name()
        self.qp.setRenderHint(QPainter.Antialiasing)
        shift = 0.10
        for key, value in RECT_COLOR.items():
            color = QColor()
            color.setRed(value[0])
            color.setGreen(value[1])
            color.setBlue(value[2])
            self.qp.setBrush(color)  # color inside
            self.qp.drawRect(QRect(FIXED_SIZE[0]*shift, FIXED_SIZE[0]/15, 40, 40))
            shift += 0.16


    def save_btn(self):
        log_method_name()
        checkbox_status =[]
        checkbox_status.append(self.check_1.isChecked())
        checkbox_status.append(self.check_2.isChecked())
        checkbox_status.append(self.check_3.isChecked())
        checkbox_status.append(self.check_4.isChecked())
        checkbox_status.append(self.check_5.isChecked())

        self.signal_rects_selected.emit(checkbox_status)
        self._save_cfg()
        self.hide()

    def _save_cfg(self):
        log_method_name()
        tree = ET.parse(CONFIG_PATH)
        root = tree.getroot()

        root.findall('t1_color')[0].text = 'true' if self.check_1.isChecked() else 'false'
        root.findall('t2_color')[0].text = 'true' if self.check_2.isChecked() else 'false'
        root.findall('t3_color')[0].text = 'true' if self.check_3.isChecked() else 'false'
        root.findall('t4_color')[0].text = 'true' if self.check_4.isChecked() else 'false'
        root.findall('t5_color')[0].text = 'true' if self.check_5.isChecked() else 'false'

        tree.write( CONFIG_PATH)

    def _load_cfg(self):
        log_method_name()
        if not os.path.isfile(CONFIG_PATH):
            prepare_cfg(CONFIG_PATH)

        tree = ET.parse(CONFIG_PATH)
        root = tree.getroot()

        self.check_1.setChecked(True) if root.findall('t1_color')[0].text == 'true' else self.check_1.setChecked(False)
        self.check_2.setChecked(True) if root.findall('t2_color')[0].text == 'true' else self.check_2.setChecked(False)
        self.check_3.setChecked(True) if root.findall('t3_color')[0].text == 'true' else self.check_3.setChecked(False)
        self.check_4.setChecked(True) if root.findall('t4_color')[0].text == 'true' else self.check_4.setChecked(False)
        self.check_5.setChecked(True) if root.findall('t5_color')[0].text == 'true' else self.check_5.setChecked(False)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = RectSelect()
    window.show()
    sys.exit(app.exec_())
