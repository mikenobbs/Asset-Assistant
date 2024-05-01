import logging, os
from logging.handlers import RotatingFileHandler

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

    def __init__(self, separating_character='=', screen_width=100, log_file='assistant.log'):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.separating_character = separating_character
        self.screen_width = screen_width
        self.log_dir = os.path.join(script_dir, 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, log_file)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.main_handler = self._get_handler(self.log_file)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = self.CustomFormatter(self.screen_width)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        file_handler = self.main_handler
        file_formatter = self.CustomFormatter(self.screen_width)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    # Other methods remain unchanged
    

    def info(self, msg):
        self.logger.info(msg)
        
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

    def _get_handler(self, log_file, count=3):
        handler = RotatingFileHandler(log_file, delay=True, mode="a", backupCount=count, encoding="utf-8")
        formatter = logging.Formatter("[%(asctime)s]  [%(levelname)s]  |%(message)-{0}s|".format(self.screen_width))
        handler.setFormatter(formatter)
        if os.path.isfile(log_file):
            self.logger.removeHandler(handler)
            handler.doRollover()
        return handler
