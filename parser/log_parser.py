# parser/log_parser.py
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from .models import Job, InputMaterial, OutputPiece
from .log_reader import read_log_files
from utils.time_utils import parse_timestamp, duration_minutes
from utils.converters import mm_to_feet, mm_to_inches


class BeamteqLogParser:
    def __init__(self, source: Path | str):
        self.source = Path(source)

    # ------------------------------------------------------------------ public
    def parse_logs(self) -> List[Tuple[Job, List[InputMaterial], List[OutputPiece]]]:
        jobs: List[Tuple[Job, List[InputMaterial], List[OutputPiece]]] = []

        job: Optional[Job] = None
        inputs: List[InputMaterial] = []
        inputs_planned: List[InputMaterial] = []
        outputs: List[OutputPiece] = []
        component_to_input: Dict[int, int] = {}      # UID → input index
        last_output_full_ts: Optional[str] = None    # full "dd.mm.yyyy HH:MM:SS"
        current_rohteil_bauteil: Optional[int] = None

        file_path = None
        uploaded_date = None
        uploaded_time = None          # ← time only

        for line, log_file in read_log_files(self.source):
            ts_full, level, msg = self._split_line(line)      # full ts = "dd.mm.yyyy HH:MM:SS"
            date_part, time_part = ts_full.split(maxsplit=1)   # split once → date, time

            # ---------- NEW JOB ----------
            if msg.startswith("File:"):
                file_path = msg.split("File:", 1)[1].strip()
                uploaded_date=date_part
                uploaded_time=time_part          # ← time only
                continue

            if "MPRWriter" in msg:
                continue

            # ---------- Production block ----------
            if msg == "--- production model begin ---":
                if job is not None:
                    inputs = inputs_planned[:len(outputs)]
                    self._finalize_job(job, inputs, outputs, jobs,
                                       component_to_input, last_output_full_ts)
                    
                job = Job(
                    file_path=file_path,
                    uploaded_date=date_part,
                    uploaded_time=time_part          # ← time only
                )

                inputs_planned = []
                inputs = []
                outputs = []
                component_to_input = {}
                last_output_full_ts = None
                current_bauteil = -1
                current_abtransport = -1
                rohteil_indexs = {}

                job.start_time = ts_full
                continue

            if msg == "--- production model end ---":
                continue

            # ---------- Input (Rohteil) ----------
            if "Rohteil" in msg:
                m_rohteil = re.search(r"Rohteil\s+(\d+)", msg)
                m_dims = re.search(r"UID\s+(\d+)\s+([\d\.]+)x([\d\.]+)x([\d\.]+).*ResidualLength=([\d\.]+)", msg)
                if m_rohteil and m_dims:
                    uid, l_mm, w_mm, h_mm, waste_mm = m_dims.groups()
                    inp = InputMaterial(
                        job_id=0,
                        length_ft=mm_to_feet(float(l_mm)),
                        width_in=mm_to_inches(float(w_mm)),
                        height_in=mm_to_inches(float(h_mm)),
                        waste_ft=mm_to_feet(float(waste_mm)),
                        timestamp=time_part
                    )
                    inputs_planned.append(inp)
                continue

            # ---------- Output (Abtransport) ----------
            if "Abtransport Bauteil" in msg:
                current_abtransport += 1
                m = re.search(r"Bauteil\s+(\d+).*LfdNr\s+(\d+)", msg)
                if m:
                    bauteil_num = int(m.group(1))
                    lfd_nr = int(m.group(2))
                    input_idx = component_to_input.get(current_abtransport) 
                    out = OutputPiece(
                        job_id=0,
                        input_id=input_idx,
                        uid=bauteil_num,
                        timestamp=time_part,
                        process_time_sec=0.0
                    )
                    outputs.append(out)
                    last_output_full_ts = ts_full
                continue

            if "Bauteil 1." in msg:
                current_bauteil += 1
                m = re.search(r"Bauteil 1\.\s*(\d+)\s+UID\s", msg)
                if m:
                    if len(inputs_planned) > 0:
                        component_to_input[current_bauteil] = len(inputs_planned) - 1
                continue

        # ---------- final job ----------
        job.end_time = last_output_full_ts

        if job is not None:
            inputs = inputs_planned[:len(outputs)]
            self._finalize_job(job, inputs, outputs, jobs,
                               component_to_input, last_output_full_ts)

        return jobs

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _split_line(line: str) -> Tuple[str, str, str]:
        """Return (full_timestamp, level, message)."""
        parts = line.split("\t")
        if len(parts) < 4:
            return "", "", line.strip()
        date, time, level, *msg = parts
        full_ts = f"{date} {time}"
        return full_ts, level.strip(), " ".join(msg).strip()

    def _finalize_job(self,
                    job: Job,
                    inputs: List[InputMaterial],
                    outputs: List[OutputPiece],
                    out_list: list,
                    component_map: Dict[int, int],
                    last_output_full_ts: Optional[str]):
        """Calculate totals and duration using time_utils."""
        # ----- totals -----
        job.total_pieces_in = len(inputs)
        job.total_pieces_out = len(outputs)
        job.total_inputs_length = sum(i.length_ft for i in inputs)
        job.total_waste = sum(i.waste_ft for i in inputs)
        job.total_outputs_length = job.total_inputs_length - job.total_waste

        # ----- SAVE ORIGINAL FULL TIMESTAMPS -----
        upload_full = f"{job.uploaded_date} {job.uploaded_time}"
        start_full = job.start_time
        end_full = last_output_full_ts
        
        # ----- CALCULATE DURATION (using full timestamps) -----
        if start_full and end_full and upload_full:
            try:
                
                upload_dt = parse_timestamp(upload_full)
                start_dt = parse_timestamp(start_full)   # "22.09.2025 09:28:27"

                end_dt   = parse_timestamp(end_full)     # "22.09.2025 09:41:32"
                job.duration_minutes = duration_minutes(upload_dt, end_dt)
                job.cutting_duration_minutes = duration_minutes(start_dt, end_dt)

                # NOW convert to time-only for DB
                job.start_time = start_dt.strftime("%H:%M:%S")
                job.end_time   = end_dt.strftime("%H:%M:%S")
            except Exception as e:
                print(f"[ERROR] Duration calc failed: {e}")
                job.duration_minutes = 0.0
                job.start_time = start_full.split()[1] if " " in start_full else ""
                job.end_time   = end_full.split()[1] if " " in end_full else ""
        else:
            job.duration_minutes = 0.0
            job.start_time = start_full.split()[1] if start_full and " " in start_full else ""
            job.end_time   = ""

        out_list.append((job, inputs, outputs))