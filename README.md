# 🕒 Time Reporter

![Time Reporter Logo](Time%20Reporter.png)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Style](https://img.shields.io/badge/ui-CustomTkinter-orange.svg)](https://github.com/TomSchimansky/CustomTkinter)

**Time Reporter** is a professional, local-first Windows desktop application designed to track and analyze your productivity with steampunk-inspired precision. It lives in your system tray, monitors active windows, and provides deep insights into your work habits while keeping your data 100% private and offline.

---

## 🚀 Why Time Reporter?

Unlike cloud-based trackers, **Time Reporter** is built for privacy-conscious developers and professionals. It doesn't just record what you do; it understands *how* you work through smart merging logic and proactive idle detection.

### ✨ Key Features

- **🧠 Smart Activity Merging:** Optionally merges short browsing sessions (<5 mins) into your development blocks to keep your focus reports clean.
- **☕ Proactive Idle Detection:** Native Windows API integration detects when you're away. Upon return, a "Smart Popup" asks how to categorize the gap (Work or Break).
- **📊 Advanced Analytics:**
  - **Daily Breakdown:** Pie charts by Application and Category.
  - **Weekly Trends:** Bar charts showing total hours worked across the last 7 days.
- **🛡️ Manual Stealth Control:** Right-click the tray icon to "Start/Stop Break" manually. Tracking pauses and your "Break" session is recorded.
- **🔔 Desktop Notifications:** Instant feedback when toggling tracking states or finishing sessions.
- **⚙️ Deep Customization:**
  - Adjustable idle thresholds.
  - Data retention policies (auto-cleanup of old data).
  - Customizable application-to-category mappings.
  - Dark/Light/System theme support.
- **📦 Zero-Impact Background Mode:** Runs in the system tray with a branded gear icon, consuming minimal resources.

---

## 🛠 Tech Stack

- **Core Engine:** Python 3.10+ with `win32gui` & `ctypes` hooks.
- **Database:** SQLite (WAL Mode enabled for high-concurrency performance).
- **GUI:** `CustomTkinter` (Modern Native UI).
- **Visualization:** `Matplotlib` (High-fidelity charts).
- **Packaging:** `PyInstaller` (Optimized one-file EXE builds).

---

## 🚀 Getting Started

### Prerequisites
- Windows 10/11
- Python 3.10+ (for source installation)

### Installation (Source)
1. Clone the repository:
   ```bash
   git clone https://github.com/MuharremTozan/Time-Reporter.git
   cd Time-Reporter
   ```
2. Run the automated setup and launcher:
   ```bash
   run.bat
   ```

### Production Build
To create a branded, standalone Windows executable:
1. Run the build script:
   ```bash
   build.bat
   ```
2. Find your **`Time Reporter.exe`** in the `dist/` folder. It will include all icons and run in "Stealth Mode" (no console).

---

## 📂 Project Architecture

```text
/Time-Reporter
├── main.py              # Application entry point & thread coordinator
├── Time Reporter.spec   # PyInstaller build configuration
├── build.bat            # EXE compiler script
├── src/
│   ├── core/            # Window hooks, Heartbeat engine & Idle logic
│   ├── db/              # SQLite manager with WAL mode support
│   ├── ui/              # CustomTkinter views & Matplotlib charts
│   └── utils/           # Tray integration, Startup manager & Exporters
├── icon.ico             # Application icon
└── Time Reporter.png    # High-res branding asset
```

---

## 🛡️ Privacy First
- **No Internet Required:** The application never attempts to connect to the web.
- **Local SQLite:** Your activity history is stored strictly in `%APPDATA%/TimeReporter/`.
- **Transparency:** Open-source code allows you to verify exactly what is being tracked.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---

*Developed with ❤️ by Muharrem Tozan*
