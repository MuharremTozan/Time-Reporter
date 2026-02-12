# 🕒 Time Reporter

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)

**Time Reporter** is a lightweight, local-first desktop application designed to track your daily activities on Windows. It automatically monitors which applications you are using and organizes them into meaningful time blocks, helping you understand where your time goes without compromising your privacy.

---

## ✨ Key Features

- **🚀 Hybrid Tracking Engine:** 
  - **Event-Driven:** Uses Windows Hooks (`WinEventHook`) to detect window switches instantly.
  - **Heartbeat:** Periodic updates every 60 seconds to ensure accuracy.
- **📊 Modern Dashboard:** 
  - **Real-time Stats:** Built with CustomTkinter for a sleek, dark-themed native Windows feel.
  - **Visual Analytics:** Interactive pie charts showing usage by Application and Category.
  - **Date Range Filters:** Quickly view stats for Today, Last 7 Days, or Last 30 Days.
- **📂 Smart Export System:**
  - **Auto-Logic:** Reconstructs your daily timeline, merging repetitive tasks and identifying breaks.
  - **Local Files:** Exports clean `.txt` reports to the application directory on exit or on demand.
- **🔒 Privacy & System:**
  - **Local-First:** All data stays on your machine in a SQLite database.
  - **System Tray:** Minimizes to tray for non-intrusive background operation.
  - **Auto-Startup:** Option to run automatically when Windows starts.
  - **Idle Detection:** Pauses tracking when you're away from your keyboard.

---

## 🛠 Tech Stack

- **Core:** Python 3.10+
- **UI:** CustomTkinter, Matplotlib
- **APIs:** `pywin32` (Win32 API), `pystray`
- **Database:** SQLite
- **Utilities:** `psutil`, `Pillow`

---

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- Python 3.10 or higher

### Installation & Run

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Time-Reporter.git
   cd Time-Reporter
   ```
2. **Standard Run:** Double-click **`run.bat`**. (Installs dependencies and starts the app)
3. **Professional Build:** Double-click **`build.bat`**. 
   - This creates a standalone **`main.exe`** in the `dist/` folder.
   - The EXE runs **without a terminal window**, living in the system tray.

---

## 📂 Project Structure

```text
/Time-Reporter
├── main.py              # Application entry point
├── build.bat            # EXE compiler (PyInstaller)
├── run.bat              # One-click launcher
├── requirements.txt     # Python dependencies
├── src/
│   ├── core/            # Tracking engine & window hooks
│   ├── db/              # SQLite database management
│   ├── ui/              # CustomTkinter interface & charts
│   └── utils/           # Tray, Export, Startup, and Idle helpers
└── documentation/       # Technical status reports
```

---

## 🗺 Roadmap

- [x] Core Tracking Engine (Hybrid Model)
- [x] SQLite Integration
- [x] Modern Dashboard (CustomTkinter)
- [x] Data Visualization (Pie Charts)
- [x] Application Categorization
- [x] System Tray Integration
- [x] Windows Auto-startup
- [x] Automatic/Manual Daily Export
- [ ] Advanced Date Range Picker
- [ ] Database Cleanup/Archiving Utilities
- [ ] Custom User Categories

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

*Developed with ❤️ by Muharrem Tozan*
