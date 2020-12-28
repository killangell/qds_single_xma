class ConfigData:
    def __init__(self):
        self.url = None
        self.timeout = None
        self.access_key = None
        self.secret_key = None

        self.exchange = None
        self.category = None
        self.period = None
        self.level_rate = None
        self.max_number = None

        # register
        self._qds_id = None
