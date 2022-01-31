#!/usr/bin/env python3

import sys
import os
import re
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from src.DragButton import DragButton
from src.DragWidget import DragWidget
from src.FiltersWidget import FiltersWidget
from src.SettingsWidget import SettingsWidget
from src.Requester import Requester
from src.PainterWidget import PainterWidget
from src.ModsContainer import ModsContainer, DEFAULT_FILTER_PATH, PROJECT_ROOT
from src.FilterManager import LogListener, FilterManager
from src.utils import load_styles, initialize_logging, log_method_name


class MainWidget(QMainWindow):
    def __init__(self, screen_geometry: QRect):
        super(MainWidget, self).__init__(None)
        self.image_path = PROJECT_ROOT + "/img/"
        # initialize_logging()
        log_method_name()

        # Setup main widget UI
        self.screen_geometry = screen_geometry
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.buttons_size = QSize(26, 26)

        self.error_widget = DragWidget()
        load_styles(self.error_widget)
        self.error_widget.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Initialize other classes, order is important
        self.painter_widget = PainterWidget(screen_geometry)
        self.settings_widget = SettingsWidget(self.painter_widget)
        self.filters_widget = FiltersWidget(self.settings_widget)
        self.requester = Requester(self.settings_widget, self.painter_widget)
        self.last_requested_time = 0
        self.logListener = LogListener(self.settings_widget)
        self.filter_manager = FilterManager(self.settings_widget)

        # Load mod configuration
        ModsContainer.load_mods_config(self.settings_widget.mod_file)

        # Setup Requester thread
        self.objThread_requester = QThread()
        self.requester.moveToThread(self.objThread_requester)
        self.requester.finished.connect(self.objThread_requester.quit)
        self.requester.failed.connect(self._requester_failed)
        self.objThread_requester.started.connect(self.requester.run)
        self.objThread_requester.finished.connect(self._requester_finished)
        # self.requester.start()

        # Setup log listener and filter manager
        self.objThread_logListener = QThread()
        self.logListener.moveToThread(self.objThread_logListener)
        self.logListener.entered_map.connect(self._request_count_chaos_items)
        self.requester.finished_counting_chaos.connect(self._request_process_chaos_counters)
        self.logListener.start()

        # Setup main widget UI
        self.screen_geometry = screen_geometry
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.move(0, self.settings_widget.main_widget_y)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(0)

        # Setup buttons
        self.drag_button = DragButton(self, True)
        icon = QIcon()
        icon.addPixmap(QPixmap(self.image_path + 'move.png'))
        self.drag_button.setIcon(icon)

        self.mode_switch_button = QPushButton()
        self.mode_switch_button.clicked.connect(lambda: self.show_hide_widget(self.painter_widget))
        font = QFont()
        font.setBold(True)
        self.mode_switch_button.setFont(font)
        if self.settings_widget.mode == "chaos_recipe":
            self.mode_switch_button.setText("C")
        else:
            self.mode_switch_button.setText("R")
        self.mode_switch_button.clicked.connect(self._switch_mode)

        self.run_button = QPushButton()
        icon.addPixmap(QPixmap(self.image_path + 'run.png'))
        self.run_button.setIcon(icon)
        self.run_button.clicked.connect(self._run_requester)

        self.painter_button = QPushButton()
        self.painter_button.clicked.connect(lambda: self.show_hide_widget(self.painter_widget))
        icon.addPixmap(QPixmap(self.image_path + 'draw1.png'))
        self.painter_button.setIcon(icon)

        self.filters_button = QPushButton()
        self.filters_button.clicked.connect(lambda: self.show_hide_widget(self.filters_widget))
        icon.addPixmap(QPixmap(self.image_path + 'filter.png'))
        self.filters_button.setIcon(icon)

        self.settings_button = QPushButton()
        self.settings_button.clicked.connect(lambda: self.show_hide_widget(self.settings_widget))
        icon.addPixmap(QPixmap(self.image_path + 'settings.png'))
        self.settings_button.setIcon(icon)

        self.exit_button = QPushButton()
        self.exit_button.clicked.connect(QCoreApplication.quit)
        icon.addPixmap(QPixmap(self.image_path + 'exit.png'))
        self.exit_button.setIcon(icon)

        self.buttons = [
            self.drag_button,
            self.mode_switch_button,
            self.run_button,
            self.painter_button,
            self.filters_button,
            self.settings_button,
            self.exit_button
        ]
        for button in self.buttons:
            button.setFixedWidth(self.buttons_size.width())
            button.setFixedHeight(self.buttons_size.height())
            button.setWindowFlags(Qt.Dialog)
            load_styles(button)
            if button is self.mode_switch_button:
                layout.addWidget(button, 0, Qt.AlignTop)
            else:
                layout.addWidget(button, 0, Qt.AlignTop)
            if button is self.drag_button:
                self._prepare_stash_switch(layout)

        widget = QWidget(flags=Qt.Widget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _prepare_stash_switch(self, layout):
        stash_switch_layout = QHBoxLayout()
        self.stash_switch_button_left = QPushButton()
        self.stash_switch_button_right = QPushButton()
        self.stash_switch_button_left.clicked.connect(self.set_prev_stash)
        self.stash_switch_button_right.clicked.connect(self.set_next_stash)
        self.stash_switch_button_left.setFixedWidth(int(self.buttons_size.width()/2))
        self.stash_switch_button_left.setFixedHeight(self.buttons_size.height())
        self.stash_switch_button_right.setFixedWidth(int(self.buttons_size.width()/2))
        self.stash_switch_button_right.setFixedHeight(self.buttons_size.height())
        load_styles(self.stash_switch_button_left)
        load_styles(self.stash_switch_button_right)
        icon = QIcon()
        icon.addPixmap(QPixmap(self.image_path + 'next.png'))
        self.stash_switch_button_right.setIcon(icon)
        icon.addPixmap(QPixmap(self.image_path + 'next.png').transformed(QTransform().rotate(180)))
        self.stash_switch_button_left.setIcon(icon)
        self.stash_switch_button_right.setIconSize(QSize(self.buttons_size.width(), int(self.buttons_size.height()/3)))
        self.stash_switch_button_left.setIconSize(QSize(self.buttons_size.width(), int(self.buttons_size.height()/3)))

        stash_switch_layout.addWidget(self.stash_switch_button_left)
        stash_switch_layout.addWidget(self.stash_switch_button_right)
        self.stash_name = QLabel("")
        self.stash_name.setFixedHeight(12)
        self.stash_name.hide()
        load_styles(self.stash_name)
        stash_switch_layout.addWidget(self.stash_name)
        layout.addLayout(stash_switch_layout)

    def show_hide_buttons(self) -> None:
        log_method_name()
        self.stash_name.hide()
        for button in self.buttons:
            if button != self.drag_button:
                if button.isVisible():
                    button.hide()
                else:
                    button.show()
        if self.stash_switch_button_left.isVisible():
            self.stash_switch_button_left.hide()
            self.stash_switch_button_right.hide()
        else:
            self.stash_switch_button_left.show()
            self.stash_switch_button_right.show()

    def show_hide_widget(self, widget: QWidget, force_show=False) -> None:
        log_method_name()
        icon = QIcon()
        if widget.isVisible() and not force_show:
            if isinstance(widget, PainterWidget):
                if widget.config_change_mode:
                    widget.hide_modification_mode()
                    return
                else:
                    icon.addPixmap(QPixmap(self.image_path + 'draw1.png'))
                    self.painter_button.setIcon(icon)
            widget.hide()
        else:
            if isinstance(widget, PainterWidget):
                if (self.requester.mode == "rare_scanner" and not widget.items) or \
                        (self.requester.mode == "chaos_recipe" and not widget.chaos_sets):
                    return
                else:
                    icon.addPixmap(QPixmap(self.image_path + 'draw2.png'))
                    self.painter_button.setIcon(icon)
            widget.show()

    def _run_requester(self) -> None:
        # Do not allow to send requests too often
        now = time.time()
        self.stash_name.hide()
        if now - self.last_requested_time < 1:
            return
        self.last_requested_time = now
        icon = QIcon()
        icon.addPixmap(QPixmap(self.image_path + 'timer.png'))
        self.run_button.setIcon(icon)
        self.objThread_requester.start()

    def _show_error_window(self, error_message: str) -> None:

        # Break message with new lines if it is too long
        error_message = re.sub("(.{128})", "\\1\n", error_message, 0, re.DOTALL)

        error_message = "PoETiS Error:\n" + error_message

        layout = QVBoxLayout()
        label = QLabel(error_message)
        label.setStyleSheet('color: yellow')
        layout.addWidget(label)
        button_exit = QPushButton("Close")
        button_exit.clicked.connect(self.error_widget.hide)
        layout.addWidget(button_exit)
        self.error_widget.setLayout(layout)
        self.error_widget.show()

    def _requester_failed(self, e: Exception) -> None:
        self.objThread_requester.quit()
        self._set_run_button_icon_run()
        self._show_error_window(e.__str__())
        self.last_requested_time = 0

    def _requester_finished(self):
        self._set_run_button_icon_run()
        self.painter_widget.paint_items()
        self.painter_widget.update()
        self.show_hide_widget(self.painter_widget, True)

    # Set icon back after Requester is done
    def _set_run_button_icon_run(self) -> None:
        icon = QIcon()
        icon.addPixmap(QPixmap(self.image_path + 'run.png'))
        self.run_button.setIcon(icon)

    # Send new position to SettingsWidget and save it
    def update_pos_size(self) -> None:
        self.settings_widget.main_widget_y = self.y()
        self.settings_widget.save_cfg()

    def set_next_stash(self):
        self.settings_widget.set_next_active_stash()
        self.stash_name.setText(self.settings_widget.active_stash[0])
        self.stash_name.show()

    def set_prev_stash(self):
        self.settings_widget.set_prev_active_stash()
        self.stash_name.setText(self.settings_widget.active_stash[0])
        self.stash_name.show()

    def _switch_mode(self):
        mode = self.requester.mode

        if mode == "chaos_recipe":
            self.mode_switch_button.setText("R")
            self.requester.mode = "rare_scanner"
            self.painter_widget.change_mode("rare_scanner")
            self.settings_widget.mode = "rare_scanner"
            self.settings_widget.save_cfg()

        else:
            self.mode_switch_button.setText("C")
            self.requester.mode = "chaos_recipe"
            self.painter_widget.change_mode("chaos_recipe")
            self.settings_widget.mode = "chaos_recipe"
            self.settings_widget.save_cfg()

    def _request_count_chaos_items(self):
        self.requester.count_chaos_items()

    def _request_process_chaos_counters(self, counters):
        self.filter_manager.reload_filter(counters)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWidget(app.desktop().screenGeometry())
    window.show()
    os.chdir(PROJECT_ROOT)
    app.exec_()
