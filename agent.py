from models.mixed import SysParams


class Agent:
    def __init__(self, sys_params=SysParams()):
        self._return_helper = None

    def convert_timestamp(self, milliseconds):
        pass

    def convert_timestamp_s(self, seconds):
        pass

    def get_kline(self, size):
        pass

    def get_kline_ex(self, fromtime, totime):
        pass

    def parse_kline_data(self, kline_list):
        pass

    def parse_kline_data_ex(self, kline_list, org=None):
        pass

    def get_holding_orders_overview(self):
        pass

    def send_open_limit_contracts(self, direction, price, volume, level_rate):
        pass

    def get_limit_pending_orders_overview(self):
        pass

    def get_trigger_pending_orders_overview(self):
        pass

    def get_all_holding_orders(self, notify=True):
        pass

    def get_all_limit_pending_orders(self, notify=True):
        pass

    def get_all_trigger_pending_orders(self, notify=True):
        pass

    def send_close_limit_contracts(self, direction='', volume=0):
        pass

    def send_open_trigger_contracts(self, trigger_type, trigger_price, order_price, volume, direction, level_rate):
        pass

    @property
    def return_helper(self):
        return self._return_helper
