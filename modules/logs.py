import logging, os
from logging.handlers import RotatingFileHandler

logging.addLevelName(logging.WARNING, 'WARN')

# Singleton logger instance that will be shared across modules
logger_instance = None

class MyLogger:
    class CustomFormatter(logging.Formatter):
        def __init__(self, screen_width, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.screen_width = screen_width
        
        def format(self, record):
            levelname = record.levelname
            if levelname == "INFO" or levelname == "WARN":
                self._style._fmt = f"[%(asctime)s]  [{levelname}]     |%(message)-{self.screen_width}s|"
            else:
                self._style._fmt = f"[%(asctime)s]  [{levelname}]    |%(message)-{self.screen_width}s|"
            return super().format(record)

    def __init__(self, separating_character='=', screen_width=100, log_file='assistant.log', debug=False):
        # Get logs directory from config with safe global access
        try:
            if 'config' in globals() and globals()['config'].get('logs'):
                self.log_dir = globals()['config']['logs']
            else:
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.log_dir = os.path.join(parent_dir, 'logs')
        except:
            # Fallback to default path if anything goes wrong
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.log_dir = os.path.join(parent_dir, 'logs')
        
        os.makedirs(self.log_dir, exist_ok=True)
        self.separating_character = separating_character
        self.screen_width = screen_width
        self.log_file = os.path.join(self.log_dir, log_file)
        
        # Use the root logger to ensure all modules use the same logger
        self.logger = logging.getLogger()
        
        # Set log level based on debug parameter
        log_level = logging.DEBUG if debug else logging.INFO
        self.logger.setLevel(log_level)
        
        # Clear any existing handlers to avoid duplicates
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
            
        self.main_handler = self._get_handler(self.log_file)

        # Create console handler with the same level as the logger
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = self.CustomFormatter(self.screen_width)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Create file handler with the same level as the logger
        file_handler = self.main_handler
        file_handler.setLevel(log_level)
        file_formatter = self.CustomFormatter(self.screen_width)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def info(self, msg):
        self.logger.info(msg)
        
    def info_center(self, msg):
        self.logger.info(self._centered(str(msg)))
        
    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
        
    def print(self, msg, error=False, warning=False, debug=False):
        if error:
            self.error(msg)
        elif warning:
            self.warning(msg)
        elif debug:
            self.debug(msg)
        else:
            self.info(msg)
                
    def _centered(self, text, sep=" ", side_space=True, left=False):
        if len(text) > self.screen_width - 2:
            return text
        space = self.screen_width - len(text) - 2
        text = f"{' ' if side_space else sep}{text}{' ' if side_space else sep}"
        if space % 2 == 1:
            text += sep
            space -= 1
        side = int(space / 2) - 1
        final_text = f"{text}{sep * side}{sep * side}" if left else f"{sep * side}{text}{sep * side}"
        return final_text

    def separator(self, text=None, space=True, border=True, debug=False, side_space=True, left=False):
        sep = " " if space else self.separating_character
        border_text = f"{self.separating_character * self.screen_width}"
        if border:
            self.print(border_text, debug=debug)
        if text:
            text_list = text.split("\n")
            for t in text_list:
                msg = f"{sep}{self._centered(t, sep=sep, side_space=side_space, left=left)}{sep}"
                self.print(msg, debug=debug)
            if border:
                self.print(border_text, debug=debug)

    def _get_handler(self, log_file, count=9):
        handler = RotatingFileHandler(log_file, delay=True, mode="a", backupCount=count, encoding="utf-8")
        formatter = logging.Formatter("[%(asctime)s]  [%(levelname)s]  |%(message)-{0}s|".format(self.screen_width))
        handler.setFormatter(formatter)
        if os.path.isfile(log_file):
            # Only attempt to remove a handler that exists
            for existing_handler in self.logger.handlers[:]:
                if isinstance(existing_handler, RotatingFileHandler) and existing_handler.baseFilename == handler.baseFilename:
                    self.logger.removeHandler(existing_handler)
            handler.doRollover()
        return handler


def get_logger(debug=None):
    """
    Get or create the singleton logger instance.
    If debug is provided, it will update the logger's debug setting.
    
    Args:
        debug (bool, optional): If provided, update the logger's debug setting
        
    Returns:
        MyLogger: The singleton logger instance
    """
    global logger_instance
    
    if logger_instance is None:
        logger_instance = MyLogger(debug=debug if debug is not None else False)
    elif debug is not None:
        # Update existing logger with new debug setting
        log_level = logging.DEBUG if debug else logging.INFO
        logger_instance.logger.setLevel(log_level)
        
        # Also update all handlers to ensure consistency
        for handler in logger_instance.logger.handlers:
            handler.setLevel(log_level)
        
    return logger_instance
