import logging
import sys
import xml.etree.ElementTree as ElementTree
from PyQt5.QtWidgets import *

LOGGING_APP_NAME = "log"
logger = logging.getLogger(LOGGING_APP_NAME)
last_logged_method_name = ""
last_logged_error = ""
styles_file = "src/styles.css"
default_league_name = "Delirium"


def load_styles(object_instance: QWidget) -> None:
    with open(styles_file, "r") as fh:
        object_instance.setStyleSheet(fh.read())


def prepare_cfg(path: str) -> None:
    root = ElementTree.Element("root")
    ElementTree.SubElement(root, "account_name")
    ElementTree.SubElement(root, "stash_name")
    ElementTree.SubElement(root, "stash_type")
    ElementTree.SubElement(root, "league")
    ElementTree.SubElement(root, "league_base_name").text = default_league_name
    ElementTree.SubElement(root, "session_id")
    ElementTree.SubElement(root, "data_file").text = "data.xml"

    ElementTree.SubElement(root, "slider_value").text = "3"
    ElementTree.SubElement(root, "t1_color").text = "true"
    ElementTree.SubElement(root, "t2_color").text = "true"
    ElementTree.SubElement(root, "t3_color").text = "true"
    ElementTree.SubElement(root, "t4_color").text = "true"
    ElementTree.SubElement(root, "t5_color").text = "true"

    ElementTree.SubElement(root, "main_widget_y").text = "200"
    ElementTree.SubElement(root, "painter_x").text = "250"
    ElementTree.SubElement(root, "painter_y").text = "250"
    ElementTree.SubElement(root, "painter_w").text = "500"
    ElementTree.SubElement(root, "painter_h").text = "500"

    xml_indent(root)
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
