import sys
import os
import json
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QToolButton,
    QLabel,
    QGraphicsDropShadowEffect,
    QMessageBox,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import QUrl, Qt, QPoint, QTimer
from PyQt6.QtGui import QIcon, QFont, QMouseEvent, QColor, QKeySequence, QAction
import urllib.parse
import traceback

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Icon paths
ICON_PATHS = {
    "back": "icons/back.png",
    "forward": "icons/forward.png",
    "refresh": "icons/refresh.png",
    "windowMinimize": "icons/window-minimize.png",
    "windowMaximize": "icons/window-maximize.png",
    "windowClose": "icons/window-close.png",
}


class HistoryManager:
    @staticmethod
    def _load_history():
        """Load history from JSON file."""
        if not os.path.exists(HISTORY_FILE):
            return {}

        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    @staticmethod
    def add_history_entry(url, timestamp=None):
        """Add a new entry to the history."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # Load existing history
        history = HistoryManager._load_history()

        # Get the date as a string (without time)
        entry_date = date.fromisoformat(timestamp.split("T")[0]).isoformat()

        # Create entry for the day if not exists
        if entry_date not in history:
            history[entry_date] = []

        # Add the new entry
        history[entry_date].append({"url": url, "timestamp": timestamp})

        # Sort entries for the day by timestamp
        history[entry_date].sort(key=lambda x: x["timestamp"])

        # Write back to file
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(history, f, indent=2)
        except IOError as e:
            print(f"Error writing history: {e}")


def _create_nav_button(icon_name):
    btn = QToolButton()
    try:
        # Use local icon paths
        btn.setIcon(QIcon(ICON_PATHS.get(icon_name, "")))
    except Exception as e:
        print(f"Navigation icon error for {icon_name}: {e}")
        # Fallback to text-based buttons
        btn.setText({"back": "←", "forward": "→", "refresh": "⟳"}.get(icon_name, ""))

    btn.setStyleSheet(
        """
        QToolButton {
            background-color: transparent;
            color: #a0a0a0;
            border: none;
            padding: 5px;
            font-size: 16px;
        }
        QToolButton:hover {
            background-color: rgba(255,255,255,0.1);
            border-radius: 5px;
        }
        QToolButton:disabled {
            color: #555;
        }
    """
    )
    return btn


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1a1a1a;
                border-bottom: 1px solid #333;
            }
        """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # App Title
        self.title_label = QLabel("Veil Browser")
        self.title_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #a0a0a0;
                background-color: transparent;
                margin-left: 5px;
            }
        """
        )
        layout.addWidget(self.title_label)

        # Spacer
        layout.addStretch()

        # Window Controls
        self.minimize_btn = QToolButton()
        self.maximize_btn = QToolButton()
        self.close_btn = QToolButton()

        # Robust icon handling with local paths
        try:
            self.minimize_btn.setIcon(QIcon(ICON_PATHS.get("windowMinimize", "")))
            self.maximize_btn.setIcon(QIcon(ICON_PATHS.get("windowMaximize", "")))
            self.close_btn.setIcon(QIcon(ICON_PATHS.get("windowClose", "")))
        except Exception as e:
            print(f"Icon loading error: {e}")
            # Fallback to monochrome icons
            self.minimize_btn.setText("—")
            self.maximize_btn.setText("□")
            self.close_btn.setText("×")

        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setStyleSheet(
                """
                QToolButton {
                    background-color: transparent;
                    color: #a0a0a0;
                    border: none;
                    padding: 2px 5px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: rgba(255,255,255,0.1);
                    border-radius: 3px;
                }
            """
            )

        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)

        # Set a fixed height for the title bar
        self.setFixedHeight(30)


class ModernBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        # Custom window flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowMinimizeButtonHint
        )

        # Enable window resizing
        self.setMouseTracking(True)

        # Variables for window dragging
        self._drag_position = QPoint()
        self._resizing = False
        self._resize_margin = 10  # Resize handle thickness

        # Main container
        main_container = QWidget()
        main_container.setStyleSheet(
            """
            QWidget {
                background-color: #121212;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
            }
        """
        )

        # Add subtle shadow effect
        shadow = QGraphicsDropShadowEffect(main_container)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        main_container.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        # Custom Title Bar
        self.title_bar = CustomTitleBar()
        main_layout.addWidget(self.title_bar)

        # Connect title bar buttons
        self.title_bar.minimize_btn.clicked.connect(self.showMinimized)
        self.title_bar.maximize_btn.clicked.connect(self.toggle_maximize)
        self.title_bar.close_btn.clicked.connect(self.close)

        # Make title bar draggable
        self.title_bar.mousePressEvent = self.mousePressEvent
        self.title_bar.mouseMoveEvent = self.mouseMoveEvent

        # Navigation Layout
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 5, 10, 5)

        # Navigation Buttons
        self.back_btn = _create_nav_button("back")
        self.forward_btn = _create_nav_button("forward")
        self.refresh_btn = _create_nav_button("refresh")

        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.refresh_btn)

        # Address Bar
        self.address_bar = QLineEdit()
        self.address_bar.setStyleSheet(
            """
            QLineEdit {
                padding: 6px;
                border: 1px solid #333;
                border-radius: 5px;
                background-color: #1e1e1e;
                color: #a0a0a0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4a4a4a;
                outline: none;
                box-shadow: 0 0 5px rgba(74, 74, 74, 0.3);
            }
        """
        )
        self.address_bar.returnPressed.connect(self.navigate_to_address)
        self.address_bar.setPlaceholderText("Enter URL or search term")
        nav_layout.addWidget(self.address_bar, stretch=1)

        # Go Button
        self.go_btn = QPushButton("Go")
        self.go_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2a2a2a;
                color: #a0a0a0;
                border: none;
                border-radius: 5px;
                padding: 6px 10px;
                margin-left: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """
        )
        self.go_btn.clicked.connect(self.navigate_to_address)
        nav_layout.addWidget(self.go_btn)

        main_layout.addLayout(nav_layout)

        # Web View Setup
        profile = QWebEngineProfile.defaultProfile()
        profile.setCachePath(CACHE_DIR)
        profile.setPersistentStoragePath(CACHE_DIR)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        profile.setHttpCacheMaximumSize(1024 * 1024 * 100)  # 100 MB cache

        self.browser = QWebEngineView()

        # Configure WebEngine settings for performance
        settings = self.browser.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, False
        )

        self.browser.setStyleSheet(
            """
            QWebEngineView {
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """
        )

        # Progress indicator
        self.loading_label = QLabel("Loading...")
        self.loading_label.setStyleSheet(
            """
            QLabel {
                color: #a0a0a0;
                font-size: 12px;
                padding: 5px;
                background-color: rgba(0,0,0,0.5);
                border-radius: 5px;
            }
        """
        )
        self.loading_label.hide()

        # Load Overlay Layout
        loading_layout = QVBoxLayout()
        loading_layout.addStretch()
        loading_layout.addWidget(
            self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter
        )
        loading_layout.addStretch()

        # Add loading label to main layout
        main_layout.addLayout(loading_layout)
        main_layout.addWidget(self.browser)

        self.setCentralWidget(main_container)

        # Connect browser events
        self.browser.loadStarted.connect(self.on_load_started)
        self.browser.loadFinished.connect(self.on_load_finished)

        # Url change and history logging
        self.browser.page().urlChanged.connect(self.update_address_bar)
        self.browser.page().urlChanged.connect(self.log_history)

        # Connect navigation buttons
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.refresh_btn.clicked.connect(self.browser.reload)

        # Enable/Disable navigation buttons based on browser state
        self.browser.page().navigationsChanged.connect(self.update_navigation_buttons)

        # Shortcuts
        self.setup_keyboard_shortcuts()

        # Initial navigation
        self.browser.setUrl(QUrl("https://www.google.com"))

        # Window sizing and positioning
        self.resize(1200, 800)
        self.center_window()

    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for browser actions"""
        # Back shortcut
        back_shortcut = QKeySequence(Qt.Key.Key_Left | Qt.KeyboardModifier.AltModifier)
        self.back_action = QAction("Back", self)
        self.back_action.setShortcut(back_shortcut)
        self.back_action.triggered.connect(self.browser.back)
        self.addAction(self.back_action)

        # Forward shortcut
        forward_shortcut = QKeySequence(
            Qt.Key.Key_Right | Qt.KeyboardModifier.AltModifier
        )
        self.forward_action = QAction("Forward", self)
        self.forward_action.setShortcut(forward_shortcut)
        self.forward_action.triggered.connect(self.browser.forward)
        self.addAction(self.forward_action)

        # Refresh shortcut
        refresh_shortcut = QKeySequence(Qt.Key.Key_F5)
        self.refresh_action = QAction("Refresh", self)
        self.refresh_action.setShortcut(refresh_shortcut)
        self.refresh_action.triggered.connect(self.browser.reload)
        self.addAction(self.refresh_action)

    def update_navigation_buttons(self):
        """Update navigation button states based on browser history"""
        page = self.browser.page()
        self.back_btn.setEnabled(page.canGoBack())
        self.forward_btn.setEnabled(page.canGoForward())

    def on_load_started(self):
        """Show loading indicator when page starts loading"""
        self.loading_label.show()
        # Use a short delay to prevent flickering
        QTimer.singleShot(200, lambda: self.update_loading_label())

    def update_loading_label(self):
        """Update loading label with current URL"""
        try:
            current_url = self.loading_label.setText(f"Loading: {current_url}")
        except Exception as e:
            self.loading_label.setText("Loading...")
            print(f"Error updating loading label: {e}")

    def on_load_finished(self, success):
        """Handle page load completion"""
        self.loading_label.hide()

        # Optional: Show error message if load failed
        if not success:
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Icon.Warning)
            error_msg.setText("Page could not be loaded")
            error_msg.setInformativeText(
                "Please check the URL and your internet connection."
            )
            error_msg.setWindowTitle("Load Error")
            error_msg.exec()

    def navigate_to_address(self):
        """Navigate to URL or perform Google search"""
        address = self.address_bar.text().strip()

        # Check if it's a valid URL
        url = self.parse_address(address)
        self.browser.setUrl(url)

    def parse_address(self, address):
        """Parse address bar input into a valid URL"""
        if not address:
            return QUrl("https://www.google.com")

        # Check if it's a valid URL
        if address.startswith(("http://", "https://", "www.")):
            if not address.startswith(("http://", "https://")):
                address = "https://" + address
            return QUrl(address)

        # Perform Google search
        search_query = urllib.parse.quote(address)
        return QUrl(f"https://www.google.com/search?q={search_query}")

    def log_history(self, url):
        """Log the browsing history"""
        HistoryManager.add_history_entry(url.toString())

    def update_address_bar(self, url):
        """Update address bar with current URL"""
        self.address_bar.setText(url.toString())

    def toggle_maximize(self):
        """Toggle window between maximized and normal states"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for window dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            x, y = event.position().x(), event.position().y()
            width, height = self.width(), self.height()

            # Check if near window edges for resizing
            if (
                x < self._resize_margin
                or x > width - self._resize_margin
                or y < self._resize_margin
                or y > height - self._resize_margin
            ):
                self._resizing = True
                self._drag_position = event.globalPosition().toPoint()
            else:
                # Normal dragging
                self._drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for window dragging and resizing"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._resizing:
                # Implement basic resizing logic
                global_pos = event.globalPosition().toPoint()
                diff = global_pos - self._drag_position
                self.resize(
                    max(self.minimumWidth(), self.width() + diff.x()),
                    max(self.minimumHeight(), self.height() + diff.y()),
                )
                self._drag_position = global_pos
            else:
                # Window dragging
                self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
        else:
            # Reset resizing state
            self._resizing = False

    def mouseReleaseEvent(self, event):
        """Reset resizing state on mouse release"""
        self._resizing = False

    def center_window(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Optional: Set app-wide font
    font = QFont("Segoe UI", 9)  # Slightly smaller font
    app.setFont(font)

    # Global application styling
    app.setStyleSheet(
        """
        QMainWindow {
            background-color: #0a0a0a;
        }
        QWidget {
            background-color: #0a0a0a;
            color: #a0a0a0;
        }
    """
    )

    # Error handling wrapper
    try:
        browser = ModernBrowser()
        browser.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Critical error: {e}")
        traceback.print_exc()
        QMessageBox.critical(
            None,
            "Critical Error",
            f"An unexpected error occurred:\n{e}\n\n" "The application will now close.",
        )


if __name__ == "__main__":
    main()
