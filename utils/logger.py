import logging
from pathlib import Path

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """Create a logger that writes to a file and stdout."""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(formatter)

    # Stream handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

log = setup_logger(
    name="beamteq_parser",
    log_file="data/output/parser.log"
)