# EyeZen (护眼禅)

<p align="center">
  <br>
  <b>A minimalist, smooth, and unobtrusive eye-care assistant for Windows.</b>
  <br>
  <br>
  <img src="https://img.shields.io/badge/platform-Windows-blue.svg" alt="Windows">
  <img src="https://img.shields.io/badge/python-3.8+-yellow.svg" alt="Python Version">
  <img src="https://img.shields.io/github/license/你的用户名/EyeZen" alt="License">
</p>

### Main Panel

<img width="793" height="630" alt="image" src="https://github.com/user-attachments/assets/51f13a2c-50bc-4028-947e-29ed4fb130e7" />

### Setting Panel

<img width="702" height="612" alt="image" src="https://github.com/user-attachments/assets/f7295ae1-db57-4985-a9d0-c9dc85e91a1e" />

### Rest Appearance

<img width="2560" height="1438" alt="3" src="https://github.com/user-attachments/assets/4f49bedd-890f-4ec1-af8d-4c7e225774b1" />



## 📖 Introduction

**EyeZen** is designed to prevent eye strain caused by prolonged computer use. Unlike simple timers, it provides a polished user experience with smooth hardware-level brightness control, a non-intrusive warm overlay for temperature adjustment, and a "forced" (but skippable) full-screen rest mode.

Built with modern **Python** and **PyQt6**, it features a multi-threaded architecture to ensure the UI remains responsive, even when communicating with monitor hardware or performing startup tasks.

The Code is totally written and updated by Gemini 3.0 and Deepseek V3. 

## ✨ Key Features

* **⏱️ Smart Work/Rest Timer:** Customizable intervals for focused work and short breaks.
* **💡 Hardware Brightness Control:** Adjusts your monitor's actual backlight using DDC/CI protocol (smooth transitions, no lag).
* **🌡️ Warm Color Overlay:** A stable, system-wide warm overlay to reduce blue light, compatible with all Windows setups.
* **🛑 Forced Rest Mode:** A full-screen, translucent overlay with calming quotes that encourages you to take a break. Includes a 30-second auto-start countdown.
* **🚀 Instant Startup:** Asynchronous loading ensures the app interface appears immediately.
* **🎮 Intelligent Exclusions:** Automatically pauses timers when running full-screen applications (games, movies) or specified processes.
* **🎛️ Quick Dashboard & Presets:** Easily switch between Normal, Smart, Office, Game, Movie, Reading, and Night modes.
* **🔔 System Tray Integration:** Minimize to tray and run quietly in the background.

## 🖼️ Screenshots

| Dashboard | Rest Overlay | Settings |
| :---: | :---: | :---: |
| | | |
| *Main control panel* | *Time to rest!* | *Customizations* |

## 🛠️ Installation & Running

### Prerequisites

* Windows 10 or 11
* Python 3.8 or higher

### Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/fgzong-star/EyeZen.git](https://github.com/fgzong-star/EyeZen.git)
    cd EyeZen
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    # (Optional) Create and activate venv
    python -m venv venv
    .\venv\Scripts\activate

    # Install required packages
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python eyezen.py
    ```

you can also find the .exe file in the release section.

*Note: The first run might take a moment to initialize monitor hardware in the background, but the splash screen will appear instantly.*

## ⚙️ Configuration

Settings are saved automatically in `eyezen_config.json` located in the application directory. You can modify settings via the GUI gear icon:

* **Work/Rest Duration:** Set your preferred intervals.
* **Auto-start Rest:** How many seconds before the rest overlay automatically begins the countdown.
* **Exclusions:** Add process names (e.g., `vlc.exe`, `chrome.exe`) to pause the timer when these apps are active.

## 🏗️ Built With

* [PyQt6](https://pypi.org/project/PyQt6/) - The GUI framework.
* [screen-brightness-control](https://github.com/Crozzers/screen_brightness_control) - For hardware-level DDC/CI monitor control.

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).

---
<p align="center">Developed with ❤️ for healthier eyes.</p>
