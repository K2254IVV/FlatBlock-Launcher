import sys
import os
import webbrowser
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
                            QComboBox, QSpacerItem, QSizePolicy, QProgressBar, 
                            QPushButton, QApplication, QMainWindow, QFrame, 
                            QStackedWidget, QListWidget, QListWidgetItem, QMessageBox,
                            QTabWidget, QGroupBox, QCheckBox)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor, QPainter

from minecraft_launcher_lib.utils import get_minecraft_directory, get_version_list
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.command import get_minecraft_command

from random_username.generate import generate_username
from uuid import uuid1
from subprocess import Popen

# Константы
VERSION = "1.0.01"
APP_NAME = "FlatBlock"
MINECRAFT_DIR = get_minecraft_directory().replace('minecraft', APP_NAME)

class FlatStyle:
    @staticmethod
    def apply(app):
        app.setStyle("Fusion")
        palette = app.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        palette.setColor(palette.WindowText, Qt.black)
        palette.setColor(palette.Base, Qt.white)
        palette.setColor(palette.AlternateBase, QColor(240, 240, 240))
        palette.setColor(palette.ToolTipBase, Qt.white)
        palette.setColor(palette.ToolTipText, Qt.black)
        palette.setColor(palette.Text, Qt.black)
        palette.setColor(palette.Button, QColor(230, 230, 230))
        palette.setColor(palette.ButtonText, Qt.black)
        palette.setColor(palette.BrightText, Qt.red)
        palette.setColor(palette.Highlight, QColor(42, 130, 218))
        palette.setColor(palette.HighlightedText, Qt.white)
        app.setPalette(palette)

class LaunchThread(QThread):
    # ... (остальной код класса LaunchThread без изменений)
    # (вставьте сюда код класса LaunchThread из предыдущей версии)

class NewsTab(QWidget):
    # ... (остальной код класса NewsTab без изменений)

class SettingsTab(QWidget):
    # ... (остальной код класса SettingsTab без изменений)

class PlayTab(QWidget):
    # ... (остальной код класса PlayTab без изменений)

class MainWindow(QMainWindow):
    # ... (остальной код класса MainWindow без изменений)

def create_placeholder_icon(color, symbol):
    """Создает иконку с помощью Qt (без Pillow)"""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setBrush(QColor(*color))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, 32, 32, 5, 5)
    
    painter.setPen(Qt.white)
    painter.setFont(QFont("Arial", 14))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, symbol)
    painter.end()
    
    return pixmap

def create_placeholder_assets():
    """Создает placeholder-ресурсы с помощью Qt (если нет Pillow)"""
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Цвета и символы для иконок
    icons = {
        "play_icon.png": ("▶", (42, 130, 218)),
        "news_icon.png": ("📰", (218, 130, 42)),
        "settings_icon.png": ("⚙", (130, 42, 218)),
        "icon.png": ("FB", (73, 109, 137))
    }
    
    for filename, (symbol, color) in icons.items():
        if not os.path.exists(f"assets/{filename}"):
            pixmap = create_placeholder_icon(color, symbol)
            pixmap.save(f"assets/{filename}")

if __name__ == '__main__':
    # Настройка приложения
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    FlatStyle.apply(app)
    
    # Создание placeholder-ресурсов (теперь без зависимости от Pillow)
    create_placeholder_assets()
    
    # Создание и отображение главного окна
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
