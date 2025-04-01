import sys
import os
import webbrowser
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt, QTimer
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
                            QComboBox, QSpacerItem, QSizePolicy, QProgressBar, 
                            QPushButton, QApplication, QMainWindow, QFrame, 
                            QStackedWidget, QListWidget, QListWidgetItem, QMessageBox,
                            QTabWidget, QGroupBox, QCheckBox)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor

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
    launch_setup_signal = pyqtSignal(str, str, int, bool)
    progress_update_signal = pyqtSignal(int, int, str)
    state_update_signal = pyqtSignal(bool)
    launch_finished = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.launch_setup_signal.connect(self.launch_setup)
        self.version_id = ''
        self.username = ''
        self.ram_amount = 2048
        self.demo_mode = False
        self.progress = 0
        self.progress_max = 0
        self.progress_label = ''
        self.process = None

    def launch_setup(self, version_id, username, ram_amount, demo_mode):
        self.version_id = version_id
        self.username = username
        self.ram_amount = ram_amount
        self.demo_mode = demo_mode
    
    def update_progress_label(self, value):
        self.progress_label = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)
    
    def update_progress(self, value):
        self.progress = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)
    
    def update_progress_max(self, value):
        self.progress_max = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def run(self):
        self.state_update_signal.emit(True)

        try:
            # Установка версии, если требуется
            self.update_progress_label("Checking version...")
            if not os.path.exists(os.path.join(MINECRAFT_DIR, "versions", self.version_id)):
                install_minecraft_version(
                    versionid=self.version_id, 
                    minecraft_directory=MINECRAFT_DIR, 
                    callback={
                        'setStatus': self.update_progress_label,
                        'setProgress': self.update_progress,
                        'setMax': self.update_progress_max
                    }
                )

            if not self.username:
                self.username = generate_username()[0]
            
            options = {
                'username': self.username,
                'uuid': str(uuid1()),
                'token': '',
                'jvmArguments': [f'-Xmx{self.ram_amount}M', f'-Xms{self.ram_amount//2}M'],
                'demo': self.demo_mode
            }

            command = get_minecraft_command(
                version=self.version_id,
                minecraft_directory=MINECRAFT_DIR,
                options=options
            )
            
            self.process = Popen(command)
            self.process.wait()
            self.launch_finished.emit(self.process.returncode)
            
        except Exception as e:
            print(f"Error during launch: {e}")
        finally:
            self.state_update_signal.emit(False)

class NewsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Minecraft News")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Новости
        news_items = [
            {
                "title": "Minecraft 1.20.4 Released",
                "date": "2023-12-07",
                "content": "The latest update includes bug fixes and performance improvements."
            },
            {
                "title": "Minecraft Live 2023",
                "date": "2023-10-15",
                "content": "Watch the annual Minecraft event to learn about upcoming features!"
            }
        ]
        
        for item in news_items:
            group = QGroupBox(f"{item['title']} - {item['date']}")
            group.setStyleSheet("QGroupBox { border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }")
            group_layout = QVBoxLayout()
            content = QLabel(item["content"])
            content.setWordWrap(True)
            group_layout.addWidget(content)
            
            # Кнопка "Подробнее" (заглушка)
            if item["title"] == "Minecraft Live 2023":
                btn = QPushButton("Watch Now")
                btn.setStyleSheet("max-width: 100px;")
                btn.clicked.connect(lambda: webbrowser.open("https://www.minecraft.net/en-us/live"))
                group_layout.addWidget(btn, 0, Qt.AlignRight)
            
            group.setLayout(group_layout)
            layout.addWidget(group)
        
        layout.addStretch()

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Настройки запуска
        launch_group = QGroupBox("Launch Settings")
        launch_layout = QVBoxLayout()
        
        # RAM
        ram_layout = QHBoxLayout()
        ram_label = QLabel("RAM Allocation (MB):")
        self.ram_combo = QComboBox()
        self.ram_combo.addItems(["1024", "2048", "3072", "4096", "5120", "6144", "7168", "8192"])
        self.ram_combo.setCurrentIndex(1)  # 2048 по умолчанию
        
        ram_layout.addWidget(ram_label)
        ram_layout.addWidget(self.ram_combo)
        ram_layout.addStretch()
        launch_layout.addLayout(ram_layout)
        
        # Демо-режим
        self.demo_check = QCheckBox("Enable demo mode")
        launch_layout.addWidget(self.demo_check)
        
        launch_group.setLayout(launch_layout)
        layout.addWidget(launch_group)
        
        # О программе
        about_group = QGroupBox(f"About {APP_NAME}")
        about_layout = QVBoxLayout()
        
        about_text = QLabel(f"""
            <b>{APP_NAME} {VERSION}</b><br><br>
            A simple Minecraft launcher built with Python and Qt.<br><br>
            Minecraft is a trademark of Mojang Studios.<br>
            This launcher is not affiliated with Mojang or Microsoft.
        """)
        about_text.setOpenExternalLinks(True)
        about_text.setTextFormat(Qt.RichText)
        about_text.setWordWrap(True)
        
        about_layout.addWidget(about_text)
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        layout.addStretch()

class PlayTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Заголовок
        title = QLabel("Play Minecraft")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Имя пользователя
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter your username")
        self.username.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        layout.addWidget(self.username)
        
        # Выбор версии
        version_layout = QHBoxLayout()
        version_label = QLabel("Version:")
        self.version_select = QComboBox()
        self.version_select.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        
        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_select)
        layout.addLayout(version_layout)
        
        # Прогресс
        self.start_progress_label = QLabel()
        self.start_progress_label.setVisible(False)
        self.start_progress_label.setStyleSheet("color: #555;")
        layout.addWidget(self.start_progress_label)
        
        self.start_progress = QProgressBar()
        self.start_progress.setVisible(False)
        self.start_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
            }
        """)
        layout.addWidget(self.start_progress)
        
        # Кнопка запуска
        self.start_button = QPushButton("LAUNCH MINECRAFT")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1a6fc7;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_button.clicked.connect(self.launch_game)
        layout.addWidget(self.start_button)
        
        layout.addStretch()
    
    def launch_game(self):
        ram_amount = int(self.parent.settings_tab.ram_combo.currentText())
        demo_mode = self.parent.settings_tab.demo_check.isChecked()
        
        if not self.username.text().strip():
            QMessageBox.warning(self, "Username Required", "Please enter a username to play Minecraft.")
            return
            
        self.parent.launch_thread.launch_setup_signal.emit(
            self.version_select.currentText(),
            self.username.text(),
            ram_amount,
            demo_mode
        )
        self.parent.launch_thread.start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {VERSION}")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.resize(800, 500)
        self.setMinimumSize(600, 400)
        
        # Создаем папку для Minecraft, если ее нет
        os.makedirs(MINECRAFT_DIR, exist_ok=True)
        
        # Инициализация UI
        self.init_ui()
        
        # Поток для запуска Minecraft
        self.launch_thread = LaunchThread()
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress)
        self.launch_thread.launch_finished.connect(self.handle_launch_finished)
        
        # Загрузка версий Minecraft
        self.load_versions()
        
        # Установка имени пользователя по умолчанию
        self.play_tab.username.setText(generate_username()[0])
    
    def init_ui(self):
        # Создаем вкладки
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { 
                padding: 8px 12px; 
                background: #f0f0f0; 
                border: 1px solid #ddd; 
                border-bottom: none; 
                border-top-left-radius: 4px; 
                border-top-right-radius: 4px; 
            }
            QTabBar::tab:selected { 
                background: white; 
                border-bottom: 1px solid white; 
            }
        """)
        
        # Вкладка Play
        self.play_tab = PlayTab(self)
        self.tabs.addTab(self.play_tab, QIcon("assets/play_icon.png"), "Play")
        
        # Вкладка News
        self.news_tab = NewsTab()
        self.tabs.addTab(self.news_tab, QIcon("assets/news_icon.png"), "News")
        
        # Вкладка Settings
        self.settings_tab = SettingsTab()
        self.tabs.addTab(self.settings_tab, QIcon("assets/settings_icon.png"), "Settings")
        
        # Устанавливаем центральный виджет
        self.setCentralWidget(self.tabs)
    
    def load_versions(self):
        try:
            self.play_tab.version_select.clear()
            versions = get_version_list()
            release_versions = [v for v in versions if v["type"] == "release"]
            
            # Сортируем версии по дате выхода (новые сначала)
            release_versions.sort(key=lambda x: x["releaseTime"], reverse=True)
            
            for version in release_versions[:20]:  # Показываем только 20 последних релизов
                self.play_tab.version_select.addItem(version["id"])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load Minecraft versions: {e}")
    
    def state_update(self, value):
        self.play_tab.start_button.setDisabled(value)
        self.play_tab.start_progress_label.setVisible(value)
        self.play_tab.start_progress.setVisible(value)
        self.tabs.setTabEnabled(1, not value)  # News tab
        self.tabs.setTabEnabled(2, not value)  # Settings tab
    
    def update_progress(self, progress, max_progress, label):
        self.play_tab.start_progress.setValue(progress)
        self.play_tab.start_progress.setMaximum(max_progress)
        self.play_tab.start_progress_label.setText(label)
    
    def handle_launch_finished(self, return_code):
        if return_code != 0:
            QMessageBox.warning(self, "Launch Failed", 
                              "Minecraft exited with an error. Please check the logs for more information.")
    
    def closeEvent(self, event):
        if self.launch_thread.isRunning():
            reply = QMessageBox.question(
                self, 'Minecraft is running',
                "Minecraft is still running. Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def create_placeholder_assets():
    """Создает placeholder-ресурсы, если они отсутствуют"""
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Иконка приложения
    if not os.path.exists("assets/icon.png"):
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (64, 64), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
        img.save("assets/icon.png")
    
    # Иконки для вкладок
    icons = {
        "play_icon.png": ("▶", (42, 130, 218)),
        "news_icon.png": ("📰", (218, 130, 42)),
        "settings_icon.png": ("⚙", (130, 42, 218))
    }
    
    for filename, (symbol, color) in icons.items():
        if not os.path.exists(f"assets/{filename}"):
            img = Image.new('RGB', (32, 32), color=color)
            d = ImageDraw.Draw(img)
            d.text((8, 8), symbol, fill=(255, 255, 255))
            img.save(f"assets/{filename}")

if __name__ == '__main__':
    # Создаем placeholder-ресурсы
    try:
        from PIL import Image, ImageDraw, ImageFont
        create_placeholder_assets()
    except ImportError:
        print("Pillow not installed, placeholder assets won't be created")

    # Настройка приложения
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    FlatStyle.apply(app)
    
    # Создание и отображение главного окна
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
