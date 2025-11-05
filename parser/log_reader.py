# parser/log_reader.py
from pathlib import Path
from typing import Generator, Tuple
from config import settings


def _read_single_file(file_path: Path, encoding: str) -> Generator[Tuple[str, Path], None, None]:
    """Yield non-empty stripped lines from a single file."""
    try:
        with open(file_path, "r", encoding=encoding) as f:
            for raw in f:
                line = raw.strip()
                if line:
                    yield line, file_path
    except Exception as e:
        print(f"Error reading {file_path}: {e}")


def read_log_files(
    path: Path | str,
    encoding: str = settings.LOG_ENCODING
) -> Generator[Tuple[str, Path], None, None]:
    """
    Yield (line, file_path) for:
      - Single .txt file
      - All .txt files in a directory (sorted)
    """
    path = Path(path)

    if path.is_file() and path.suffix.lower() == ".txt":
        yield from _read_single_file(path, encoding)

    elif path.is_dir():
        txt_files = sorted([f for f in path.glob("*.txt") if f.is_file()])
        if not txt_files:
            print(f"No .txt files found in {path}")
            return
        for txt_file in txt_files:
            yield from _read_single_file(txt_file, encoding)

    else:
        raise ValueError(f"Invalid path: {path}. Must be .txt file or directory.")