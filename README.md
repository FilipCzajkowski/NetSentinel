# 🛡️ NetSentinel

> **Asynchronous Workstation Diagnostics & Network Security Health CLI**  
> Built for IT Support Technicians, System Administrators, and Junior SOC Analysts.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![AsyncIO](https://img.shields.io/badge/AsyncIO-Concurrency-orange?style=for-the-badge)
![Rich](https://img.shields.io/badge/CLI-Rich_Terminal-magenta?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📌 Overview

**NetSentinel** is a lightweight, asynchronous command-line tool designed to perform rapid health checks on local workstations and network endpoints. It automates common troubleshooting steps performed by Level 1/2 IT Support and Security teams:

1. **System Resource Telemetry:** Collects live metrics on CPU load, RAM saturation, disk partition free space (with automatic threshold alerts), OS details, and system uptime.
2. **Asynchronous Network Diagnostics:** Measures latency and connectivity against critical public and DNS resolvers concurrently using `asyncio`.
3. **Security Port Auditor:** Scans target IP addresses for common and high-risk exposed services (e.g. unencrypted Telnet, SMB, RDP, FTP) to detect misconfigurations.
4. **Structured JSON Export:** Serializes diagnostic sessions into standard JSON format for incident ticketing (Jira/ServiceNow) or centralized auditing.

---

## 🚀 Key Features

- ⚡ **High-Speed Asynchronous Checks:** Concurrently checks network targets and socket connections in milliseconds.
- 🎨 **Rich Visual Dashboard:** Clean, color-coded terminal tables with alerts for high disk utilization or exposed sensitive ports.
- 🧩 **Modular Clean Architecture:** Decoupled modules for system monitoring, network diagnostics, and reporting.
- 🧪 **Unit Tested:** Built with testability in mind using `pytest`.
- 📁 **JSON Audit Logging:** Export machine-readable reports with a single CLI flag.

---

## 🛠️ Project Structure

```text
NetSentinel/
├── sentinel/
│   ├── __init__.py
│   ├── system_monitor.py      # Hardware & OS metrics collection (psutil)
│   ├── network_checker.py     # Asynchronous socket & latency probes
│   └── reporter.py            # Rich terminal tables and JSON serialization
├── tests/
│   └── test_sentinel.py       # Pytest unit test suite
├── main.py                    # CLI entry point (argparse)
├── requirements.txt           # Project dependencies
└── README.md
```

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/FilipCzajkowski/NetSentinel.git
   cd NetSentinel
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Usage Examples

### 1. Standard Full Audit (Localhost + System + Network)
```bash
python main.py
```

### 2. Audit a Specific Remote Host or Gateway
Scan specific ports on a remote server with a 1.5s timeout:
```bash
python main.py --target 192.168.1.1 --ports 22,80,443,8080 --timeout 1.5
```

### 3. Generate a Ticket Audit JSON Report
Export diagnostic findings directly to a JSON file:
```bash
python main.py --export incident_report.json
```

### 4. Network Only Mode (Skip Local Hardware Metrics)
```bash
python main.py --skip-system --target 8.8.8.8 --ports 53,443
```

---

## 🧪 Running Unit Tests

Run the test suite using `pytest`:
```bash
pytest -v
```

---

## 👤 Author

**Filip Czajkowski**
- LinkedIn: [linkedin.com/in/CzajkowskiFilip](https://linkedin.com/in/CzajkowskiFilip)
- GitHub: [@FilipCzajkowski](https://github.com/FilipCzajkowski)
- Email: `CzajkowskiFilip@proton.me`

---

## 📄 License
This project is licensed under the MIT License.
