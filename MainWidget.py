from __future__ import unicode_literals
from src.MainMenu import MainMenu
from src.RectSelect import RectSelect
#from src.ModValueMain import ModValueMain
from PyQt5.QtWidgets import QApplication, QWidget
import xml.etree.ElementTree as ET
from src.RectProcess import RectProcess
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QSizePolicy,QGridLayout
from PyQt5.QtGui import QPainter, QPen, QIcon, QPixmap
from PyQt5.QtCore import Qt, QRect
from win32api import GetSystemMetrics
from src.utils import initialize_logging, log_method_name, CONFIG_PATH

window_width = GetSystemMetrics(0)
window_height = GetSystemMetrics(1)
width_multi = 0.88542
height_multi = 0.83334
width_width_scale = window_width/1920
window_height_scale = window_height/1080


class MainWidget(QWidget):
    """ Rectangle printing class """

    def __init__(self, parent=None):
        log_method_name()
        super(MainWidget, self).__init__(parent)
        self.rect_processor = RectProcess(width_width_scale, window_height_scale)
        self.rect_select = RectSelect()
        #self.mod_list = ModValueMain()
        self.main_menu = MainMenu(self.rect_processor)
        self.image_path = "src/img/"
        self.setup_ui(self)
        self.setMouseTracking(1)
        self.btn_menu.clicked.connect(self.open_menu)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_net.clicked.connect(self.show_net)
        self.btn_mods.clicked.connect(self.show_mods)
        self.btn_hide.clicked.connect(self.hide_buttons)
        self.btn_show.clicked.connect(self.show_buttons)

        self.rect_select.signal_rects_selected.connect(self.signal_rects_selected)
        self.main_menu.signal_rects_created.connect(self.signal_show_net)
        self.main_menu.signal_rects_processing.connect(self.signal_nets_processing)
        self.qp = None
        self.gui_state = None
        self.rects_state = None
        self.rectangles_ready = None
        self.net_clickable = None
        self.selected_rects = []
        self.load_rects_selected()

    def closeEvent(self, event):
        log_method_name()
        event.accept()

    def hide_buttons(self):
        log_method_name()

        self.btn_show.show()
        self.btn_net.hide()
        self.btn_menu.hide()
        self.btn_settings.hide()
        self.btn_mods.hide()
        self.btn_hide.hide()


    def show_buttons(self):
        log_method_name()
        self.btn_net.show()
        self.btn_menu.show()
        self.btn_settings.show()
        self.btn_mods.show()
        self.btn_hide.show()
        self.btn_show.hide()

    def open_menu(self):
        log_method_name()
        self.main_menu.show()

    def open_settings(self):
        log_method_name()
        self.rect_select.show()

    def signal_rects_selected(self, rects):
        log_method_name()
        self.selected_rects = []
        if rects[0]:
            self.selected_rects.append('UltraRare')
        if rects[1]:
            self.selected_rects.append('HighValuable')
        if rects[2]:
            self.selected_rects.append('Valuable')
        if rects[3]:
            self.selected_rects.append('MidValuable')
        if rects[4]:
            self.selected_rects.append('LowValuable')

    def load_rects_selected(self):
        log_method_name()
        tree = ET.parse(CONFIG_PATH)
        root = tree.getroot()

        if root.findall('t1_color')[0].text == 'true':
            self.selected_rects.append('UltraRare')
        if root.findall('t2_color')[0].text == 'true':
            self.selected_rects.append('HighValuable')
        if root.findall('t3_color')[0].text == 'true':
            self.selected_rects.append('Valuable')
        if root.findall('t4_color')[0].text == 'true':
            self.selected_rects.append('MidValuable')
        if root.findall('t5_color')[0].text == 'true':
            self.selected_rects.append('LowValuable')

    def signal_nets_processing(self):
        log_method_name()
        self.btn_net.setIcon(self.net_processing)
        self.btn_menu.setDisabled(True)
        print("net processing")

    def signal_show_net(self):
        log_method_name()
        print("net processed")
        self.btn_net.setIcon(self.net_rdy)
        self.net_clickable = True
        self.btn_menu.setEnabled(True)

    def show_mods(self):
        log_method_name()
        self.mod_list.show()

    def show_net(self):
        log_method_name()
        if self.net_clickable:
            self.rectangles_ready = not self.rectangles_ready
            self.update()

    def setup_ui(self, Widget):
        log_method_name()
        self.setFixedSize(window_width, window_height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)

        self.net_processing = QIcon()
        self.net_processing.addPixmap(QPixmap(self.image_path + 'net_p.png'))
        self.net_nrdy = QIcon()
        self.net_nrdy.addPixmap(QPixmap(self.image_path + 'net_n.png'))
        self.net_rdy = QIcon()
        self.net_rdy.addPixmap(QPixmap(self.image_path + 'net_r.png'))
        self.btn_net = QPushButton()
        self.btn_net.setIcon(self.net_nrdy)
        self.btn_net.setStyleSheet('QPushButton{border: 0px solid;}')
        self.btn_net.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btn_menu = QPushButton()
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(self.image_path + 'menu.png'))
        self.btn_menu.setIcon(icon1)
        self.btn_menu.setStyleSheet('QPushButton{border: 0px solid;}')
        self.btn_menu.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btn_settings = QPushButton()
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(self.image_path + 'settings.png'))
        self.btn_settings.setIcon(icon1)
        self.btn_settings.setStyleSheet('QPushButton{border: 0px solid;}')
        self.btn_settings.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btn_mods = QPushButton()
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(self.image_path + 'mods.png'))
        self.btn_mods.setIcon(icon1)
        self.btn_mods.setStyleSheet('QPushButton{border: 0px solid;}')
        self.btn_mods.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btn_hide = QPushButton()
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(self.image_path + 'hide.png'))
        self.btn_hide.setIcon(icon1)
        self.btn_hide.setStyleSheet('QPushButton{border: 0px solid;}')
        self.btn_hide.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btn_show = QPushButton()
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(self.image_path + 'show.png'))
        self.btn_show.setIcon(icon1)
        self.btn_show.setStyleSheet('QPushButton{border: 0px solid;}')
        self.btn_show.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        vbox = QHBoxLayout()

        vbox.addWidget(self.btn_net)
        vbox.addWidget(self.btn_menu)
        vbox.addWidget(self.btn_settings)
        vbox.addWidget(self.btn_mods)
        vbox.addWidget(self.btn_hide)
        vbox.addWidget(self.btn_show)

        vbox.setContentsMargins(0, 30, window_width * width_multi, window_height * height_multi)

        self.btn_show.hide()
        self.setLayout(vbox)

    def paintEvent(self, r):
        log_method_name()
        self.qp = QPainter()
        self.qp.begin(self)
        if self.rectangles_ready:
            self.draw_net(r)
        self.qp.end()

    def draw_net(self, r):
        log_method_name()
        self.qp.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.red)
        for key, value in self.rect_processor.rectangles.items():
            if key in self.selected_rects:
                for val in value:
                    pen.setWidth(self.rect_processor.border_size)
                    pen.setColor(val[1])
                    self.qp.setPen(pen)
                    self.qp.drawRect(val[0])

    def mouseMoveEvent(self, QMouseEvent):

        for key, value in self.rect_processor.rectangles.items():
            if key in self.selected_rects:
                for val in value:
                    if val[0].x() < QMouseEvent.pos().x() < (val[0].x() + val[0].width()):
                        if val[0].y() < QMouseEvent.pos().y() < (val[0].y() + val[0].height()):
                            print(val[2].explicit_tiers)
                            print(val[2].score)


if __name__ == '__main__':
    import sys
    initialize_logging()
    app = QApplication(sys.argv)
    window = MainWidget()
    window.showFullScreen()
    window.setFocus()
    sys.exit(app.exec_())