

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QSlider,
    QGroupBox, QCheckBox, QScrollArea, QComboBox
)
from PySide6.QtCore import Qt
import subprocess
import json
import os
from translations import MESSAGE
from translations import TEXT



# Ścieżka dla katalogu ustawień
# Path for the settings directory
SETTINGS_FOLDER = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
SETTINGS_FOLDER = os.path.join(SETTINGS_FOLDER, "lumen")

# Ścieżka dla pliku ustawień
# Path for the settings file
SETTINGS_FILE = os.path.join(SETTINGS_FOLDER, "settings.json")




# Funkcja do stworzenia katalogu jeśli nie istnieje
# Function to create directory if it doesn't exist
def create_settings_folder(lang):
    try:
        os.makedirs(SETTINGS_FOLDER, exist_ok=True)

    except OSError as e:
        # Wświetlanie błędy w przypadku niepowodzenia
        print(f"[ERROR] {MESSAGE[lang]['settings_folder_creation_error']}")
        return False
    
    return True


# Funkcja do wczytywania ustawień z pliku
# Function for loading settings from a file
def load_settings(lang):
    if not create_settings_folder(lang):
        return {}
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[ERROR] {MESSAGE[lang]['load_settings_error']}")
        return {}




# Funkcja do zapisywania ustawień do pliku
# Function to save settings to a file
def save_settings(data, lang):
    if not create_settings_folder(lang):
        print(f"[ERROR] {MESSAGE[lang]['save_settings_error1']}")
        return {}
    try:
        temp_file = SETTINGS_FILE + ".temp"
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, SETTINGS_FILE)

    except IOError as e:
        print(f"[ERROR] {MESSAGE[lang]['save_settings_error2']}")



# Funkcja do sortowania monitorów
# Function to sort monitors
def sort_monitors(monitors):
    return sorted(monitors, key=lambda m: m.active, reverse=True)







