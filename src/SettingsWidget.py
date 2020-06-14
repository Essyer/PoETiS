import os
import xml.etree.ElementTree as ElementTree
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.PainterWidget import PainterWidget
from src.DragWidget import DragWidget
from src.Slider import Slider
from src.utils import log_method_name, prepare_cfg, load_styles, default_league_name
from src.ModsContainer import CONFIG_PATH, FILTER_DIR, DEFAULT_FILTER_PATH

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

        label_mod_config = QLabel("Mod Filter")
        layout_main.addWidget(label_mod_config)
        self.combo_mod_file = QComboBox()
        self._update_mod_file_combo()
        self.combo_mod_file.activated.connect(self.save_cfg)
        layout_main.addWidget(self.combo_mod_file)

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
        radio_stash_quad = QRadioButton("Quad")
        if self.stash_type == "Normal":
            self.radio_stash_normal.setChecked(True)
        else:
            radio_stash_quad.setChecked(True)
        self.radio_stash_normal.toggled.connect(self.save_cfg)
        radio_stash_quad.toggled.connect(self.save_cfg)

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

    def _update_mod_file_combo(self) -> None:
        # TODO refresh button to trigger this
        self.combo_mod_file.clear()
        filters = os.listdir(FILTER_DIR)
        # there is probably a better way to exclude gitignore...
        ignore = ["mods_empty.xml", ".gitignore"]
        for f in filters:
            if f not in ignore and os.path.isfile(FILTER_DIR + f):
                self.combo_mod_file.addItem(f)

        self.combo_mod_file.setCurrentText(os.path.basename(self.mod_file))

    @staticmethod
    def load_main_widget_y() -> int:
        # no longer used
        tree = ElementTree.parse(CONFIG_PATH)
        root = tree.getroot()
        return int(root.find("main_widget_y").text)

    def _load_cfg(self) -> None:
        log_method_name()
        if not os.path.isfile(CONFIG_PATH):
            prepare_cfg(CONFIG_PATH)
        tree = ElementTree.parse(CONFIG_PATH)
        root = tree.getroot()
        self.account_name = self._cfg_load_or_default(root, "account_name")
        self.stash_name = self._cfg_load_or_default(root, "stash_name")
        # mod_file should probably be validated upon loading (for existence)
        self.mod_file = self._cfg_load_or_default(root, "mod_file", DEFAULT_FILTER_PATH)
        self.league = self._cfg_load_or_default(root, "league")
        self.league_base_name = self._cfg_load_or_default(root, "league_base_name", default_league_name)
        self.session_id = self._cfg_load_or_default(root, "session_id")
        self.stash_type = self._cfg_load_or_default(root, "stash_type", "Quad")
        self.painter_widget.stash_type = self.stash_type
        self.main_widget_y = self._cfg_load_or_default(root, "main_widget_y", "0")

        self._set_values_from_cfg()


    def _set_values_from_cfg(self) -> None:
        tree = ElementTree.parse(CONFIG_PATH)
        root = tree.getroot()

        slider_color1 = self._cfg_load_or_default(root, "slider_color1", "brown")
        slider_color2 = self._cfg_load_or_default(root, "slider_color2", "blue")
        slider_color3 = self._cfg_load_or_default(root, "slider_color3", "green")
        slider_color4 = self._cfg_load_or_default(root, "slider_color4", "yellow")
        slider_color5 = self._cfg_load_or_default(root, "slider_color5", "white")
        colors = [slider_color1, slider_color2, slider_color3, slider_color4, slider_color5]

        self.painter_widget.colors = colors
        self.slider.set_colors(colors)
        self.slider_value = int(self._cfg_load_or_default(root, "slider_value", "3"))
        # maybe just read this from settings widget at run time?
        self.painter_widget.number_of_mods_to_draw = self.slider_value

        self.main_widget_y = int(root.find("main_widget_y").text)

        painter_x = int(self._cfg_load_or_default(root, "painter_x", "250"))
        painter_y = int(self._cfg_load_or_default(root, "painter_y", "250"))
        painter_w = int(self._cfg_load_or_default(root, "painter_w", "500"))
        painter_h = int(self._cfg_load_or_default(root, "painter_h", "500"))
        painter_geometry = QRect(painter_x, painter_y, painter_w, painter_h)
        self.painter_widget.setGeometry(painter_geometry)
        self.painter_widget.setFixedWidth(painter_geometry.width())
        self.painter_widget.setFixedHeight(painter_geometry.height())

    def save_cfg(self) -> None:
        log_method_name()
        tree = ElementTree.parse(CONFIG_PATH)
        root = tree.getroot()

        self._cfg_set_or_create(root, "account_name", self.edit_account_name.text())
        self._cfg_set_or_create(root, "stash_name", self.edit_stash.text())
        self._cfg_set_or_create(root, "mod_file", FILTER_DIR + self.combo_mod_file.currentText())
        self._cfg_set_or_create(root, "league_base_name", self.edit_base_league_name.text())
        self._cfg_set_or_create(root, "league", self.combo_league.currentText())
        self._cfg_set_or_create(root, "session_id", self.edit_session.text())
        stash_type = "Normal" if self.radio_stash_normal.isChecked() else "Quad"
        self._cfg_set_or_create(root, "stash_type", stash_type)
        self._cfg_set_or_create(root, "main_widget_y", str(self.main_widget_y))
        if hasattr(self, "slider"):
            self._cfg_set_or_create(root, "slider_value", str(self.slider.value))
        if self.painter_geometry:
            self._cfg_set_or_create(root, "painter_x", str(self.painter_geometry.x()))
            self._cfg_set_or_create(root, "painter_y", str(self.painter_geometry.y()))
            self._cfg_set_or_create(root, "painter_w", str(self.painter_geometry.width()))
            self._cfg_set_or_create(root, "painter_h", str(self.painter_geometry.height()))

        tree.write(CONFIG_PATH)

        # Painter already notifies us about size/position changes through signal,
        # I don't know how to do bidirectional signaling so I'm setting values by reference
        self.painter_widget.stash_type = stash_type
        if hasattr(self, "slider"):
            self.painter_widget.number_of_mods_to_draw = self.slider.value

        self.configuration_changed.emit(self.get_settings_for_requester())  # Notify Requester


    def _cfg_set_or_create(self, root, match, new_value) -> None:
        ele = root.find(match)
        if ele == None:
            ele = ElementTree.SubElement(root, match)

        ele.text = new_value

    def _cfg_load_or_default(self, root, match, default="") -> str:
        ele = root.find(match)
        if ele == None:
            return default
        return ele.text


    def get_settings_for_requester(self) -> dict:
        return {
            "account_name": self.edit_account_name.text(),
            "stash_name": self.edit_stash.text(),
            "league": self.combo_league.currentText(),
            "session_id": self.edit_session.text(),
            "mod_file": FILTER_DIR + self.combo_mod_file.currentText()
        }
