import os
import logging
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QWidget, QGraphicsDropShadowEffect, QToolButton)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QColor
from .title_bar import CustomTitleBar
from .constants import ICON_PATHS

logger = logging.getLogger(__name__)


class VeilBrowser(QMainWindow):
    """Main browser window class"""
    def __init__(self):
        super().__init__()
        self.init_window()
        self.init_ui()
        self.setup_connections()

    def init_window(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMouseTracking(True)
        self._drag_position = QPoint()
        self._resizing = False
        self._resize_margin = 10
        self.resize(1200, 800)

    def init_ui(self):
        main_widget = QWidget()
        main_widget.setStyleSheet("background: #121212; border: 1px solid #2a2a2a;")

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        # Title bar
        self.title_bar = CustomTitleBar()
        self.title_bar.minimize_btn.clicked.connect(self.showMinimized)
        self.title_bar.maximize_btn.clicked.connect(self.toggle_maximize)
        self.title_bar.close_btn.clicked.connect(self.close)
        layout.addWidget(self.title_bar)

        # Navigation bar
        nav_bar = QHBoxLayout()
        self.back_btn = self._create_nav_button("back")
        self.forward_btn = self._create_nav_button("forward")
        self.refresh_btn = self._create_nav_button("refresh")

        self.address_bar = QLineEdit()
        self.address_bar.setStyleSheet("padding: 6px; background: #1e1e1e;")
        self.address_bar.returnPressed.connect(self.navigate)

        nav_bar.addWidget(self.back_btn)
        nav_bar.addWidget(self.forward_btn)
        nav_bar.addWidget(self.refresh_btn)
        nav_bar.addWidget(self.address_bar)
        layout.addLayout(nav_bar)

        # Web view
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl("https://google.com"))
        layout.addWidget(self.web_view)

        self.setCentralWidget(main_widget)

    def _create_nav_button(self, icon_type):
        btn = QToolButton()
        try:
            btn.setIcon(QIcon(ICON_PATHS[icon_type]))
        except:
            btn.setText({"back": "←", "forward": "→", "refresh": "⟳"}[icon_type])
        btn.setStyleSheet("QToolButton { padding: 5px; background: transparent; }")
        return btn

    def setup_connections(self):
        self.back_btn.clicked.connect(self.web_view.back)
        self.forward_btn.clicked.connect(self.web_view.forward)
        self.refresh_btn.clicked.connect(self.web_view.reload)
        self.web_view.urlChanged.connect(self.update_url)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint()
            self._resizing = (
                    event.position().x() < self._resize_margin or
                    event.position().y() < self._resize_margin or
                    self.width() - event.position().x() < self._resize_margin or
                    self.height() - event.position().y() < self._resize_margin
            )

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._resizing:
                self.resize(event.globalPosition().x(), event.globalPosition().y())
            else:
                self.move(event.globalPosition().toPoint() - self._drag_position)

    def navigate(self):
        url = self.address_bar.text()
        if not url.startswith(('http', 'https')):
            url = f'https://google.com/search?q={url}'
        self.web_view.setUrl(QUrl(url))

    def update_url(self, url):
        self.address_bar.setText(url.toString())
