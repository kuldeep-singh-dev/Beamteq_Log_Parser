# parser/models.py

from dataclasses import dataclass

@dataclass
class Job:
    file_path: str
    uploaded_date: str = ""
    uploaded_time: str = ""
    start_time: str = ""
    end_time: str = ""
    duration_minutes: float = 0.0
    cutting_duration_minutes: float = 0.0
    total_inputs_length: float = 0.0
    total_outputs_length: float = 0.0
    total_waste: float = 0.0
    total_pieces_in: int = 0
    total_pieces_out: int = 0
    # Helper – will be filled later when we know the DB id
    db_id: int = 0

@dataclass
class InputMaterial:
    job_id: int
    length_ft: float
    width_in: float
    height_in: float
    waste_ft: float
    timestamp: str

@dataclass
class OutputPiece:
    job_id: int
    input_id: int
    uid: int
    timestamp: str
    process_time_sec: float
