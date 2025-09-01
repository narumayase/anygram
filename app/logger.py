import logging
from app.config import LOG_LEVEL

numeric_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

logger = logging.getLogger("mylogger")
logger.setLevel(numeric_level)
logger.propagate = False  # evita duplicar logs si hay root logger

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] [request_id=%(request_id)s] %(name)s: %(message)s"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

class RequestLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"]["request_id"] = self.extra.get("request_id", "unknown")
        return msg, kwargs
    
log = RequestLoggerAdapter(logger, extra={"request_id": "unknown"})