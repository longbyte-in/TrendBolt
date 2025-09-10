from __future__ import annotations

import logging
import os
from typing import Optional

from .config import get_settings


def setup_logging(level: Optional[str] = None) -> None:
    s = get_settings()
    log_level = (level or s.log_level or "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


