-- db/schema.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    uploaded_date TEXT,
    uploaded_time TEXT,
    start_time TEXT,
    end_time TEXT,
    duration_min REAL,
    cut_duration_min REAL,
    total_input_length_ft REAL,
    total_output_length_ft REAL,
    total_waste_ft REAL,
    total_pieces_in INTEGER,
    total_pieces_out INTEGER,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS input_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    length_ft REAL,
    width_in REAL,
    height_in REAL,
    waste_ft REAL,
    timestamp TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS output_pieces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    input_id INTEGER,
    uid INTEGER,
    timestamp TEXT,
    process_time_sec REAL,
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE,
    FOREIGN KEY (input_id) REFERENCES input_materials (id) ON DELETE CASCADE
);
