# rtmaps_python

> Python package providing external APIs for RTMaps runtime engine

---

## ⚠️ Important Notice

**The `rtmaps` pip package is not yet officially released!**  
Use the test package from TestPyPI until official release:

```bash
pip install -i https://test.pypi.org/simple/ rtmaps==1.0.0
```

---

## 📦 Quick Start

1. **Create Python virtual environment:**
```bash
python -m venv .venv-rtmaps
source .venv-rtmaps/Scripts/activate  # On Windows: .venv-rtmaps\Scripts\activate
```

2. **Install base requirements:**
```bash
pip install -i https://test.pypi.org/simple/ rtmaps==0.0.8
pip install -r base_requierements.txt
```

3. **Install example-specific dependencies:**
```bash
# For Web UI example
pip install -r examples/WebUI/additionnal_requirements.txt

# For REST API example
pip install -r examples/REST/additionnal_requirements.txt
```

---

## 📂 Project Structure

```
rtmaps_python/
├── README.md                    # This file
├── base_requierements.txt       # Core dependencies
└── .gitignore                   # Git ignore rules

examples/
├── Basic/                      # Simple Python API usage examples
│   └── basic_usage.py
├── Advanced/                   # Advanced use cases & exporters
│   └── csv_to_mcap/            # CSV to MCAP converter example
│       ├── README.md
│       └── csv_to_mcap.py
├── REST/                       # Typed REST API (port 8000)
│   ├── README.md               # API documentation & endpoints
│   └── rtmaps_typed_rest_api.py
└── WebUI/                     # Web-based control panel (port 8080)
    ├── README.md               # UI documentation & controls
    ├── rtmaps_web_control_ui.py
    └── webui/                  # Static files (HTML, JS, CSS)
```

---

## 🔹 Basic Python API Usage (`examples/Basic/`)

Simple direct usage of RTMaps Abstraction API for building custom diagrams.

**Example:** [`basic_usage.py`](examples/Basic/basic_usage.py)

**Run it:**
```bash
cd examples/Basic
python basic_usage.py
```

This example:
- Creates an RTMaps diagram programmatically
- Adds components (`Randint`, `DataViewer`)
- Connects outputs to inputs
- Sets component properties (`vectorSize`, `max`)
- Runs and reads output data
- Clean shutdown with proper resource cleanup

---

## 🔸 Advanced Use Cases (`examples/Advanced/`)

### CSV to MCAP Converter (`examples/Advanced/csv_to_mcap/`)

Converts CSV files to [MCAP](https://mcap.io/) format using RTMaps streaming components.

**Example:** [`csv_to_mcap.py`](examples/Advanced/csv_to_mcap/csv_to_mcap.py)

**Run it:**
```bash
cd examples/Advanced/csv_to_mcap
python csv_to_mcap.py INPUT_CSV_FOLDER OUTPUT_MCAP_FOLDER
```

**Verbose mode (see RTMaps console output):**
```bash
python csv_to_mcap.py INPUT_CSV_FOLDER OUTPUT_MCAP_FOLDER --verbose
```

Features:
- Bulk processing of all `.csv` files in input folder
- Automatic channel type detection (`Float(s)`)
- Topic name auto-generation from CSV columns
- Proper EOF handling and cleanup
- Real-time logging to console

---

## REST API (`examples/REST/`)

Typed FastAPI backend for RTMaps runtime control.

**Start it:**
```bash
cd examples/REST
python rtmaps_typed_rest_api.py
```

Access: `http://localhost:8000`

See [`README.md`](examples/REST/README.md) for full API documentation.

---

### Web UI (`examples/WebUI/`)

HTML5/CSS3/JS control panel with live state monitoring.

**Start it:**
```bash
cd examples/WebUI
python rtmaps_web_control_ui.py
```

Access: `http://127.0.0.1:8080/webui/index.html`

See [`README.md`](examples/WebUI/README.md) for controls and features.

---
