import sys
import os
import platform
import psutil
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from veil_browser.log_config import setup_logging
from veil_browser.browser_window import VeilBrowser
from veil_browser.constants import ICON_PATHS

# Initialize data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Set up logging
logger = setup_logging(DATA_DIR)

def main():
    """Main application entry point"""
    try:
        logger.info("=" * 50)
        logger.info("🌐 Veil Browser - Application Startup")
        logger.info("=" * 50)

        # Verify icon resources
        logger.info("Verifying icon resources...")
        for icon_name, path in ICON_PATHS.items():
            full_path = os.path.join(os.path.dirname(__file__), path)
            if not os.path.exists(full_path):
                logger.warning(f"Icon not found: {full_path} for {icon_name}")
            else:
                logger.info(f"Icon verified: {full_path}")

        app = QApplication(sys.argv)
        app.setApplicationName("Veil Browser")
        app.setApplicationVersion("1.0.0")

        # Font configuration
        try:
            font = QFont("Segoe UI", 9)
            app.setFont(font)
        except Exception as e:
            logger.warning(f"Font setup failed: {e}")

        # Create and show browser
        browser = VeilBrowser()
        browser.show()

        # System info logging
        logger.info(f"System: {platform.platform()}")
        logger.info(f"Python: {sys.version}")
        try:
            mem = psutil.virtual_memory()
            logger.info(f"Memory Available: {mem.available / (1024**3):.1f} GB")
        except Exception as e:
            logger.error(f"Memory check failed: {e}")

        exit_code = app.exec()
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()