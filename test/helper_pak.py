
from datetime import datetime

class BasicLogger:
    def __init__(self, logfile_name):
        self.logfile_name = logfile_name
        self.level = "INFO"
        with open(self.logfile_name, 'w') as lf:
            lf.write("<timestamp>:INFO:bodonka:in-a-gadda-da-veeda plays on for eons.\n")

    def write(self, msg):
        timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
        with open(self.logfile_name, 'a') as lf:
            lf.write(f"{timestamp}:{self.level}:rufus:{msg}\n")

    def __getattr__(self, name):
        def output(message):
            if name in ['debug', 'info', 'warn', 'fatal', 'any']:
                self.write(message)
        return output

def excErrorMessage(excinfo):
    """
        At some point in time excinfo.value.args[0] was the interesting part
        but now the appropriate thing is str(excinfo.value)
    """
    return str(excinfo.value)