# Klasa tworząca okno programu
# Class that creates a program window
class LumenWindow(QMainWindow):
    def __init__(self, monitors):
        super().__init__()

        self.settings = load_settings('en') 
        self.current_lang = self.settings.get("_language", 'en')


        self.setWindowTitle("Lumen")
        self.setGeometry(100, 100, 600, 400)

        self.monitors = sort_monitors(monitors)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        scroll_area.setWidget(container)



        self.lang_combo = QComboBox()
        self.lang_combo.addItem(TEXT['en']['language_en'], 'en')
        self.lang_combo.addItem(TEXT['pl']['language_pl'], 'pl')
        self.lang_combo.currentIndexChanged.connect(self.switch_language)
        self.main_layout.addWidget(self.lang_combo)

        index = self.lang_combo.findData(self.current_lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)




        self.widgets = []      


        # Checkbox "Pokaż nieaktywne porty"
        # Checkbox "Show inactive ports"
        self.show_inactive_checkbox = QCheckBox(f"{TEXT[self.current_lang]['show_inactive_ports']}")
        self.show_inactive_checkbox.stateChanged.connect(self.update_visible_ports)
        self.main_layout.addWidget(self.show_inactive_checkbox)


        for mon in self.monitors:
            self.create_monitor_group(mon)

        self.main_layout.addStretch()
        self.update_visible_ports()


        # Wczytanie zapisanych ustawień
        # Loading saved settings
        self.settings = load_settings(self.current_lang)
        for w in self.widgets:
            mon = w["monitor"]
            if mon.name in self.settings:
                s = self.settings[mon.name]
                
                w["alias_edit"].setPlaceholderText(TEXT[self.current_lang]['enter_custom_name'])
                alias_value = s.get("alias", "")
                
                w["alias_edit"].setText(alias_value)
                w["slider_software"].setValue(s.get("software_brightness", mon.software_brightness))
                w["slider_hardware"].setValue(s.get("hardware_brightness", mon.hardware_brightness))
                w["remember_checkbox"].setChecked(s.get("remember", True))

                if mon.active:
                    self.change_software_brightness(mon, w["slider_software"].value())
                    self.change_hardware_brightness(mon, w["slider_hardware"].value())




    def create_monitor_group(self, mon):
        group_box = QGroupBox(mon.display_name())
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)

        status_label = QLabel(f"Status: {f"{TEXT[self.current_lang]['active']}" if mon.active else f"{TEXT[self.current_lang]['inactive']}" }")
        group_layout.addWidget(status_label)

        alias_edit = QLineEdit()
        alias_edit.setPlaceholderText(f"{TEXT[self.current_lang]['enter_custom_name']}")
        group_layout.addWidget(alias_edit)

        # Jasność programowa
        # Software brightness
        software_label = QLabel(TEXT[self.current_lang]['software_brightness'])
        group_layout.addWidget(software_label)
        slider_software = QSlider(Qt.Horizontal)
        slider_software.setMinimum(5)
        slider_software.setMaximum(100)
        slider_software.setValue(mon.software_brightness)
        group_layout.addWidget(slider_software)
        slider_software_label = QLabel(f"{TEXT[self.current_lang]['current_value']}: {mon.software_brightness}%")
        group_layout.addWidget(slider_software_label)

        slider_software.valueChanged.connect(
            lambda value, mon=mon, lbl=slider_software_label: (
                self.change_software_brightness(mon, value),
                lbl.setText(f"{TEXT[self.current_lang]['current_value']}: {value}%")
            )
        )

        # Jasność sprzętowa
        # Hardware brightness
        hardware_label = QLabel(TEXT[self.current_lang]['hardware_brightness'])
        group_layout.addWidget(hardware_label)
        slider_hardware = QSlider(Qt.Horizontal)
        slider_hardware.setMinimum(0)
        slider_hardware.setMaximum(100)
        slider_hardware.setValue(mon.hardware_brightness)
        group_layout.addWidget(slider_hardware)

        slider_hardware_label = QLabel(f"{TEXT[self.current_lang]['current_value']}: {mon.hardware_brightness}%")
        group_layout.addWidget(slider_hardware_label)

        slider_hardware.valueChanged.connect(
            lambda value, mon=mon, lbl=slider_hardware_label: (
                self.change_hardware_brightness(mon, value),
                lbl.setText(f"{TEXT[self.current_lang]['current_value']}: {value}%")
            )
        )

        # Checkbox "Remember settings"
        remember_checkbox = QCheckBox(f"{TEXT[self.current_lang]['remember_settings']}")
        remember_checkbox.setChecked(False)
        group_layout.addWidget(remember_checkbox)

        self.main_layout.addWidget(group_box)

        self.widgets.append({
            "monitor": mon,
            "group_box": group_box,
            "status_label": status_label,
            "alias_edit": alias_edit,
            "software_label": software_label,
            "slider_software": slider_software,
            "slider_software_label": slider_software_label,
            "hardware_label": hardware_label,
            "slider_hardware": slider_hardware,
            "slider_hardware_label": slider_hardware_label,
            "remember_checkbox": remember_checkbox,
        })




    def update_visible_ports(self):
        show_inactive = self.show_inactive_checkbox.isChecked()
        for w in self.widgets:
            mon = w["monitor"]
            w["group_box"].setVisible(mon.active or show_inactive)
            w["slider_software"].setEnabled(mon.active)
            w["slider_hardware"].setEnabled(mon.active)



    def change_software_brightness(self, mon, value):
        mon.software_brightness = value
        brightness = value / 100
        try:
            subprocess.run(
                ["xrandr", "--output", mon.name, "--brightness", str(brightness)],
                check=True
            )
        except Exception as e:
            print(f"[ERROR] {MESSAGE[self.current_lang]['software_brightness_change']} {mon.name}: {e}")



    def change_hardware_brightness(self, mon, value):
        mon.hardware_brightness = value
        try:
            result = subprocess.run(
                ["ddcutil", "setvcp", "10", str(value)],
                capture_output=True,
                text=True
            )
            if "DDCRC_NULL_RESPONSE" in result.stderr:
                print(f"[INFO] {MESSAGE[self.current_lang]['ddc_response']} {mon.name}")
            elif result.returncode != 0:
                print(f"[ERROR] {MESSAGE[self.current_lang]['hardware_brightness_error']} {mon.name}: {result.stderr}")
        except Exception as e:
            print(f"[EXCEPTION] {MESSAGE[self.current_lang]['failed_hardware']} {mon.name}: {e}")




    def closeEvent(self, event):
        data_to_save = {}
        for w in self.widgets:
            mon = w["monitor"]
            remember = w["remember_checkbox"].isChecked()
            if remember:
                alias_text = w["alias_edit"].text()
                data_to_save[mon.name] = {
                    "alias": alias_text,
                    "software_brightness": w["slider_software"].value(),
                    "hardware_brightness": w["slider_hardware"].value(),
                    "remember": remember
                }
        data_to_save["_language"] = self.current_lang
        save_settings(data_to_save, self.current_lang)
        super().closeEvent(event)





    def switch_language(self, index):
        self.current_lang = self.lang_combo.itemData(index)
        self.update_ui_texts()
        # self.create_monitor_group()


    def update_ui_texts(self):
    
        # Aktualizacja tekstu w ComboBox
        #Updating text in ComboBox
        self.lang_combo.setItemText(self.lang_combo.findData('en'), TEXT[self.current_lang]['language_en'])
        self.lang_combo.setItemText(self.lang_combo.findData('pl'), TEXT[self.current_lang]['language_pl'])

        # Aktualizacja tekstu checkboxa "Pokaż nieaktywne porty"
        # Update the "Show inactive ports" checkbox text
        self.show_inactive_checkbox.setText(TEXT[self.current_lang]['show_inactive_ports'])

        # Aktualizacja tekstów w dynamicznie tworzonych widżetach
        # Updating texts in dynamically created widgets
        for w in self.widgets:
            mon = w["monitor"]
            w["group_box"].setTitle(mon.display_name())
            
            # Status
            w["status_label"].setText(f"Status: {TEXT[self.current_lang]['active']}" if mon.active else f"Status: {TEXT[self.current_lang]['inactive']}")
            
            # Alias
            w["alias_edit"].setPlaceholderText(TEXT[self.current_lang]['enter_custom_name'])
            
            # Slider labels
            w["software_label"].setText(TEXT[self.current_lang]['software_brightness'])
            w["slider_software_label"].setText(f"{TEXT[self.current_lang]['current_value']}: {w['slider_software'].value()}%")
            w["hardware_label"].setText(TEXT[self.current_lang]['hardware_brightness'])
            w["slider_hardware_label"].setText(f"{TEXT[self.current_lang]['current_value']}: {w['slider_hardware'].value()}%")
                        
            # Checkbox
            w["remember_checkbox"].setText(TEXT[self.current_lang]['remember_settings'])
