import sys
import os
import logging
import platform
import psutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QToolButton, QSizePolicy, QStyle, QLabel,
    QGraphicsDropShadowEffect
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEnginePage,
    QWebEngineSettings
)
from PyQt6.QtCore import QUrl, Qt, QPoint
from PyQt6.QtGui import QIcon, QAction, QFont, QMouseEvent, QColor, QPalette

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)


# Configure logging
def setup_logging():
    # Ensure log directory exists
    log_dir = os.path.join(DATA_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Log file path
    log_file_path = os.path.join(log_dir, 'veil_browser.log')

    # Configure logging to write to both console and file
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


# Set up logger
logger = setup_logging()

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
        logger.info("Initializing CustomTitleBar")

        try:
            self.setStyleSheet("""
                QWidget {
                    background-color: #1a1a1a;
                    border-bottom: 1px solid #333;
                }
            """)
            layout = QHBoxLayout(self)
            layout.setContentsMargins(5, 2, 5, 2)
            logger.info("CustomTitleBar layout created with slim margins")

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
            logger.info("Added app title label")

            # Spacer
            layout.addStretch()
            logger.info("Added layout stretch")

            # Window Controls
            self.minimize_btn = QToolButton()
            self.maximize_btn = QToolButton()
            self.close_btn = QToolButton()

            # Robust icon handling with local paths
            try:
                self.minimize_btn.setIcon(QIcon(ICON_PATHS["windowMinimize"]))
                self.maximize_btn.setIcon(QIcon(ICON_PATHS["windowMaximize"]))
                self.close_btn.setIcon(QIcon(ICON_PATHS["windowClose"]))
                logger.info("Icons loaded successfully")
            except Exception as e:
                logger.error(f"Icon loading error: {e}")
                # Fallback to monochrome icons
                self.minimize_btn.setText("—")
                self.maximize_btn.setText("□")
                self.close_btn.setText("×")
                logger.warning("Falling back to text-based window control buttons")

            # Styling window control buttons
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
                logger.info("Window control button styling applied")

            layout.addWidget(self.minimize_btn)
            layout.addWidget(self.maximize_btn)
            layout.addWidget(self.close_btn)
            logger.info("Added window control buttons to layout")

            # Set a fixed height for the title bar
            self.setFixedHeight(30)
            logger.info("Set fixed title bar height to 30 pixels")

        except Exception as e:
            logger.critical(f"Fatal error in CustomTitleBar initialization: {e}")
            raise


def _create_nav_button(icon_name):
    logger.info(f"Creating navigation button for {icon_name}")
    btn = QToolButton()
    try:
        # Use local icon paths
        btn.setIcon(QIcon(ICON_PATHS[icon_name]))
        logger.info(f"Loaded icon for {icon_name}")
    except Exception as e:
        logger.warning(f"Navigation icon error for {icon_name}: {e}")
        # Fallback to text-based buttons
        btn.setText({
                        "back": "←",
                        "forward": "→",
                        "refresh": "⟳"
                    }[icon_name])
        logger.warning(f"Using text fallback for {icon_name}")

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
    logger.info(f"Styling applied to {icon_name} navigation button")
    return btn


class VeilBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing Veil Browser")

        # Custom window flags to remove default title bar and enable resizing
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )

        # Enable window resizing
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        logger.info("Window resizing enabled")

        # Add window resize capability
        self.setMouseTracking(True)
        logger.info("Mouse tracking enabled for window resizing")

        # Variables for window dragging
        self._drag_position = QPoint()
        self._resizing = False
        self._resize_margin = 10  # Resize handle thickness
        logger.info(f"Set resize margin to {self._resize_margin} pixels")

        # Main container with subtle border
        main_container = QWidget()
        main_container.setStyleSheet("""
            QWidget {
                background-color: #121212;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
            }
        """)
        logger.info("Created main container with dark, subtle styling")

        # Add subtle shadow effect
        shadow = QGraphicsDropShadowEffect(main_container)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        main_container.setGraphicsEffect(shadow)
        logger.info("Added subtle shadow effect to main container")

        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(1, 1, 1, 1)  # Thin border
        main_layout.setSpacing(0)
        logger.info("Created main layout with minimal margins")

        # Custom Title Bar
        self.title_bar = CustomTitleBar()
        main_layout.addWidget(self.title_bar)
        logger.info("Added custom title bar to main layout")

        # Connect title bar buttons
        self.title_bar.minimize_btn.clicked.connect(self.showMinimized)
        self.title_bar.maximize_btn.clicked.connect(self.toggle_maximize)
        self.title_bar.close_btn.clicked.connect(self.close)
        logger.info("Connected title bar button events")

        # Make title bar draggable
        self.title_bar.mousePressEvent = self.mousePressEvent
        self.title_bar.mouseMoveEvent = self.mouseMoveEvent
        logger.info("Made title bar draggable")

        # Navigation Layout
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 5, 10, 5)
        logger.info("Created navigation layout")

        # Navigation Buttons
        self.back_btn = _create_nav_button("back")
        self.forward_btn = _create_nav_button("forward")
        self.refresh_btn = _create_nav_button("refresh")

        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.refresh_btn)
        logger.info("Added navigation buttons to layout")

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
        logger.info("Added styled address bar")

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
        logger.info("Added 'Go' button")

        main_layout.addLayout(nav_layout)

        # Web View Configuration
        self.browser = QWebEngineView()

        # Create a custom profile to enable JavaScript, cookies, and local storage
        self.profile = QWebEngineProfile.defaultProfile()

        # Enable JavaScript and other settings using a more robust method
        settings = self.browser.settings()
        try:
            # Try different methods to enable JavaScript
            settings.setAttribute(16, True)  # Using numeric value for JavascriptEnabled
        except Exception as e:
            logger.warning(f"Could not set JavaScript setting: {e}")
            try:
                # Fallback method (if exists)
                settings.setAttribute('JavascriptEnabled', True)
            except Exception as fallback_error:
                logger.error(f"Fallback JavaScript setting failed: {fallback_error}")

        # Create a custom page with the profile
        self.page = QWebEnginePage(self.profile, self.browser)

        # Set the custom page for the web view
        self.browser.setPage(self.page)

        # Connect page signals
        self.page.urlChanged.connect(self.update_address_bar)
        self.page.loadProgress.connect(self.handle_load_progress)
        self.page.loadFinished.connect(self.on_load_finished)

        # Create a context to allow interaction with web pages
        self.page.runJavaScript("""
            document.addEventListener('click', function(e) {
                window.qt_page_clicked = true;
            });
        """)

        # Stylesheet for the web view
        self.browser.setStyleSheet("""
            QWebEngineView {
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)

        # Set initial URL and add to layout
        initial_url = QUrl("https://www.google.com")
        self.browser.setUrl(initial_url)
        main_layout.addWidget(self.browser)
        logger.info("Created web view and set initial URL to Google")

        self.setCentralWidget(main_container)

        # Connect browser navigation buttons
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.refresh_btn.clicked.connect(self.browser.reload)
        logger.info("Connected browser navigation events")

        # Window sizing and positioning
        self.resize(1200, 800)
        self.center_window()
        logger.info("Resized window to 1200x800 and centered")

    def toggle_maximize(self):
        try:
            if self.isMaximized():
                logger.info("Restoring window to normal size")
                self.showNormal()
            else:
                logger.info("Maximizing window")
                self.showMaximized()
        except Exception as e:
            logger.error(f"Error in toggle_maximize: {e}")

    def mousePressEvent(self, event: QMouseEvent):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                x, y = event.position().x(), event.position().y()
                width, height = self.width(), self.height()

                # Resize areas
                if (x < self._resize_margin or x > width - self._resize_margin or
                        y < self._resize_margin or y > height - self._resize_margin):
                    logger.info(f"Entered resize mode at position x:{x}, y:{y}")
                    self._resizing = True
                    self._drag_position = event.globalPosition().toPoint()
                else:
                    # Normal dragging
                    logger.info("Preparing to drag window")
                    self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        except Exception as e:
            logger.error(f"Error in mousePressEvent: {e}")

    def mouseMoveEvent(self, event: QMouseEvent):
        try:
            if event.buttons() == Qt.MouseButton.LeftButton:
                if self._resizing:
                    # Implement basic resizing logic
                    logger.info("Resizing window")
                    global_pos = event.globalPosition().toPoint()
                    diff = global_pos - self._drag_position
                    self.resize(
                        max(self.minimumWidth(), self.width() + diff.x()),
                        max(self.minimumHeight(), self.height() + diff.y())
                    )
                    self._drag_position = global_pos
                else:
                    # Window dragging
                    logger.info("Dragging window")
                    self.move(event.globalPosition().toPoint() - self._drag_position)
                event.accept()
            else:
                # Reset resizing state
                self._resizing = False
        except Exception as e:
            logger.error(f"Error in mouseMoveEvent: {e}")

    def mouseReleaseEvent(self, event):
        try:
            logger.info("Mouse button released, resetting resize state")
            self._resizing = False
        except Exception as e:
            logger.error(f"Error in mouseReleaseEvent: {e}")

    def handle_load_progress(self, progress):
        """
        Track and log page loading progress.

        Args:
            progress (int): Percentage of page load progress (0-100)
        """
        try:
            logger.info(f"Page loading progress: {progress}%")

            # Optional: Update a status bar or progress indicator if needed
            if hasattr(self, 'address_bar'):
                if progress < 100:
                    # Optionally modify address bar to show loading status
                    current_text = self.address_bar.text()
                    self.address_bar.setText(f"{current_text} - Loading ({progress}%)")
                else:
                    # Reset address bar when loading is complete
                    self.update_address_bar(self.browser.url())
        except Exception as e:
            logger.error(f"Error in handle_load_progress: {e}")

    def navigate_to_url(self):
        """
        Robust URL navigation method with enhanced parsing and loading.
        """
        try:
            # Get raw URL input from address bar
            raw_url = self.address_bar.text().strip()

            # Handle empty input
            if not raw_url:
                logger.warning("Empty URL input")
                return

            # URL parsing and validation
            try:
                # Default to HTTPS if no protocol specified
                if not raw_url.startswith(('http://', 'https://', 'file://')):
                    # For search queries or URLs without a dot
                    if ' ' in raw_url or not ('.' in raw_url):
                        raw_url = f'https://www.google.com/search?q={raw_url.replace(" ", "+")}'
                    else:
                        raw_url = 'https://' + raw_url

                # Convert to QUrl for robust handling
                qurl = QUrl(raw_url)

                # Validate and load URL
                if qurl.isValid():
                    logger.info(f"Navigating to validated URL: {qurl.toString()}")

                    # Use the custom page to load the URL
                    self.page.setUrl(qurl)

                    # Ensure focus on web view
                    self.browser.setFocus()
                else:
                    logger.warning(f"Invalid URL: {raw_url}")
                    self.address_bar.setText("Invalid URL")

            except Exception as parse_error:
                logger.error(f"URL parsing error: {parse_error}")
                # Fallback to search
                search_url = f'https://www.google.com/search?q={raw_url.replace(" ", "+")}'
                self.page.setUrl(QUrl(search_url))

        except Exception as e:
            logger.critical(f"Catastrophic navigation error: {e}")

    def update_address_bar(self, url):
        """
        Update address bar with current page URL and manage navigation buttons.
        """
        try:
            # Safely convert URL to string
            url_string = url.toString() if url else "about:blank"

            logger.info(f"Browser navigated to: {url_string}")

            # Update address bar
            self.address_bar.setText(url_string)

            # Manage navigation button states
            history = self.browser.page().history()
            self.back_btn.setEnabled(history.canGoBack())
            self.forward_btn.setEnabled(history.canGoForward())

        except Exception as e:
            logger.error(f"Address bar update error: {e}")
            self.address_bar.setText("about:blank")

    def setup_browser_connections(self):
        """
        Centralized method to set up all browser-related signal connections.
        """
        # URL changed event
        self.browser.urlChanged.connect(self.update_address_bar)

        # Optional load progress tracking
        self.browser.loadProgress.connect(handle_load_progress)

        # Optional load finished event
        self.browser.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, ok):
        """
        Handle page load completion with detailed logging.
        """
        if ok:
            logger.info("Page loaded successfully")
            # Optional: Run a script to check page interactivity
            self.page.runJavaScript("""
                console.log('Page loaded and ready for interaction');
                document.body.style.userSelect = 'auto';
            """)
        else:
            logger.warning("Page load failed")
            self.address_bar.setText("Load Failed")

    def center_window(self):
        try:
            frame_geometry = self.frameGeometry()
            screen_center = QApplication.primaryScreen().availableGeometry().center()
            frame_geometry.moveCenter(screen_center)
            self.move(frame_geometry.topLeft())
            logger.info("Window centered on screen")
        except Exception as e:
            logger.error(f"Error centering window: {e}")


def main():
    """
    Main entry point for the Veil web browser application.
    Handles application initialization, configuration, and launch.
    """
    try:
        # Log application start
        logger.info("=" * 50)
        logger.info("🌐 Veil Browser - Application Startup")
        logger.info("=" * 50)

        # System and Environment Check
        logger.info("Performing system environment check...")
        logger.info(f"Python Version: {sys.version}")
        logger.info(f"Operating System: {platform.platform()}")

        # Initialize Qt Application
        logger.info("Initializing Qt Application...")
        app = QApplication(sys.argv)

        # Application Metadata
        app.setApplicationName("Veil Browser")
        app.setApplicationVersion("1.0.0")
        logger.info("Application metadata configured")

        # Font Configuration
        logger.info("Configuring application font...")
        try:
            # Attempt to use Segoe UI, fallback to system default
            font = QFont("Segoe UI", 9)
            app.setFont(font)
            logger.info("Font set to Segoe UI, size 9")
        except Exception as font_error:
            logger.warning(f"Font configuration failed: {font_error}")
            logger.warning("Falling back to system default font")

        # Global Application Styling
        logger.info("Applying global application stylesheet...")
        app.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QWidget {
                background-color: #0a0a0a;
                color: #a0a0a0;
            }
        """)
        logger.info("Global stylesheet applied successfully")

        # Check Icon Paths
        logger.info("Verifying icon resources...")
        for icon_name, path in ICON_PATHS.items():
            if not os.path.exists(path):
                logger.warning(f"Icon not found: {path} for {icon_name}")
            else:
                logger.info(f"Icon verified: {path}")

        # Create Browser Instance
        logger.info("Creating browser window...")
        try:
            browser = VeilBrowser()
            logger.info("Browser window instantiated successfully")
        except Exception as browser_init_error:
            logger.critical(f"Failed to create browser window: {browser_init_error}")
            raise

        # Display Browser
        logger.info("Displaying browser window...")
        browser.show()

        # Screen and Display Information
        primary_screen = QApplication.primaryScreen()
        logger.info(f"Primary Screen: {primary_screen.name()}")
        logger.info(f"Screen Resolution: {primary_screen.size().width()}x{primary_screen.size().height()}")

        # Performance and Resource Logging
        logger.info("System Resource Check:")

        # Cross-platform memory information
        try:
            memory = psutil.virtual_memory()
            logger.info(f"Total Memory: {memory.total / (1024 * 1024 * 1024):.2f} GB")
            logger.info(f"Available Memory: {memory.available / (1024 * 1024 * 1024):.2f} GB")
            logger.info(f"Memory Usage: {memory.percent}%")
        except Exception as mem_error:
            logger.warning(f"Could not retrieve memory information: {mem_error}")

        # CPU Information
        try:
            logger.info(f"CPU Cores: {os.cpu_count()}")
            logger.info(f"CPU Usage: {psutil.cpu_percent()}%")
        except Exception as cpu_error:
            logger.warning(f"Could not retrieve CPU information: {cpu_error}")

        # Enter Event Loop
        logger.info("=" * 50)
        logger.info("🚀 Entering Application Event Loop")
        logger.info("=" * 50)

        # Run the application and capture exit code
        exit_code = app.exec()

        logger.info(f"Application exit code: {exit_code}")

        # Exit with captured code
        sys.exit(exit_code)

    except Exception as global_error:
        # Global error handler
        logger.critical("=" * 50)
        logger.critical("🚨 CRITICAL APPLICATION ERROR 🚨")
        logger.critical("=" * 50)
        logger.critical(f"Error Details: {global_error}")
        logger.critical(f"Error Type: {type(global_error).__name__}")

        # Optional: More detailed traceback
        import traceback
        logger.critical("Traceback:\n" + traceback.format_exc())

        # Ensure application exits with error status
        sys.exit(1)


if __name__ == "__main__":
    logger.info("Script started as main program")
    main()
