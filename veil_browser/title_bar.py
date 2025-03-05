from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QToolButton
from PyQt6.QtGui import QIcon
from .constants import ICON_PATHS
import logging

logger = logging.getLogger(__name__)


class CustomTitleBar(QWidget):
    """Custom window title bar with native-style controls"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Title label
        self.title_label = QLabel("Veil")
        self.title_label.setStyleSheet("font-size: 12px; color: #a0a0a0;")
        layout.addWidget(self.title_label)

        # Spacer
        layout.addStretch()

        # Window controls
        self.minimize_btn = self._create_control_button(ICON_PATHS["windowMinimize"], "—")
        self.maximize_btn = self._create_control_button(ICON_PATHS["windowMaximize"], "□")
        self.close_btn = self._create_control_button(ICON_PATHS["windowClose"], "×")

        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)

        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #333;")

    def _create_control_button(self, icon_path, fallback_text):
        btn = QToolButton()
        try:
            btn.setIcon(QIcon(icon_path))
        except:
            btn.setText(fallback_text)
        btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                color: #a0a0a0;
                padding: 2px 5px;
                border: none;
            }
            QToolButton:hover { background: rgba(255,255,255,0.1); }
        """)
        return btn
