import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('log_config')
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    'crm.log',
    maxBytes=5*1024*1024,
    backupCount=1
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)