class MuteLogger:
    def __init__(self, params=None):
        self.params = params

    def write(self, *args, **kwargs): return True
    def any(self, *args, **kwargs): return True
    def info(self, *args, **kwargs): return True
    def error(self, *args, **kwargs): return True
    def warn(self, *args, **kwargs): return True
    def warning(self, *args, **kwargs): return True
    def verbose(self, *args, **kwargs): return True
    def debug(self, *args, **kwargs): return True

    def __getattr__(self, name):
        def muteness(*args, **kwargs):
            return True
        return muteness

###################################################################################
