# main.py
import sys
from pathlib import Path
from config import settings
from parser.log_parser import BeamteqLogParser
from db.database import Database
from utils.logger import log
from utils.time_utils import duration_minutes
from datetime import datetime

def job_to_dict(job) -> dict:
    """Convert a Job dataclass → dict that matches the DB table."""
    return {
        "file_path": job.file_path,
        "uploaded_date": job.uploaded_date,
        "uploaded_time": job.uploaded_time,
        "start_time": job.start_time,
        "end_time": job.end_time,
        "duration_min": job.duration_minutes,
        "cut_duration_min": job.cutting_duration_minutes,
        "total_input_length_ft": job.total_inputs_length,
        "total_output_length_ft": job.total_outputs_length,
        "total_waste_ft": job.total_waste,
        "total_pieces_in": job.total_pieces_in,
        "total_pieces_out": job.total_pieces_out,
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

def input_to_dict(inp, job_db_id: int) -> dict:
    return {
        "job_id": job_db_id,
        "length_ft": inp.length_ft,
        "width_in": inp.width_in,
        "height_in": inp.height_in,
        "waste_ft": inp.waste_ft,
        "timestamp": inp.timestamp
    }

def output_to_dict(out, job_db_id: int, input_id_map: dict) -> dict:
    # input_id_map: input_index → DB id
    db_input_id = input_id_map.get(out.input_id) if out.input_id is not None else None
    return {
        "job_id": job_db_id,
        "input_id": db_input_id,
        "uid": out.uid,
        "timestamp": out.timestamp,
        "process_time_sec": out.process_time_sec
    }

def main(source_path: str):
    log.info(f"Starting parse of: {source_path}")

    db = Database(settings.DB_PATH)
    parser = BeamteqLogParser(source_path)
    jobs_data = parser.parse_logs()

    log.info(f"Found {len(jobs_data)} job(s) to process")

    for job, inputs, outputs in jobs_data:
        # 1. insert job → get its DB id
        job_dict = job_to_dict(job)
        job_id = db.insert("jobs", job_dict)
        log.info(f"Job {job.file_path} → DB id {job_id}")

        # 2. bulk insert inputs
        input_rows = [input_to_dict(inp, job_id) for inp in inputs]
        db.bulk_insert("input_materials", input_rows)

        # 3. build a map: input list index → DB id (for foreign key)
        # we just inserted them in the same order, so we can fetch the ids:
        input_ids = [row[0] for row in db.fetchall(
            "SELECT id FROM input_materials WHERE job_id = ? ORDER BY id", (job_id,))]
        input_index_to_db_id = {idx: db_id for idx, db_id in enumerate(input_ids)}

        # 4. bulk insert outputs
        output_rows = [
            output_to_dict(out, job_id, input_index_to_db_id) for out in outputs
        ]
        db.bulk_insert("output_pieces", output_rows)

    db.close()
    log.info("All done! Database is ready.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_log_or_folder>")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: path does not exist: {path}")
        sys.exit(1)

    main(path)