import os
import re
import xml.etree.ElementTree as ElementTree
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from src.PainterWidget import PainterWidget
from src.DragWidget import DragWidget
from src.Slider import Slider
from src.utils import log_method_name, prepare_cfg, load_styles, default_league_name, xml_indent
from src.ModsContainer import CONFIG_PATH, FILTER_DIR, DEFAULT_FILTER_PATH

slider_colors = ["brown", "green", "blue", "yellow", "white"]
stash_default_text = "Add your stash here..."


class SettingsWidget(DragWidget):
    configuration_changed = pyqtSignal(dict)
    stash_item_change_already_called = False  # No idea what's going on... If I don't check it like that when you modify
    # text of last (default) row, program ends up in infinite loop between _process_stash_item_changed and
    # _add_stash_item_to_table. It is probably because in the latter insertRow() triggers signal of changed item.
    # I don't have better solution right now and league starts in 2 days.
    active_stash = ["", 0, "normal"]

    def __init__(self, painter_widget: PainterWidget):
        self.painter_geometry = None
        super(SettingsWidget, self).__init__()
        log_method_name()
        self.painter_widget = painter_widget
        self.painter_widget.colors = slider_colors
        self.mode = "chaos_recipe"  # default mode
        self.allow_identified = False
        self.fill_greedy = True
        self.auto_reload_filter = False
        self.poe_log_path = ""
        self.poe_filter_path = ""
        self.poe_filter_name = ""
        self.maximum_chaos_sets = 16

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

        button_stashes = QPushButton("Add/remove stashes")
        layout_main.addWidget(button_stashes)
        self._prepare_stashes_window()
        button_stashes.clicked.connect(self.window_stashes.show)

        label_mod_config = QLabel("Mod Filter")
        layout_main.addWidget(label_mod_config)
        self.combo_mod_file = QComboBox()
        self._update_mod_file_combo()
        self.combo_mod_file.activated.connect(self.save_cfg)
        self.combo_mod_file.installEventFilter(self)
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

        self.button_show_account_session = QPushButton("Show/hide account name and session")
        layout_main.addWidget(self.button_show_account_session)

        self.label_account_name = QLabel("Account name")
        layout_main.addWidget(self.label_account_name)
        self.edit_account_name = QLineEdit(self.account_name)
        self.edit_account_name.textChanged.connect(self.save_cfg)
        layout_main.addWidget(self.edit_account_name)

        self.label_session = QLabel("Session ID")
        layout_main.addWidget(self.label_session)
        self.edit_session = QLineEdit(self.session_id)
        self.edit_session.textChanged.connect(self.save_cfg)
        layout_main.addWidget(self.edit_session)

        # Hide account name and session ID if any of them was provided before
        if self.account_name or self.session_id:
            self.hide_account_session(True)
        self.button_show_account_session.clicked.connect(self.hide_account_session)

        btn_adjust_net = QPushButton("Adjust net position and size")
        btn_adjust_net.clicked.connect(self.painter_widget.show_hide_config)
        layout_main.addWidget(btn_adjust_net)

        label_session = QLabel("Minimum number of item mods to draw a frame")
        layout_main.addWidget(label_session)
        layout_slider = QHBoxLayout()
        self.slider.set_range(1, 5)
        self.slider.set_value(self.slider_value)
        load_styles(self.slider)
        layout_slider.addWidget(self.slider)
        layout_main.addLayout(layout_slider)

        self.slider.on_value_changed_call(self.save_cfg)

        self.radio_allow_identified = QRadioButton()
        self.radio_allow_identified.setAutoExclusive(False)
        self.radio_allow_identified.setChecked(self.allow_identified)
        self.radio_allow_identified.clicked.connect(self.switch_allow_identified)
        layout_radio = QHBoxLayout()
        layout_radio.setAlignment(Qt.AlignLeft)
        layout_radio.addWidget(self.radio_allow_identified)
        layout_radio.addWidget(QLabel("Allow identified items in chaos recipe"))
        layout_main.addLayout(layout_radio)

        self.radio_fill_greedy = QRadioButton()
        self.radio_fill_greedy.setAutoExclusive(False)
        self.radio_fill_greedy.setChecked(self.fill_greedy)
        self.radio_fill_greedy.clicked.connect(self.switch_fill_greedy)
        layout_radio = QHBoxLayout()
        layout_radio.setAlignment(Qt.AlignLeft)
        layout_radio.addWidget(self.radio_fill_greedy)
        layout_radio.addWidget(QLabel("Fill chaos recipe with more than one ilvl < 75 item"))
        layout_main.addLayout(layout_radio)

        self.radio_auto_reload = QRadioButton()
        self.radio_auto_reload.setAutoExclusive(False)
        self.radio_auto_reload.setChecked(self.auto_reload_filter)
        self.radio_auto_reload.clicked.connect(self.switch_auto_reload)
        layout_radio = QHBoxLayout()
        layout_radio.setAlignment(Qt.AlignLeft)
        layout_radio.addWidget(self.radio_auto_reload)
        layout_radio.addWidget(QLabel("Reload filter automatically after entering a map"))
        layout_main.addLayout(layout_radio)

        layout_main.addWidget(QLabel("PoE log file location"))
        self.poe_log_path_button = QPushButton()
        self.poe_log_path_button.clicked.connect(self.select_poe_log_file)
        if self.poe_log_path:
            self.poe_log_path_button.setText(self.path_for_button(self.poe_log_path))
        else:
            self.poe_log_path_button.setText("Set PoE log file location")
        self.poe_log_path_button.setToolTip("PoE log file location")
        layout_main.addWidget(self.poe_log_path_button)

        layout_main.addWidget(QLabel("PoE filter file location"))
        self.poe_filter_path_button = QPushButton()
        self.poe_filter_path_button.clicked.connect(self.select_poe_filter_file)
        if self.poe_filter_path:
            self.poe_filter_path_button.setText(self.path_for_button(self.poe_filter_path))
        else:
            self.poe_filter_path_button.setText("Set PoE filter file location")
        self.poe_filter_path_button.setToolTip("PoE filter file location")
        layout_main.addWidget(self.poe_filter_path_button)

        layout_main.addWidget(QLabel("Max number of chaos recipe sets in stash"))
        self.maximum_chaos_sets_text = QLineEdit(str(self.maximum_chaos_sets))
        self.maximum_chaos_sets_text.textChanged.connect(self.save_cfg)
        layout_main.addWidget(self.maximum_chaos_sets_text)

        self.btn_hide = QPushButton("Close")
        self.btn_hide.clicked.connect(self.close)
        layout_main.addWidget(self.btn_hide)

        self.setLayout(layout_main)

    def _prepare_stashes_window(self):
        self.window_stashes = DragWidget()
        self.window_stashes.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        load_styles(self.window_stashes)
        self.window_stashes.setFixedWidth(400)  # maybe some day I will make it to resize to columns width...

        self.widget_stashes = QTableWidget(0, 2)
        self.widget_stashes.itemChanged.connect(self._process_stash_item_changed)
        self.widget_stashes.setHorizontalHeaderLabels(["Name", "Normal/Quad"])
        self.widget_stashes.verticalHeader().hide()
        header = self.widget_stashes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.widget_stashes.adjustSize()
        self.stashes_ui = []
        for stash in self.stashes:
            if stash["name"]:
                self._add_stash_item_to_table(stash["name"], stash["type"])
        self._add_stash_item_to_table(stash_default_text, "normal")

        load_styles(self.widget_stashes)
        layout = QVBoxLayout()
        layout.addWidget(self.widget_stashes)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.window_stashes.hide)
        layout.addWidget(close_button)
        self.window_stashes.setLayout(layout)

    # I miss C++ lambdas
    def _add_stash_item_to_table(self, name: str, stash_type: str) -> None:
        row = self.widget_stashes.rowCount()
        self.widget_stashes.insertRow(row)
        table_item = QTableWidgetItem(name)
        self.widget_stashes.setItem(row, 0, table_item)
        group_box = QGroupBox()
        box_layout = QHBoxLayout()
        radio1 = QRadioButton()
        radio2 = QRadioButton()
        if stash_type == "normal":
            radio1.setChecked(True)
        else:
            radio2.setChecked(True)
        radio1.clicked.connect(self._process_stash_item_changed)
        radio2.clicked.connect(self._process_stash_item_changed)
        box_layout.addWidget(radio1)
        box_layout.addStretch(1)
        box_layout.addWidget(radio2)
        group_box.setLayout(box_layout)

        self.widget_stashes.setCellWidget(row, 1, group_box)

        self.stashes_ui.append([table_item, radio1, radio2])

    def _process_stash_item_changed(self):
        if hasattr(self, "edit_account_name"):  # verify if _setup_ui finished
            self.stashes = []
            stashes_to_remove = []
            for index, item in enumerate(self.stashes_ui):
                name = item[0].text()
                stash_type = "normal" if item[1].isChecked() else "quad"
                if name == "":
                    stashes_to_remove.append(index)
                if name != stash_default_text and name != "":
                    self.stashes.append({"name": name, "type": stash_type})

            for index in stashes_to_remove:
                self.stashes_ui.remove(self.stashes_ui[index])
                self.widget_stashes.removeRow(index)

            if len(self.stashes_ui) == 2:
                self.active_stash = [self.stashes_ui[0][0].text(), 0,
                                     "normal" if self.stashes_ui[0][1].isChecked() else "quad"]
            if self.stashes_ui:
                stash_text = self.stashes_ui[-1][0].text()
                if stash_text != stash_default_text and not self.stash_item_change_already_called:
                    self.stash_item_change_already_called = True
                    self._add_stash_item_to_table(stash_default_text, "normal")
            self.stash_item_change_already_called = False
            self.save_cfg()

    def eventFilter(self, target, event) -> bool:
        if target == self.combo_mod_file and event.type() == QEvent.MouseButtonPress:
            self._update_mod_file_combo()
        return False

    def _create_slider(self) -> None:
        self.slider = Slider()

    def close(self) -> None:
        self.hide()
        self.painter_widget.hide_modification_mode()
        if self.poe_log_path_button:
            self.poe_log_path_button.setText(self.path_for_button(self.poe_log_path))

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
        text_bak = None
        if self.combo_mod_file.currentText():
            text_bak = self.combo_mod_file.currentText()
        self.combo_mod_file.clear()
        filters = os.listdir(FILTER_DIR)
        # there is probably a better way to exclude gitignore...
        ignore = ["mods_empty.xml", ".gitignore"]
        for f in filters:
            if f not in ignore and os.path.isfile(FILTER_DIR + f):
                self.combo_mod_file.addItem(f)
        if text_bak:
            print(text_bak)
            self.combo_mod_file.setCurrentText(os.path.basename(text_bak))
        else:
            self.combo_mod_file.setCurrentText(os.path.basename(self.mod_file))

    def _load_cfg(self) -> None:
        log_method_name()
        if not os.path.isfile(CONFIG_PATH):
            prepare_cfg(CONFIG_PATH)
        tree = ElementTree.parse(CONFIG_PATH)
        root = tree.getroot()
        self.account_name = self._cfg_load_or_default(root, "account_name")
        stashes_nodes = self._cfg_load_stashes(root)
        self.stashes = []
        for stash in stashes_nodes:
            self.stashes.append(stash)
        if self.stashes:
            self.active_stash = [self.stashes[0]["name"], 0, self.stashes[0]["type"]]
        # mod_file should probably be validated upon loading (for existence)
        self.mod_file = self._cfg_load_or_default(root, "mod_file", DEFAULT_FILTER_PATH)
        self.league = self._cfg_load_or_default(root, "league")
        self.league_base_name = self._cfg_load_or_default(root, "league_base_name", default_league_name)
        self.session_id = self._cfg_load_or_default(root, "session_id")
        self.stash_type = self._cfg_load_or_default(root, "stash_type", "quad")
        self.painter_widget.stash_type = self.stash_type
        self.mode = self._cfg_load_or_default(root, "mode", "chaos_recipe")
        self.allow_identified = self._cfg_load_or_default(root, "allow_identified", "False") == "True"
        self.fill_greedy = self._cfg_load_or_default(root, "fill_greedy", "True") == "True"
        self.auto_reload_filter = self._cfg_load_or_default(root, "auto_reload", "True") == "True"
        self.poe_log_path = self._cfg_load_or_default(root, "log_path", "Set PoE log file location")
        self.poe_filter_path = self._cfg_load_or_default(root, "filter_path", "Set PoE filter file location")
        self.poe_filter_name = self._cfg_load_or_default(root, "filter_name", "")
        self.maximum_chaos_sets = int(self._cfg_load_or_default(root, "max_chaos_sets", "16"))

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
        self.slider_value = int(self._cfg_load_or_default(root, "slider_value", "1"))
        # maybe just read this from settings widget at run time?
        self.painter_widget.number_of_mods_to_draw = self.slider_value

        self.main_widget_y = int(self._cfg_load_or_default(root, "main_widget_y", "0"))

        painter_x = int(self._cfg_load_or_default(root, "painter_x", "250"))
        painter_y = int(self._cfg_load_or_default(root, "painter_y", "250"))
        painter_w = int(self._cfg_load_or_default(root, "painter_w", "500"))
        painter_h = int(self._cfg_load_or_default(root, "painter_h", "500"))
        painter_geometry = QRect(painter_x, painter_y, painter_w, painter_h)
        self.painter_widget.setGeometry(painter_geometry)
        self.painter_widget.setFixedWidth(painter_geometry.width())
        self.painter_widget.setFixedHeight(painter_geometry.height())
        self.painter_widget.mode = self.mode

    def save_cfg(self) -> None:
        log_method_name()
        tree = ElementTree.parse(CONFIG_PATH)
        root = tree.getroot()

        self._cfg_set_or_create(root, "account_name", self.edit_account_name.text())
        self._cfg_save_stashes(root)
        self._cfg_set_or_create(root, "mod_file", FILTER_DIR + self.combo_mod_file.currentText())
        self._cfg_set_or_create(root, "league_base_name", self.edit_base_league_name.text())
        self._cfg_set_or_create(root, "league", self.combo_league.currentText())
        self._cfg_set_or_create(root, "session_id", self.edit_session.text())
        self._cfg_set_or_create(root, "main_widget_y", str(self.main_widget_y))
        if hasattr(self, "slider"):
            self._cfg_set_or_create(root, "slider_value", str(self.slider.value))
        if self.painter_geometry:
            self._cfg_set_or_create(root, "painter_x", str(self.painter_geometry.x()))
            self._cfg_set_or_create(root, "painter_y", str(self.painter_geometry.y()))
            self._cfg_set_or_create(root, "painter_w", str(self.painter_geometry.width()))
            self._cfg_set_or_create(root, "painter_h", str(self.painter_geometry.height()))

        self._cfg_set_or_create(root, "mode", self.mode)
        self._cfg_set_or_create(root, "allow_identified", str(self.allow_identified))
        self._cfg_set_or_create(root, "fill_greedy", str(self.fill_greedy))
        self._cfg_set_or_create(root, "auto_reload", str(self.auto_reload_filter))
        self._cfg_set_or_create(root, "log_path", self.poe_log_path)
        self._cfg_set_or_create(root, "filter_path", self.poe_filter_path)
        if self.poe_filter_name:
            self.poe_filter_name = self.poe_filter_name.rstrip()
        self._cfg_set_or_create(root, "filter_name", self.poe_filter_name)
        self._cfg_set_or_create(root, "max_chaos_sets", self.maximum_chaos_sets_text.text())
        self.maximum_chaos_sets = int(self.maximum_chaos_sets_text.text())

        xml_indent(root)
        tree.write(CONFIG_PATH)

        # Painter already notifies us about size/position changes through signal,
        # I don't know how to do bidirectional signaling so I'm setting values by reference
        self.painter_widget.stash_type = self.stashes[0]["type"] if self.stashes else "normal"
        if hasattr(self, "slider"):
            self.painter_widget.number_of_mods_to_draw = self.slider.value
        self.painter_widget.update()
        if self.stashes and not self.active_stash[0]:
            self.active_stash = [self.stashes[0]["name"], 0, self.stashes[0]["type"]]

        self.configuration_changed.emit(self.get_settings_for_requester())  # Notify Requester

    @staticmethod
    def _cfg_set_or_create(root: ElementTree, match: str, new_value: str) -> None:
        ele = root.find(match)
        if ele is None:
            ele = ElementTree.SubElement(root, match)

        ele.text = new_value

    @staticmethod
    def _cfg_load_or_default(root: ElementTree, match: str, default="") -> str:
        ele = root.find(match)
        if ele is None:
            return default
        return ele.text

    @staticmethod
    def _cfg_load_stashes(root: ElementTree) -> list:
        stashes = root.find('stashes')
        if stashes is None:
            return [{'name': "", 'type': "normal"}]
        return [{'name': x.text, 'type': x.attrib['type']} for x in list(stashes)]

    def _cfg_save_stashes(self, root: ElementTree) -> None:
        stashes = root.find('stashes')
        if stashes is None:
            stashes = ElementTree.SubElement(root, "stashes")

        for child in list(stashes):
            stashes.remove(child)
        for stash in self.stashes:
            if stash["name"]:
                node = ElementTree.SubElement(stashes, "stash")
                node.text = stash["name"]
                node.set("type", stash["type"])

    def get_settings_for_requester(self) -> dict:
        return {
            "account_name": self.edit_account_name.text(),
            "stash_name": self.active_stash[0],
            "league": self.combo_league.currentText(),
            "session_id": self.edit_session.text(),
            "mod_file": FILTER_DIR + self.combo_mod_file.currentText(),
            "mode": self.mode,
            "allow_identified": self.allow_identified,
            "fill_greedy": self.fill_greedy
        }

    def hide_account_session(self, force_hide=False):
        if self.edit_account_name.isVisible() or force_hide:
            self.edit_account_name.hide()
            self.label_account_name.hide()
            self.edit_session.hide()
            self.label_session.hide()
            self.adjustSize()
        else:
            self.edit_account_name.show()
            self.label_account_name.show()
            self.edit_session.show()
            self.label_session.show()
            self.adjustSize()

    def set_next_active_stash(self):
        index = self.active_stash[1]+1
        if index < len(self.stashes):
            self.active_stash = [self.stashes[index]["name"], index, self.stashes[index]["type"]]
        else:
            self.active_stash = [self.stashes[0]["name"], 0, self.stashes[0]["type"]]
        self.painter_widget.stash_type = self.active_stash[2]

    def set_prev_active_stash(self):
        index = self.active_stash[1] - 1
        if index >= 0:
            self.active_stash = [self.stashes[index]["name"], index, self.stashes[index]["type"]]
        else:
            index = len(self.stashes) - 1
            self.active_stash = [self.stashes[index]["name"], index, self.stashes[index]["type"]]
        self.painter_widget.stash_type = self.active_stash[2]

    def switch_allow_identified(self):
        self.allow_identified = self.radio_allow_identified.isChecked()
        self.save_cfg()

    def switch_fill_greedy(self):
        self.fill_greedy = self.radio_fill_greedy.isChecked()
        self.save_cfg()

    def switch_auto_reload(self):
        self.auto_reload_filter = self.radio_auto_reload.isChecked()
        self.save_cfg()

    def select_poe_log_file(self):
        current_path = ""
        if self.poe_log_path:
            current_path = os.path.dirname(self.poe_log_path)
        log_path = QFileDialog.getOpenFileName(self, "Select PoE log file", current_path)[0]

        if log_path:
            if "client.txt" not in log_path.lower():
                self.poe_log_path_button.setText("Invalid log file!")
            else:
                self.poe_log_path_button.setText(self.path_for_button(log_path))
                self.poe_log_path = log_path
                self.save_cfg()

    def select_poe_filter_file(self):
        current_path = ""
        if self.poe_filter_path:
            current_path = os.path.dirname(self.poe_filter_path)
        filter_path = QFileDialog.getOpenFileName(self, "Select PoE filter file", current_path)[0]
        if not filter_path and not self.poe_filter_path:
            self.poe_filter_path_button.setText("Set PoE filter file location")
        else:
            filter_path = filter_path or self.poe_filter_path
            correct_filter = False
            try:
                with open(filter_path, 'r') as f:
                    lines_left = 50  # Check next lines for filter name
                    for line in f:
                        if "#poetis start" in line.lower():
                            lines_left = -1  # Skip lines modified by us
                        if "#poetis end" in line.lower():
                            lines_left = 50  # Check next lines for filter name
                        if lines_left > 0:
                            lines_left -= 1
                            if "type:" in line.lower():
                                print(os.path.splitext(os.path.basename(filter_path))[0])
                                self.poe_filter_name = os.path.splitext(os.path.basename(filter_path))[0]
                                correct_filter = True
                                break
                            elif "name:" in line.lower():
                                self.poe_filter_name = line[6:]
                                correct_filter = True
                                break
                if correct_filter:
                    self.poe_filter_path_button.setText(self.path_for_button(filter_path))
                    self.poe_filter_path = filter_path
                    self.save_cfg()
                else:
                    self.poe_filter_path_button.setText("Invalid filter file!")
            except OSError as e:
                self.poe_filter_path = ""
                self.save_cfg()
                self.poe_filter_path_button.setText("Filter file not found!")

    @staticmethod
    def path_for_button(path) -> str:
        out = ""
        if len(path) > 50:
            out = "..."
        return out + path[-50:]
