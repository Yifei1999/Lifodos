import logging
from logging.handlers import TimedRotatingFileHandler
from os.path import dirname, exists
import os

logging.basicConfig(encoding='utf-8')

root_path = dirname(dirname(__file__))

log_path = root_path + f"/logger/history/app.log"
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# initialize a new logger for other packages to import
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=30)
file_handler.suffix = "%Y-%m-%d.log"
file_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# 创建一个格式化器
formatter = logging.Formatter('[%(asctime)s] - [%(levelname)s] - [%(filename)s:%(lineno)d] %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# 将处理器添加到 logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# add production environment logger
sys_log_path = "/export"
if exists(sys_log_path):
    log_path = sys_log_path + f"/app_detail.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    sys_file_handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=30)
    sys_file_handler.suffix = "%Y-%m-%d"
    sys_file_handler.setLevel(logging.DEBUG)
    sys_file_handler.setFormatter(formatter)
    logger.addHandler(sys_file_handler)

    log_path = sys_log_path + f"/app.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    sys_file_handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=30)
    sys_file_handler.suffix = "%Y-%m-%d"
    sys_file_handler.setLevel(logging.INFO)
    sys_file_handler.setFormatter(formatter)
    logger.addHandler(sys_file_handler)
    print("production environment: logger service has been enabled!")
else:
    print("production environment: logger service has been disabled!")


if __name__ == "__main__":
    logger.debug("hello my logger!")
