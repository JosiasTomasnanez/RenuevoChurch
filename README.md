# RenuevoChurch — Administration System ⛪

A cross-platform desktop application built with Python and Tkinter, designed to streamline member administration, consolidation monitoring, and ministry configuration for **Iglesia Renuevo**. The system connects to a secure cloud-hosted backend on Render to ensure seamless, real-time data synchronization.

## ✨ Features

* **Modular Views**: Clean and dedicated interfaces for adding, searching, and modifying church members.
* **Asynchronous Startup**: A polished splash screen with a dynamic progress bar handles backend wake-up calls and initial data caching without freezing the UI.
* **Live API Sync**: Integrated client layers (`PeopleAPI` and `ConfigAPI`) communicate with the remote server to fetch up-to-date data on ministries, consolidation levels, and personal records.
* **Automated Updates**: Multi-platform auto-updater checks the remote server version on launch, downloads the appropriate installer (`.exe` for Windows or `.sh` for Linux), handles execution, and restarts the application automatically.
* **Smart Layout Management**: Built using a stack-based frame approach (`.lift()` and `.lower()`) inside a main container to provide smooth navigation between views.

## 📂 Project Architecture

The repository is structured with a clean separation of concerns between the user interface and the API communication layer

## 🚀 Getting Started

### Prerequisites

* **Python 3.12** or higher installed on your system.
* Active internet connection (needed for API sync and update checks).

### Installation & Execution

1. **Clone the repository:**
```bash
git clone https://github.com/JosiasTomasnanez/RenuevoChurch.git
cd RenuevoChurch

```


2. **Install requirements:**
Make sure to install third-party UI dependencies like `tkcalendar`:
```bash
pip install -r requirements.txt

```


3. **Run the app package:**
```bash
python3 -m src.frontend.main

```



## 🛠️ Built With

* [Python](https://www.python.org/) - Core language.
* [Tkinter / TTK](https://docs.python.org/3/library/tkinter.html) - Desktop GUI framework.
* [Render](https://render.com/) - Backend hosting provider.
* [Neon](https://neon.com/) - Backend PostgreSQL provider.

## 📌 Update Feed

The client automatically requests version updates at startup from Render. If a version mismatch with the current build is found, the installation wizard starts automatically.
