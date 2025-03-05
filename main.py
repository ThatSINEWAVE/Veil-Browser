import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QToolButton, QSizePolicy, QStyle
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl, Qt, QPoint
from PyQt6.QtGui import QIcon, QAction, QFont, QMouseEvent

# Icon paths
ICON_PATHS = {
    "back": "icons/back.png",
    "forward": "icons/forward.png",
    "refresh": "icons/refresh.png",
    "windowMinimize": "icons/window-minimize.png",
    "windowMaximize": "icons/window-maximize.png",
    "windowClose": "icons/window-close.png"
}


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # App Title
        self.title_label = QPushButton("Veil Browser")
        self.title_label.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.title_label)

        # Spacer
        layout.addStretch()

        # Window Controls
        self.minimize_btn = QToolButton()
        self.maximize_btn = QToolButton()
        self.close_btn = QToolButton()

        # Robust icon handling with local paths
        try:
            self.minimize_btn.setIcon(QIcon(ICON_PATHS["windowMinimize"]))
            self.maximize_btn.setIcon(QIcon(ICON_PATHS["windowMaximize"]))
            self.close_btn.setIcon(QIcon(ICON_PATHS["windowClose"]))
        except Exception as e:
            print(f"Icon loading error: {e}")
            # Fallback to system icons
            self.minimize_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton))
            self.maximize_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
            self.close_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))

        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }
                QToolButton:hover {
                    background-color: rgba(0,0,0,0.1);
                }
            """)

        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)


class ModernBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        # Remove transparent background
        self.setWindowFlags(Qt.WindowType.Window)

        # Enable window resizing
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint)

        # Variables for window dragging
        self._drag_position = QPoint()

        # Main container
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
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
        self.back_btn = self._create_nav_button("back")
        self.forward_btn = self._create_nav_button("forward")
        self.refresh_btn = self._create_nav_button("refresh")

        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.refresh_btn)

        # Address Bar
        self.address_bar = QLineEdit()
        self.address_bar.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #e0e0e0;
                border-radius: 15px;
                background-color: white;
                font-size: 14px;
                color: black;  /* Ensure text is visible */
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                box-shadow: 0 0 5px rgba(74, 144, 226, 0.3);
            }
        """)
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.address_bar, stretch=1)

        # Go Button
        self.go_btn = QPushButton("Go")
        self.go_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 6px 12px;
                margin-left: 5px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        self.go_btn.clicked.connect(self.navigate_to_url)
        nav_layout.addWidget(self.go_btn)

        main_layout.addLayout(nav_layout)

        # Web View
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        main_layout.addWidget(self.browser)

        self.setCentralWidget(main_container)

        # Connect browser events
        self.browser.urlChanged.connect(self.update_address_bar)
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.refresh_btn.clicked.connect(self.browser.reload)

        # Window sizing and positioning
        self.resize(1200, 800)
        self.center_window()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def _create_nav_button(self, icon_name):
        btn = QToolButton()
        try:
            # Use local icon paths
            btn.setIcon(QIcon(ICON_PATHS[icon_name]))
        except Exception as e:
            print(f"Navigation icon error for {icon_name}: {e}")
            # Fallback to system-provided icons
            btn.setIcon(QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_ArrowBack if icon_name == "back" else
                QStyle.StandardPixmap.SP_ArrowForward if icon_name == "forward" else
                QStyle.StandardPixmap.SP_BrowserReload
            ))

        btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: rgba(0,0,0,0.1);
                border-radius: 5px;
            }
        """)
        return btn

    def navigate_to_url(self):
        url = self.address_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.browser.setUrl(QUrl(url))

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())

    def center_window(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())


def main():
    app = QApplication(sys.argv)
    # Optional: Set app-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Optional: Set application style
    app.setStyleSheet("""
        QMainWindow {
            background-color: white;
        }
    """)

    browser = ModernBrowser()
    browser.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()