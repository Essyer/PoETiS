import platform
from time import sleep
from src.utils import log_method_name, load_styles, print_windows_warning

try:
    import pywintypes  # Need to import even though not using, win32gui crashes on exe init without it
    from win32gui import GetWindowText, GetForegroundWindow
except ModuleNotFoundError:
    print_windows_warning()

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from src.DragButton import DragButton
from src.ResizeButton import ResizeButton
from src.Item import Item
from src.ModsContainer import PROJECT_ROOT


stash_cells_root = {
    "quad": 24,
    "normal": 12
}

windows_to_draw_frames = ["python", "poetis", "path of exile"]

pen_width = 3


# Checks if frames over items should be drawn, triggers hide if focus is not on the widget or game
class FocusCheck(QObject):
    def __init__(self, painter_widget):
        super(FocusCheck, self).__init__()
        self.painter_widget = painter_widget
        self.frames_draw_allowed = False
        self.last_window = None

    def run(self) -> None:
        if platform.system().lower() != 'windows':
            # skip focus check and allow draw anytime
            self.frames_draw_allowed = True
            return
        while True:
            window = GetWindowText(GetForegroundWindow())
            self.frames_draw_allowed = window.lower() in windows_to_draw_frames
            sleep(0.2)
            if window != self.last_window:
                self.painter_widget.update()
            self.last_window = window


class PainterWidget(QWidget):
    geometry_changed = pyqtSignal(QRect)

    def __init__(self, screen_geometry: QRect):
        super(PainterWidget, self).__init__()
        self.image_path = PROJECT_ROOT + "/img/"
        self.stash_type = "quad"
        self.colors = []
        self.stash_cells = stash_cells_root[self.stash_type]
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.screen_geometry = screen_geometry
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.move(250, 250)
        self.setFixedWidth(500)
        self.setFixedHeight(500)
        self.qp = QPainter()

        # Setup window focus checking thread
        self.focus_check = FocusCheck(self)
        self.focus_check_thread = QThread()
        self.focus_check.moveToThread(self.focus_check_thread)
        self.focus_check_thread.started.connect(self.focus_check.run)
        self.focus_check_thread.start()

        self.config_change_mode = False  # True when modifying net size and position
        self.drag_button = DragButton(self, False)
        load_styles(self.drag_button)
        self.drag_button.setFixedWidth(25)
        self.drag_button.setFixedHeight(25)
        icon = QIcon()
        icon.addPixmap(QPixmap(self.image_path + 'move.png'))
        self.drag_button.setIcon(icon)

        self.resize_button = ResizeButton(self)
        load_styles(self.resize_button)
        self.resize_button.setFixedWidth(25)
        self.resize_button.setFixedHeight(25)
        icon.addPixmap(QPixmap(self.image_path + 'resize.png'))
        self.resize_button.setIcon(icon)

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.drag_button, Qt.AlignTop)
        layout_buttons.addStretch()
        layout_buttons.addWidget(self.resize_button, Qt.AlignTop)
        layout_buttons.setAlignment(Qt.AlignBottom)
        layout_buttons.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(layout_buttons)
        self.drag_button.hide()
        self.resize_button.hide()
        self.setLayout(self.layout)

        self.number_of_mods_to_draw = 1
        self.items = []

    def paintEvent(self, r: QPaintEvent) -> None:
        self.stash_cells = stash_cells_root[self.stash_type]
        if self.config_change_mode:
            self.paint_config()
        elif self.focus_check.frames_draw_allowed:
            self.paint_items()

    def paint_config(self) -> None:
        self.qp.begin(self)
        self.qp.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.red)
        pen.setWidth(pen_width)
        pen.setColor(QColor("Red"))
        self.qp.setPen(pen)
        cell_width = int(self.width() / self.stash_cells)
        cell_height = int((self.height() - self.drag_button.height()) / self.stash_cells)
        for i in range(self.stash_cells):
            for j in range(self.stash_cells):
                self.qp.drawRect(i * cell_width, j * cell_height, cell_width, cell_height)

        self.qp.end()
        self.update()  # Need to refresh in case when net over items was visible

    def paint_items(self) -> None:
        for item in self.items:
            if len(item.mods_matched) > 0:
                self.qp.begin(self)
                self.qp.setRenderHint(QPainter.Antialiasing)
                pen = QPen(Qt.red)
                pen.setWidth(pen_width)
                pen.setColor(QColor("Red"))
                if len(item.explicits) == 6:
                    pen.setStyle(Qt.DotLine)  # Change pen style if there are no open affixes
                if self.colors:
                    pen.setColor(QColor(self.colors[len(item.mods_matched)-1]))
                self.qp.setPen(pen)
                self.draw_net(item)
                self.qp.end()

    def draw_net(self, item: Item) -> None:
        if len(item.mods_matched) < self.number_of_mods_to_draw:
            return
        cell_width = int((self.width()) / self.stash_cells)
        cell_height = int((self.height() - self.drag_button.height()) / self.stash_cells)
        self.qp.drawRect(item.x * cell_width + pen_width, item.y * cell_height + pen_width, item.width * cell_width -
                         pen_width, item.height * cell_height - pen_width)

    def show_hide_config(self) -> None:
        log_method_name()
        if self.config_change_mode:
            self.hide_modification_mode()
        else:
            self.show_modification_mode()

    def show_modification_mode(self) -> None:
        log_method_name()
        self.drag_button.show()
        self.resize_button.show()
        self.show()
        self.config_change_mode = True

    def hide_modification_mode(self) -> None:
        log_method_name()
        self.drag_button.hide()
        self.resize_button.hide()
        self.hide()
        self.config_change_mode = False

    def update_pos_size(self) -> None:
        self.geometry_changed.emit(QRect(self.geometry()))
