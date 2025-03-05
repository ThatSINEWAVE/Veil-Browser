import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QToolButton, QSizePolicy, QStyle, QLabel,
    QGraphicsDropShadowEffect
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl, Qt, QPoint
from PyQt6.QtGui import QIcon, QAction, QFont, QMouseEvent, QColor, QPalette

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
                background-color: #1a1a1a;
                border-bottom: 1px solid #333;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)  # Reduced margins for a slimmer title bar

        # App Title
        self.title_label = QLabel("Veil")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #a0a0a0;
                background-color: transparent;
                margin-left: 5px;
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
            # Fallback to monochrome icons
            self.minimize_btn.setText("—")
            self.maximize_btn.setText("□")
            self.close_btn.setText("×")

        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setStyleSheet("""
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
            """)

        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)

        # Set a fixed height for the title bar
        self.setFixedHeight(30)


def _create_nav_button(icon_name):
    btn = QToolButton()
    try:
        # Use local icon paths
        btn.setIcon(QIcon(ICON_PATHS[icon_name]))
    except Exception as e:
        print(f"Navigation icon error for {icon_name}: {e}")
        # Fallback to text-based buttons
        btn.setText({
                        "back": "←",
                        "forward": "→",
                        "refresh": "⟳"
                    }[icon_name])

    btn.setStyleSheet("""
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
    """)
    return btn


class ModernBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        # Custom window flags to remove default title bar and enable resizing
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )

        # Enable window resizing
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)

        # Add window resize capability
        self.setMouseTracking(True)

        # Variables for window dragging
        self._drag_position = QPoint()
        self._resizing = False
        self._resize_margin = 10  # Resize handle thickness

        # Main container with subtle border
        main_container = QWidget()
        main_container.setStyleSheet("""
            QWidget {
                background-color: #121212;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
            }
        """)

        # Add subtle shadow effect
        shadow = QGraphicsDropShadowEffect(main_container)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        main_container.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(1, 1, 1, 1)  # Thin border
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
        self.address_bar.setStyleSheet("""
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
        """)
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.address_bar, stretch=1)

        # Go Button
        self.go_btn = QPushButton("Go")
        self.go_btn.setStyleSheet("""
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
        """)
        self.go_btn.clicked.connect(self.navigate_to_url)
        nav_layout.addWidget(self.go_btn)

        main_layout.addLayout(nav_layout)

        # Web View
        self.browser = QWebEngineView()
        self.browser.setStyleSheet("""
            QWebEngineView {
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
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
            # Check if near window edges for resizing
            x, y = event.position().x(), event.position().y()
            width, height = self.width(), self.height()

            # Resize areas
            if (x < self._resize_margin or x > width - self._resize_margin or
                    y < self._resize_margin or y > height - self._resize_margin):
                self._resizing = True
                self._drag_position = event.globalPosition().toPoint()
            else:
                # Normal dragging
                self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._resizing:
                # Implement basic resizing logic
                global_pos = event.globalPosition().toPoint()
                diff = global_pos - self._drag_position
                self.resize(
                    max(self.minimumWidth(), self.width() + diff.x()),
                    max(self.minimumHeight(), self.height() + diff.y())
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
        self._resizing = False

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
    font = QFont("Segoe UI", 9)  # Slightly smaller font
    app.setFont(font)

    # Global application styling
    app.setStyleSheet("""
        QMainWindow {
            background-color: #0a0a0a;
        }
        QWidget {
            background-color: #0a0a0a;
            color: #a0a0a0;
        }
    """)

    browser = ModernBrowser()
    browser.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()