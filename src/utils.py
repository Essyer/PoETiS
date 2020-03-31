import logging
import sys
import xml.etree.ElementTree as ElementTree
from xml.dom import minidom

LOGGING_APP_NAME = 'log'
logger = logging.getLogger(LOGGING_APP_NAME)
last_logged_method_name = ''
last_logged_error = ''
CONFIG_PATH = "config.xml"

def prepare_cfg(path):

    root = ElementTree.Element("root")
    ElementTree.SubElement(root, 'account_id')
    ElementTree.SubElement(root, 'stash_name')
    ElementTree.SubElement(root, 'stash_type')
    ElementTree.SubElement(root, 'multiple_query')
    ElementTree.SubElement(root, 'league')
    data_file = ElementTree.SubElement(root, 'data_file')
    data_file.text = 'data.xml'
    color1 = ElementTree.SubElement(root, 't1_color')
    color2 = ElementTree.SubElement(root, 't2_color')
    color3 = ElementTree.SubElement(root, 't3_color')
    color4 = ElementTree.SubElement(root, 't4_color')
    color5 = ElementTree.SubElement(root, 't5_color')
    color1.text = 'true'
    color2.text = 'true'
    color3.text = 'true'
    color4.text = 'true'
    color5.text = 'true'

    data = minidom.parseString("".join(ElementTree.tostring(root).decode('utf-8').
                                       split())).toprettyxml(indent="  ")
    with open(path, 'w') as file:
        file.write(data)

def initialize_logging():
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('output.log', mode='w')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def log_method_name():
    try:
        class_name = str(sys._getframe(1).f_locals['self'].__class__.__name__)
        method_name = sys._getframe(1).f_code.co_name
    except KeyError:
        class_name = 'none'
        method_name = 'EXCEEDED CALL STACK!'
    except ValueError:
        class_name = ' '
        method_name = 'EXCEEDED CALL STACK!'

    global last_logged_method_name
    if method_name != last_logged_method_name:
        logger.info(class_name + ': ' + method_name)
        last_logged_method_name = method_name


def log_error(message):
    try:
        class_name = str(sys._getframe(1).f_locals['self'].__class__.__name__)
        method_name = sys._getframe(1).f_code.co_name
    except KeyError:
        class_name = 'none'
        method_name = 'EXCEEDED CALL STACK!'
    except ValueError:
        class_name = ' '
        method_name = 'EXCEEDED CALL STACK!'

    global last_logged_error
    if method_name != last_logged_error:
        logger.error(class_name + ': ' + method_name + '->' + message)
        last_logged_error = method_name
