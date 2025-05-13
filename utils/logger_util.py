from logging import Logger, Formatter, StreamHandler, FileHandler
import logging
import pandas as pd
from pandas import DataFrame
from typing import Dict, List
import re

class LoggerUtil:
    def __init__(self, log_filename: str):
        self.log_filename = log_filename
        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.console_handler = self._create_stream_handler(formatter)
        self.file_handler = self._create_file_handler(log_filename, formatter)                
        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.file_handler)    


    def get_log_file_content_as_dataframe(self) -> DataFrame:
        # Regular expression to parse log lines (Adjust based on your log format)
        logs_from_file = self._read_log_file(self.log_filename)
        df = DataFrame(logs_from_file)
        # Convert timestamp column to datetime format
        # print(f"!!! {df}")
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S,%f", errors="coerce")
        return df

    # example line from log: {'level': 'INFO', 'message': 'test123', 'timestamp': '2025-02-10 14:58:38,916'}
    def _read_log_file(self, log_file_path: str) -> List[Dict[str, any]]:
        log_pattern = re.compile(r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (?P<level>\w+) - (?P<message>.*)')
        parsed_logs = []
        with open(log_file_path, "r") as file:
            for line in file:
                match = log_pattern.match(line)
                if match:
                    parsed_logs.append(match.groupdict())
        return parsed_logs

    def _create_file_handler(self, log_filename: str, formatter: Formatter) -> FileHandler:
        file_handler = FileHandler(log_filename)
        file_handler = self._init_handler(file_handler, formatter, logging.INFO)
        return file_handler
        
    def _create_stream_handler(self, formatter: Formatter) -> StreamHandler:
        stream_handler = StreamHandler()
        stream_handler = self._init_handler(stream_handler, formatter, logging.DEBUG)
        return stream_handler
        
    def _init_handler(self, handler, formatter: Formatter, log_level: int) -> StreamHandler:
        # Create console handler for logging to console        
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        return handler
    
    def log_debug(self, message: str):
        self.logger.debug(message)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_warning(self, message: str):
        self.logger.warning(message)

    def log_error(self, message: str):
        self.logger.error(message)
        
    def log_critical(self, message: str):
        self.logger.critical(message)
