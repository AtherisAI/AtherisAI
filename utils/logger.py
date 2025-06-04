import logging
import os
from datetime import datetime
from typing import Optional

class AtherisLogger:
    def __init__(self, name: str, log_dir: str = "logs"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        log_filename = f"{name}_{datetime.utcnow().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(os.path.join(self.log_dir, log_filename))
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')

        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.logger.debug("Logger initialized.")

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)


# Example usage
if __name__ == "__main__":
    logger = AtherisLogger("agent_system")

    logger.debug("This is a debug message.")
    logger.info("System initialized.")
    logger.warning("Possible inconsistency detected.")
    logger.error("Failed to fetch Solana RPC data.")
    logger.critical("Critical failure in agent coordination loop.")
