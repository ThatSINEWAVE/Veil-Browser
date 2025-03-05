<div align="center">

# Veil Browser

![Veil-Browser](https://raw.githubusercontent.com/ThatSINEWAVE/Veil-Browser/refs/heads/main/.github/SCREENSHOTS/VEIL-BROWSER.png)

Veil Browser is a privacy-first web browser designed to eliminate tracking, data collection, and intrusive analytics. It is fully open-source and built with the goal of providing a truly private browsing experience. The project is currently in its early development stage and remains highly unstable.

</div>

## Features (Planned)
- 🚫 **No Trackers** – No hidden tracking, telemetry, or data collection.
- 🔓 **Open Source** – Fully transparent code for community-driven development.
- 🎭 **Custom UI** – A unique, modern, and minimalist interface.
- 🛠 **No Bloat** – Stripped-down browsing experience without unnecessary features.
- 🏴 **Privacy by Design** – Enforced privacy-focused settings by default.

## Project Structure
```
veil-browser/
├── main.py
├── data/
│   ├── logs/
│   │   └── veil_browser.log
│   ├── history.json
│   └── icons.json
├── icons/
│   ├── back.png
│   ├── forward.png
│   ├── refresh.png
│   ├── window-minimize.png
│   ├── window-maximize.png
│   └── window-close.png
└── veil_browser/
    ├── __init__.py
    ├── constants.py
    ├── log_config.py
    ├── title_bar.py
    └── browser_window.py
```

## Current Status
Veil Browser is in **early development** and is currently **unstable and mostly unusable**. Key functionalities, such as smooth navigation and stability, are still under development.

<div align="center">

## ☕ [Support my work on Ko-Fi](https://ko-fi.com/thatsinewave)

</div>

## Installation & Running
### Prerequisites
- Python 3.8+
- PyQt6
- PyQt6-WebEngine
- psutil

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/veil-browser.git
   cd veil-browser
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Ensure required directories exist:
   ```sh
   mkdir -p icons data/logs
   ```
4. Place required PNG icons in `icons/` directory
5. Run the browser:
   ```sh
   python main.py
   ```

The application will automatically create:
- `data/history.json` – Browsing history storage
- `data/icons.json` – Icon configuration file
- `data/logs/` – Application log directory

## Known Issues
- Frequent crashes
- Navigation issues and broken rendering
- Limited functionality beyond basic browsing
- Initial setup requires manual icon placement

## Roadmap
- Improve stability and usability
- Add an integrated ad and tracker blocker
- Enhance the UI with more customization options
- Implement better memory management
- Automate icon setup process

<div align="center">

## [Join my discord server](https://discord.gg/2nHHHBWNDw)

</div>

## Contributions
Contributions are welcome! Feel free to fork the repository, submit issues, and open pull requests.
Please note:
- Icon assets must be placed in `icons/` directory
- Configuration files reside in `data/` directory
- Core browser logic is in `veil_browser/` package

## License
This project is licensed under the GPL-3.0 License. See [LICENSE](LICENSE) for more details.

## Disclaimer
This browser is **not yet suitable for daily use**. Expect bugs, crashes, and missing features as development progresses.

Stay tuned for updates and improvements as we work toward making Veil Browser a truly private and reliable browsing solution!