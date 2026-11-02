import logging
import json
import sys
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    """Format logs as structured JSON for easy debugging and monitoring."""
    def format(self, record):
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj, ensure_ascii=False)

def setup_app_logging(log_file: str | None = None) -> logging.Logger:
    """
    Konfigurerer strukturert logging for regnskapspipelinen.
    Skriver som standard kun til minne/konsoll (stdout) for å overholde NFR-3.1 (ingen filskriving til disk).
    """
    logger = logging.getLogger("g56_accounting")
    logger.setLevel(logging.INFO)
    
    # Unngå doble handlere ved gjenbruk
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s"))
        logger.addHandler(console_handler)
        
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(JsonFormatter())
            logger.addHandler(file_handler)
            
    return logger
