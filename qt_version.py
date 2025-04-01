import sys
import os
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt, QTimer
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
                            QComboBox, QSpacerItem, QSizePolicy, QProgressBar, 
                            QPushButton, QApplication, QMainWindow, QFrame, 
                            QStackedWidget, QListWidget, QListWidgetItem, QMessageBox)
from PyQt5.QtGui import QPixmap, QIcon, QFont

from minecraft_launcher_lib.utils import get_minecraft_directory, get_version_list
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.command import get_minecraft_command

from random_username.generate import generate_username
from uuid import uuid1
from subprocess import Popen

class FlatStyle:
    @staticmethod
    def apply(app):
        app.setStyle("Fusion")
        palette = app.palette()
        palette.setColor(palette.Window, Qt.white)
        palette.setColor(palette.WindowText, Qt.black)
        palette.setColor(palette.Base, Qt.white)
        palette.setColor(palette.AlternateBase, Qt.lightGray)
        palette.setColor(palette.ToolTipBase, Qt.white)
        palette.setColor(palette.ToolTipText, Qt.black)
        palette.setColor(palette.Text, Qt.black)
        palette.setColor(palette.Button, Qt.lightGray)
        palette.setColor(palette.ButtonText, Qt.black)
        palette.setColor(palette.BrightText, Qt.red)
        palette.setColor(palette.Highlight, Qt.darkCyan)
        palette.setColor(palette.HighlightedText, Qt.white)
        app.setPalette(palette)

class LaunchThread(QThread):
    launch_setup_signal = pyqtSignal(str, str, int)
    progress_update_signal = pyqtSignal(int, int, str)
    state_update_signal = pyqtSignal(bool)
    launch_finished = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.launch_setup_signal.connect(self.launch_setup)
        self.version_id = ''
        self.username = ''
        self.ram_amount = 2048
        self.progress = 0
        self.progress_max = 0
        self.progress_label = ''
        self.process = None

    def launch_setup(self, version_id, username, ram_amount):
        self.version_id = version_id
        self.username = username
        self.ram_amount = ram_amount
    
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
            install_minecraft_version(
                versionid=self.version_id, 
                minecraft_directory=minecraft_directory, 
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
                'jvmArguments': [f'-Xmx{self.ram_amount}M', f'-Xms{self.ram_amount//2}M']
            }

            command = get_minecraft_command(
                version=self.version_id,
                minecraft_directory=minecraft_directory,
                options=options
            )
            
            self.process = Popen(command)
            self.process.wait()
            self.launch_finished.emit(self.process.returncode)
            
        except Exception as e:
            print(f"Error during launch: {e}")
        finally:
            self.state_update_signal.emit(False)

class NewsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Latest News")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Placeholder for news content
        news_content = QLabel("Minecraft 1.20 update is now available!\n\n"
                             "New features include:\n"
                             "- Cherry blossom biome\n"
                             "- Archaeology system\n"
                             "- New mob: Sniffer")
        news_content.setWordWrap(True)
        layout.addWidget(news_content)
        
        layout.addStretch()

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Settings")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # RAM Settings
        ram_layout = QHBoxLayout()
        ram_label = QLabel("RAM Allocation (MB):")
        self.ram_slider = QComboBox()
        self.ram_slider.addItems(["1024", "2048", "3072", "4096", "5120"])
        self.ram_slider.setCurrentIndex(1)  # Default to 2048MB
        
        ram_layout.addWidget(ram_label)
        ram_layout.addWidget(self.ram_slider)
        ram_layout.addStretch()
        layout.addLayout(ram_layout)
        
        # Minecraft directory
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Minecraft Directory:")
        self.dir_display = QLabel(minecraft_directory)
        self.dir_display.setWordWrap(True)
        
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_display)
        layout.addLayout(dir_layout)
        
        layout.addStretch()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlatLauncher 1.0")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.resize(800, 500)
        self.setMinimumSize(600, 400)
        
        # Create main widgets
        self.create_sidebar()
        self.create_main_content()
        
        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_layout.addWidget(self.sidebar, 1)
        main_layout.addWidget(self.main_content, 3)
        
        self.setCentralWidget(main_widget)
        
        # Launch thread
        self.launch_thread = LaunchThread()
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress)
        self.launch_thread.launch_finished.connect(self.handle_launch_finished)
        
        # Load versions
        self.load_versions()
        
        # Set default username
        self.username.setText(generate_username()[0])
    
    def create_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setStyleSheet("background-color: #f0f0f0;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        
        # Logo
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("assets/logo.png").scaled(150, 150, Qt.KeepAspectRatio))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)
        
        layout.addSpacing(20)
        
        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background: #2a82da;
                color: white;
            }
        """)
        
        items = ["Play", "News", "Settings"]
        for item in items:
            list_item = QListWidgetItem(item)
            list_item.setFont(QFont("Arial", 10))
            self.nav_list.addItem(list_item)
        
        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self.change_page)
        layout.addWidget(self.nav_list)
        
        layout.addStretch()
        
        # Account info (placeholder)
        account_label = QLabel("Logged in as: Player")
        account_label.setFont(QFont("Arial", 8))
        layout.addWidget(account_label)
        
        self.sidebar.setLayout(layout)
    
    def create_main_content(self):
        self.main_content = QFrame()
        self.main_content.setFrameShape(QFrame.StyledPanel)
        
        self.stacked_widget = QStackedWidget()
        
        # Play page
        self.play_page = QWidget()
        self.create_play_page()
        self.stacked_widget.addWidget(self.play_page)
        
        # News page
        self.news_page = NewsWidget()
        self.stacked_widget.addWidget(self.news_page)
        
        # Settings page
        self.settings_page = SettingsWidget()
        self.stacked_widget.addWidget(self.settings_page)
        
        layout = QVBoxLayout(self.main_content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.stacked_widget)
    
    def create_play_page(self):
        layout = QVBoxLayout(self.play_page)
        
        # Title
        title = QLabel("Play Minecraft")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Username
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter your username")
        self.username.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        layout.addWidget(self.username)
        
        # Version selection
        version_layout = QHBoxLayout()
        version_label = QLabel("Version:")
        self.version_select = QComboBox()
        self.version_select.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        
        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_select)
        layout.addLayout(version_layout)
        
        # Progress bar
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
        
        # Play button
        self.start_button = QPushButton("PLAY")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
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
    
    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
    
    def load_versions(self):
        try:
            versions = get_version_list()
            release_versions = [v for v in versions if v["type"] == "release"]
            
            # Sort versions by release time (newest first)
            release_versions.sort(key=lambda x: x["releaseTime"], reverse=True)
            
            for version in release_versions[:20]:  # Show only the 20 most recent releases
                self.version_select.addItem(version["id"])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load Minecraft versions: {e}")
    
    def state_update(self, value):
        self.start_button.setDisabled(value)
        self.start_progress_label.setVisible(value)
        self.start_progress.setVisible(value)
        self.nav_list.setDisabled(value)
    
    def update_progress(self, progress, max_progress, label):
        self.start_progress.setValue(progress)
        self.start_progress.setMaximum(max_progress)
        self.start_progress_label.setText(label)
    
    def launch_game(self):
        ram_amount = int(self.settings_page.ram_slider.currentText())
        self.launch_thread.launch_setup_signal.emit(
            self.version_select.currentText(),
            self.username.text(),
            ram_amount
        )
        self.launch_thread.start()
    
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

if __name__ == '__main__':
    # Set up Minecraft directory
    minecraft_directory = get_minecraft_directory().replace('minecraft', 'FlatLauncher')
    os.makedirs(minecraft_directory, exist_ok=True)
    
    # Create application
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    FlatStyle.apply(app)
    
    # Check for required assets
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Create placeholder assets if they don't exist
    if not os.path.exists("assets/logo.png"):
        # Create a simple placeholder logo
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (256, 256), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "FlatLauncher", fill=(255, 255, 255))
        img.save("assets/logo.png")
    
    if not os.path.exists("assets/icon.png"):
        # Create a simple placeholder icon
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (64, 64), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
        img.save("assets/icon.png")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
