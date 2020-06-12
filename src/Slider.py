from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Slider(QWidget):
    def __init__(self, slider_colors, slider_orientation=Qt.Horizontal):
        super(Slider, self).__init__()
        self._slider = QSlider(slider_orientation)
        self.on_value_changed_call(self.set_value)

        self.setLayout(QVBoxLayout())

        self._colorTicksWidget = QWidget(self)
        self._colorTicksWidget.setLayout(QHBoxLayout())
        self._colorTicksWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.value = 0

        self.layout().addWidget(self._colorTicksWidget)
        self.layout().addWidget(self._slider)
        self.slider_colors = slider_colors
        for index in range(5):
            button = QPushButton()
            button.setStyleSheet("background-color: " + self.slider_colors[index])
            button.setContentsMargins(0, 0, 0, 0)
            self._colorTicksWidget.layout().addWidget(button)

    def set_range(self, minimum: int, maximum: int) -> None:
        self._slider.setRange(minimum, maximum)

    def set_page_step(self, value: int) -> None:
        self._slider.setPageStep(value)

    def set_tick_interval(self, value: int) -> None:
        self._slider.setTickInterval(value)

    def set_tick_position(self, position: QSlider.TickPosition) -> None:
        self._slider.setTickPosition(position)

    def set_value(self, value: int) -> None:
        self.value = value
        self._slider.setValue(value)
        self._update_colors(value)

    def on_value_changed_call(self, function) -> None:
        self._slider.valueChanged.connect(function)

    def _update_colors(self, value: int) -> None:
        index = 0
        for children in self._colorTicksWidget.children():
            if isinstance(children, QPushButton):
                if index < value - 1:
                    children.setStyleSheet("background-color: gray")
                else:
                    children.setStyleSheet("background-color: " + self.slider_colors[index])
                index += 1
