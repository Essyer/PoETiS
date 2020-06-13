import os
import xml.etree.ElementTree as ElementTree
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.PainterWidget import PainterWidget
from src.DragWidget import DragWidget
from src.Slider import Slider
from src.utils import log_method_name, prepare_cfg, load_styles
from src.ModsContainer import CONFIG_PATH

slider_colors = ["brown", "green", "blue", "yellow", "white"]


class SettingsWidget(DragWidget):
    configuration_changed = pyqtSignal(dict)

    def __init__(self, painter_widget: PainterWidget):
        self.painter_geometry = None
        super(SettingsWidget, self).__init__()
        log_method_name()
        self.painter_widget = painter_widget
        self.painter_widget.colors = slider_colors

        self._create_slider()  # Need to create if before loading configuration file to set tiles colors
        self._load_cfg()
        self._setup_ui()
        self.main_widget_y = 0

        self.painter_widget.geometry_changed.connect(self.painter_geometry_changed)

    def painter_geometry_changed(self, geometry: QRect) -> None:
        self.painter_geometry = geometry
        self.save_cfg()

    def _setup_ui(self) -> None:
        log_method_name()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        load_styles(self)
        layout_main = QVBoxLayout()

        label_id = QLabel("Account name")
        layout_main.addWidget(label_id)
        self.edit_account_name = QLineEdit(self.account_name)
        self.edit_account_name.textChanged.connect(self.save_cfg)
        layout_main.addWidget(self.edit_account_name)

        label_stash = QLabel("Stash name")
        layout_main.addWidget(label_stash)
        self.edit_stash = QLineEdit(self.stash_name)
        self.edit_stash.textChanged.connect(self.save_cfg)
        layout_main.addWidget(self.edit_stash)

        label_base_league_name = QLabel("League base name")
        layout_main.addWidget(label_base_league_name)
        self.edit_base_league_name = QLineEdit(self.league_base_name)
        self.edit_base_league_name.textChanged.connect(self._update_leagues_combo)
        self.edit_base_league_name.textChanged.connect(self.save_cfg)
        layout_main.addWidget(self.edit_base_league_name)

        label_league = QLabel("League")
        layout_main.addWidget(label_league)
        self.combo_league = QComboBox()
        self._update_leagues_combo()
        self.combo_league.currentTextChanged.connect(self.save_cfg)
        layout_main.addWidget(self.combo_league)

        label_session = QLabel("Session ID")
        layout_main.addWidget(label_session)
        self.edit_session = QLineEdit(self.session_id)
        self.edit_session.textChanged.connect(self.save_cfg)
        layout_main.addWidget(self.edit_session)

        label_session = QLabel("Stash type")
        layout_main.addWidget(label_session)
        layout_radio = QHBoxLayout()
        self.radio_stash_normal = QRadioButton("Normal")
        self.radio_stash_normal.toggled.connect(self.save_cfg)
        radio_stash_quad = QRadioButton("Quad")
        radio_stash_quad.toggled.connect(self.save_cfg)
        if self.stash_type == "Normal":
            self.radio_stash_normal.setChecked(True)
        else:
            radio_stash_quad.setChecked(True)
        layout_radio.addWidget(self.radio_stash_normal)
        layout_radio.addWidget(radio_stash_quad)
        layout_main.addLayout(layout_radio)

        btn_adjust_net = QPushButton("Adjust net position and size")
        btn_adjust_net.clicked.connect(self.painter_widget.show_hide_config)
        layout_main.addWidget(btn_adjust_net)

        label_session = QLabel("Item tiers to detect")
        layout_main.addWidget(label_session)
        layout_slider = QHBoxLayout()
        self.slider.set_range(1, 5)
        self.slider.set_value(self.slider_value)
        load_styles(self.slider)
        layout_slider.addWidget(self.slider)
        layout_main.addLayout(layout_slider)

        self.slider.on_value_changed_call(self.save_cfg)

        self.btn_hide = QPushButton("Close")
        self.btn_hide.clicked.connect(self.close)
        layout_main.addWidget(self.btn_hide)

        self.setLayout(layout_main)

    def _create_slider(self):
        self.slider = Slider()

    def close(self) -> None:
        self.hide()
        self.painter_widget.hide_modification_mode()

    def _update_leagues_combo(self) -> None:
        self.combo_league.clear()
        main_name = self.edit_base_league_name.text()
        index = 0
        for name in [main_name, main_name + " HC", "SSF " + main_name, "SSF " + main_name + " HC", "Standard",
                     "Hardcore", "SSF Hardcore", "SSF Standard"]:
            self.combo_league.insertItem(index, name)
            index += 1
        self.combo_league.setCurrentText(self.league)

    @staticmethod
    def load_main_widget_y() -> int:
        tree = ElementTree.parse(CONFIG_PATH)
        root = tree.getroot()
        return int(root.find("main_widget_y").text)

    def _load_cfg(self) -> None:
        log_method_name()
        if not os.path.isfile(CONFIG_PATH):
            prepare_cfg(CONFIG_PATH)
        tree = ElementTree.parse(CONFIG_PATH)
        root = tree.getroot()
        self.account_name = root.find("account_name").text
        self.stash_name = root.find("stash_name").text
        self.league = root.find("league").text
        self.league_base_name = root.find("league_base_name").text
        self.session_id = root.find("session_id").text
        if root.find("stash_type").text == "Normal":
            self.stash_type = "Normal"
        else:
            self.stash_type = "Quad"

        self._set_values_from_cfg()

    def _set_values_from_cfg(self) -> None:
        tree = ElementTree.parse(CONFIG_PATH)
        root = tree.getroot()

        slider_color1 = root.find("slider_color1").text
        slider_color2 = root.find("slider_color2").text
        slider_color3 = root.find("slider_color3").text
        slider_color4 = root.find("slider_color4").text
        slider_color5 = root.find("slider_color5").text
        colors = [slider_color1, slider_color2, slider_color3, slider_color4, slider_color5]

        self.painter_widget.colors = colors
        self.slider.set_colors(colors)
        self.slider_value = int(root.find("slider_value").text)

        self.main_widget_y = int(root.find("main_widget_y").text)

        painter_geometry = QRect(int(root.find("painter_x").text), int(root.find("painter_y").text),
                                 int(root.find("painter_w").text), int(root.find("painter_h").text))
        self.painter_widget.setGeometry(painter_geometry)
        self.painter_widget.setFixedWidth(painter_geometry.width())
        self.painter_widget.setFixedHeight(painter_geometry.height())

    def save_cfg(self) -> None:
        log_method_name()
        tree = ElementTree.parse(CONFIG_PATH)
        root = tree.getroot()

        root.find("account_name").text = self.edit_account_name.text()
        root.find("stash_name").text = self.edit_stash.text()
        root.find("league_base_name").text = self.edit_base_league_name.text()
        root.find("league").text = self.combo_league.currentText()
        root.find("session_id").text = self.edit_session.text()
        stash_type = "Normal" if self.radio_stash_normal.isChecked() else "Quad"
        root.find("stash_type").text = stash_type
        root.find("main_widget_y").text = str(self.main_widget_y)
        if hasattr(self, "slider"):
            root.find("slider_value").text = str(self.slider.value)
        if self.painter_geometry:
            root.find("painter_x").text = str(self.painter_geometry.x())
            root.find("painter_y").text = str(self.painter_geometry.y())
            root.find("painter_w").text = str(self.painter_geometry.width())
            root.find("painter_h").text = str(self.painter_geometry.height())

        tree.write(CONFIG_PATH)

        # Painter already notifies us about size/position changes through signal,
        # I don't know how to do bidirectional signaling so I'm setting values by reference
        self.painter_widget.stash_type = stash_type
        if hasattr(self, "slider"):
            self.painter_widget.number_of_mods_to_draw = self.slider.value

        self.configuration_changed.emit(self.get_settings_for_requester())  # Notify Requester

    def get_settings_for_requester(self) -> dict:
        return {
            "account_name": self.edit_account_name.text(),
            "stash_name": self.edit_stash.text(),
            "league": self.combo_league.currentText(),
            "session_id": self.edit_session.text()
        }
