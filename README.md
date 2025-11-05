# Beamteq Log Parser

A Python tool to parse Beamteq CNC log files (`.txt`), extract production data, and save to SQLite.

## Quick Start

```bash
git clone https://github.com/kuldeep-singh-dev/Beamteq_Log_Parser.git
cd beamteq_log_parser
pip install -r requirements.txt

## Quick Start

1. **Put your Beamteq log files** in:


2. **Run the parser**:
```bash
# Parse all .txt files in the folder
python main.py data/logs/

# Or parse a single file
python main.py data/logs/log_ex.txt

## Output

- **Database**: `db/beamteq.db` (created automatically)
- **Tables**:
  - `jobs`
  - `input_materials`
  - `output_pieces`

---

## Features

- **mm → ft/in** conversion
- **Duration** from last `Abtransport` (accurate cutting time)
- **Links outputs to inputs** via `Bauteil` number
- **Multiple jobs per file** supported

---

## Project Structure

beamteq-log-parser/
│
├── config/
│   └── settings.py               # App config (paths, encoding)
│
├── data/
│   ├── logs/                     # ← Put your .txt log files here
│   └── output/                   # CSV exports, reports
│
├── db/                           # ← Database files
│   ├── init.py
│   ├── database.py               # SQLite connection & CRUD
│   └── schema.sql                # Table definitions
│
├── parser/
│   ├── init.py
│   ├── log_parser.py             # Core parsing logic
│   ├── log_reader.py             # Reads .txt files
│   └── models.py                 # Job, InputMaterial, OutputPiece
│
├── utils/
│   ├── init.py
│   ├── converter.py              # mm_to_feet, mm_to_inches
│   ├── loggers.py                # Logging setup
│   └── time_utils.py             # parse_timestamp, duration_minutes
│
├── main.py                       # Entry point
└── README.md
