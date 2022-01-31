import os
import pythoncom
import win32com.client as comclt
from time import sleep
from PyQt5.QtCore import pyqtSignal, QThread
from src.ModsContainer import items_categories_filter


class LogListener(QThread):
    entered_map = pyqtSignal()

    def __init__(self, settings_widget):
        super().__init__()
        self.settings_widget = settings_widget

    @staticmethod
    def follow(file, sleep_sec=0.1):
        """ Yield each line from a file as they are written.
        `sleep_sec` is the time to sleep after empty reads. """
        line = ''
        while True:
            tmp = file.readline()
            if tmp is not None:
                line += tmp
                if line.endswith("\n"):
                    yield line
                    line = ''
            elif sleep_sec:
                sleep(sleep_sec)

    def run(self) -> None:
        while True:
            file_path = self.settings_widget.poe_log_path
            if file_path and ".txt" in self.settings_widget.poe_log_path:
                with open(file_path, 'r', encoding="utf8") as file:
                    map_generated = False
                    file.seek(0, 2)
                    for line in self.follow(file):
                        # if "area \"labyrinth" in line.lower() and not map_generated:  # Aspirant's plaza for debugging
                        if "area \"map" in line.lower() and not map_generated:
                            map_generated = True
                        if map_generated and "you have entered" in line.lower():
                            map_generated = False
                            # sleep(1)
                            # print(line, end='')
                            self.entered_map.emit()
            sleep(0.1)


class FilterManager:
    def __init__(self, settings_widget):
        self.settings_widget = settings_widget
        pythoncom.CoInitialize()
        self.wsh = comclt.Dispatch("WScript.Shell")
        self.filter_string = ""

    def reload_filter(self, chaos_counters):
        # print("reload filter " + str(chaos_counters))
        if self.settings_widget.poe_filter_name:
            self.generate_filters(chaos_counters)
            self.modify_filter()
            self.wsh.AppActivate("path of exile")
            reload_command = "/itemfilter " + self.settings_widget.poe_filter_name.rstrip()
            self.wsh.SendKeys("{ENTER}")
            self.wsh.SendKeys(reload_command)
            self.wsh.SendKeys("{ENTER}")

    def modify_filter(self):
        if self.settings_widget.poe_filter_path:
            # qwe = self.settings_widget.poe_filter_path + 'qwe'
            # with open(qwe, 'w+') as qw:
            #     qw.write("test123")

            dummy_file = self.settings_widget.poe_filter_path + 'bak'
            is_skipped = False
            # Open original file in read only mode and dummy file in write mode
            with open(self.settings_widget.poe_filter_path, 'r') as read_obj, open(dummy_file, 'w+') as write_obj:
                # Line by line copy data from original file to dummy file
                should_delete = False
                deleted_end = False
                filter_modified = False
                for line in read_obj:
                    # if current line matches the given condition then skip that line
                    if "#poetis start" in line.lower():
                        should_delete = True
                    elif "#poetis end" in line.lower():
                        should_delete = False
                        deleted_end = True
                    if deleted_end and not filter_modified or (not should_delete and not filter_modified):
                        write_obj.write(self.filter_string)
                        filter_modified = True

                    if not should_delete:
                        # Need to cleanup end string
                        # If I try to save my filter changes with last character as a new line,
                        # all changes disappear if it is an online filter
                        line = line.replace("#poetis end", "")
                        write_obj.write(line)
                    else:
                        is_skipped = True
            # If any line is skipped then rename dummy file as original file
            if is_skipped or filter_modified:
                os.remove(self.settings_widget.poe_filter_path)
                os.rename(dummy_file, self.settings_widget.poe_filter_path)
            else:
                os.remove(dummy_file)

    def generate_filters(self, chaos_counters):
        max_chaos_sets = self.settings_widget.maximum_chaos_sets
        self.filter_string = "#poetis start\n"
        for category in chaos_counters:
            if chaos_counters[category][0] + chaos_counters[category][1] < max_chaos_sets:
                if chaos_counters[category][0] < max_chaos_sets - 1:
                    self.filter_string += self.generate_category(category, "regal")
                if chaos_counters[category][1] < max_chaos_sets:
                    self.filter_string += self.generate_category(category, "chaos")
        self.filter_string += "#poetis end"  # No new line so it can work with online filters

    def generate_category(self, cat, cr, second_weapon=False) -> str:
        category = items_categories_filter[cat]
        result = "Show\n"
        result += "\tHasInfluence None\n"
        result += "\tRarity Rare\n"
        if not self.settings_widget.allow_identified:
            result += "\tIdentified False\n"
        if cr == "chaos":
            result += "\tItemLevel >= 60\n" + "\tItemLevel <= 74\n"
        else:
            result += "\tItemLevel > 75\n"
        if category == "Body Armours":
            result += "\tSockets <= 5\n"

        base_type = "\tClass "
        if category == "weapon":
            if not second_weapon:
                base_type += "\"Daggers\" \"One Hand Axes\" \"One Hand Maces\" \"One Hand Swords\" \"Rune Daggers\" " \
                             "\"Sceptres\" \"Thrusting One Hand Swords\" \"Wands\"\n"
                base_type += "\tWidth <= 1\n\tHeight <= 3\n"
            else:
                base_type += "\"Two Hand Swords\" \"Two Hand Axes\" \"Two Hand Maces\" \"Staves\" \"Warstaves\" " \
                             "\"Bows\"\n "
                base_type += "\tWidth <= 2\n\tHeight <= 3\n"
                base_type += "\tSockets <= 5\n"
        else:
            base_type += category + "\n"

        result += base_type

        bg_color = "\tSetBackgroundColor "
        if category == "Body Armours":
            bg_color += "221 0 255 255"
        elif category == "Helmets":
            bg_color += "248 255 4 255"
        elif category == "Gloves":
            bg_color += "4 255 0 255"
        elif category == "Boots":
            bg_color += "0 24 255 255"
        elif category == "weapon":
            bg_color += "0 220 255 255"
        elif category in ["Rings", "Amulets", "Belts"]:
            bg_color += "255 3 3 255"

        result += bg_color + "\n"

        if category == "weapon" and not second_weapon:
            result += self.generate_category(cat, cr, True)
        return result
