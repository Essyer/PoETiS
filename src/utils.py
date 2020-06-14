import logging
import sys
import xml.etree.ElementTree as ElementTree
from PyQt5.QtWidgets import *
from src.ModsContainer import DEFAULT_FILTER_PATH

LOGGING_APP_NAME = "log"
logger = logging.getLogger(LOGGING_APP_NAME)
last_logged_method_name = ""
last_logged_error = ""
styles_file = "styles/styles.css"
default_league_name = "Harvest"


def load_styles(object_instance: QWidget) -> None:
    with open(styles_file, "r") as fh:
        object_instance.setStyleSheet(fh.read())


def prepare_cfg(path: str) -> None:
    # all this does now is create the file with the root element
    root = ElementTree.Element("root")
    tree = ElementTree.ElementTree(root)
    tree.write(path)


def initialize_logging() -> None:
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("output.log", mode="w")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def log_method_name() -> None:
    return
    # try:
    #     class_name = str(sys._getframe(1).f_locals["self"].__class__.__name__)
    #     method_name = sys._getframe(1).f_code.co_name
    # except KeyError:
    #     class_name = "none"
    #     method_name = "EXCEEDED CALL STACK!"
    # except ValueError:
    #     class_name = " "
    #     method_name = "EXCEEDED CALL STACK!"
    #
    # global last_logged_method_name
    # if method_name != last_logged_method_name:
    #     logger.info(class_name + ": " + method_name)
    #     last_logged_method_name = method_name


def log_error(message) -> None:
    return
    # try:
    #     class_name = str(sys._getframe(1).f_locals["self"].__class__.__name__)
    #     method_name = sys._getframe(1).f_code.co_name
    # except KeyError:
    #     class_name = "none"
    #     method_name = "EXCEEDED CALL STACK!"
    # except ValueError:
    #     class_name = " "
    #     method_name = "EXCEEDED CALL STACK!"
    #
    # global last_logged_error
    # if message != last_logged_error:
    #     logger.error(class_name + ": " + method_name + "->" + message)
    #     last_logged_error = message


def xml_indent(elem: ElementTree.Element, level=0) -> None:
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xml_indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def print_windows_warning() -> None:
    print("[WARNING] Skipping Windows-only API calls.  Please install windows dependencies if you want this functionality.")
