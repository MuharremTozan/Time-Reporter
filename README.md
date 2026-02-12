# 🕒 Time Reporter

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)

**Time Reporter** is a lightweight, local-first desktop application designed to track your daily activities on Windows. It automatically monitors which applications you are using and organizes them into meaningful time blocks, helping you understand where your time goes without compromising your privacy.

---

## ✨ Key Features

- **🚀 Hybrid Tracking Engine:** 
  - **Event-Driven:** Uses Windows Hooks (`WinEventHook`) to detect window switches instantly.
  - **Heartbeat:** Periodic updates every 60 seconds to ensure accuracy even during long sessions.
- **⚡ Pro Performance:** Multi-threaded architecture with a non-polling message pump, resulting in **~0% CPU usage**.
- **🔒 Privacy First:** All data is stored locally in a SQLite database. No cloud, no tracking, no data leakage.
- **💤 Smart Idle Detection:** Automatically pauses tracking if no user input (mouse/keyboard) is detected for a specified duration (default: 5 mins).
- **📊 Time-Block Logic:** Groups continuous activity into single blocks instead of cluttered per-minute records.
- **📦 Zero Configuration:** Comes with a `run.bat` for automatic environment setup and launch.

---

## 🛠 Tech Stack

- **Core:** Python 3.10+
- **APIs:** `pywin32` (Win32 API), `ctypes`
- **Database:** SQLite
- **UI:** CustomTkinter (Coming Soon)
- **Utilities:** `psutil`

---

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- Python 3.10 or higher

### Installation & Run
The easiest way to start is using the provided batch file:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Time-Reporter.git
   cd Time-Reporter
   ```
2. **Standard Run:** Double-click **`run.bat`**. (Shows terminal for logs)
3. **Professional Build:** Double-click **`build.bat`**. 
   - This creates a standalone **`main.exe`** in the `dist/` folder.
   - The EXE runs **without a terminal window**, perfectly hidden in the background while the UI stays visible.

---

## 📂 Project Structure

```text
/Time-Reporter
├── main.py              # Application entry point
├── run.bat              # One-click launcher for Windows
├── requirements.txt     # Python dependencies
├── src/
│   ├── core/            # Tracking engine & window hooks
│   ├── db/              # SQLite database management
│   ├── utils/           # Idle detection & system helpers
│   └── ui/              # Desktop interface components
├── documentation/       # Progress reports & technical docs
└── .agent/              # AI Agent protocols & workflows
```

---

## 🗺 Roadmap

- [x] Core Tracking Engine (Hybrid Model)
- [x] SQLite Integration
- [x] Idle Detection Logic
- [x] Multi-threaded Architecture
- [ ] **Modern Dashboard (CustomTkinter)**
- [ ] **Data Visualization (Charts & Analytics)**
- [ ] Application Categorization (Work, Play, Social)
- [ ] System Tray Integration

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

*Developed with ❤️ by Muharrem Tozan*
