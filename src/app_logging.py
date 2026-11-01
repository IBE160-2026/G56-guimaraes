import logging
import json
import os
import sys
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """Format logs as structured JSON for easy debugging and monitoring."""
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
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

def setup_app_logging(log_file: str = "app.log") -> logging.Logger:
    """Konfigurerer strukturert JSON-logging for regnskapspipelinen."""
    logger = logging.getLogger("g56_accounting")
    logger.setLevel(logging.INFO)
    
    # Unngå doble handlere ved gjenbruk
    if not logger.handlers:
        # Console handler (standard format for oversikt)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s"))
        logger.addHandler(console_handler)
        
        # File handler (strukturert JSON format)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
        
    return logger
