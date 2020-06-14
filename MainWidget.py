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

        self.error_widget = DragWidget()
        load_styles(self.error_widget)
        self.error_widget.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Initialize other classes, order is important
        self.painter_widget = PainterWidget(screen_geometry)
        self.settings_widget = SettingsWidget(self.painter_widget)
        self.filters_widget = FiltersWidget(self.settings_widget)
        self.requester = Requester(self.settings_widget, self.painter_widget)
        self.last_requested_time = 0

        # Load mod configuration
        ModsContainer.load_mods_config(self.settings_widget.mod_file)

        # Setup Requester thread
        self.objThread = QThread()
        self.requester.moveToThread(self.objThread)
        self.requester.finished.connect(self.objThread.quit)
        self.requester.failed.connect(self._requester_failed)
        self.objThread.started.connect(self.requester.run)
        self.objThread.finished.connect(self._set_run_button_icon_run)

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
            self.run_button,
            self.painter_button,
            self.filters_button,
            self.settings_button,
            self.exit_button
        ]
        for button in self.buttons:
            button.setFixedWidth(25)
            button.setFixedHeight(25)
            button.setWindowFlags(Qt.Dialog)
            load_styles(button)
            layout.addWidget(button, 0, Qt.AlignTop)

        widget = QWidget(flags=Qt.Widget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def show_hide_buttons(self) -> None:
        log_method_name()
        for button in self.buttons:
            if button != self.drag_button:
                if button.isVisible():
                    button.hide()
                else:
                    button.show()

    def show_hide_widget(self, widget: QWidget) -> None:
        log_method_name()
        icon = QIcon()
        if widget.isVisible():
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
                if not widget.items:
                    return
                else:
                    icon.addPixmap(QPixmap(self.image_path + 'draw2.png'))
                    self.painter_button.setIcon(icon)
            widget.show()

    def _run_requester(self) -> None:
        # Do not allow to send requests too often
        now = time.time()
        if now - self.last_requested_time < 10:
            return
        self.last_requested_time = now
        icon = QIcon()
        icon.addPixmap(QPixmap(self.image_path + 'timer.png'))
        self.run_button.setIcon(icon)
        self.objThread.start()

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
        self.objThread.quit()
        self._set_run_button_icon_run()
        self._show_error_window(e.__str__())
        self.last_requested_time = 0

    # Set icon back after Requester is done
    def _set_run_button_icon_run(self) -> None:
        icon = QIcon()
        icon.addPixmap(QPixmap(self.image_path + 'run.png'))
        self.run_button.setIcon(icon)

    # Send new position to SettingsWidget and save it
    def update_pos_size(self) -> None:
        self.settings_widget.main_widget_y = self.y()
        self.settings_widget.save_cfg()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWidget(app.desktop().screenGeometry())
    window.show()
    os.chdir(PROJECT_ROOT)
    app.exec_()
