import logging
import time
from pprint import pformat

from config_helper import ConfigHelper
from huobi.HuobiDMService import HuobiDM
from organized import Organized
from upath import UPath
from huobi.helpers.huobi_return_helper import HuobiReturnHelper as ru
from huobi.helpers.contract_position_info_helper import ContractPositionInfoHelper as cpi_helper


class Qds_Single_XMA:
    def __init__(self):
        self._config = None
        self._dm = None
        self._symbol_type = 'BTC'
        self._symbol_period = 'BTC_CQ'         # BTC_NQ
        self._contract_type_period = 'quarter' # next_quarter
        self._period = "4hour"
        self._xma_type = 'EMA'
        self._xma_value = 10
        self._max_number = 1
        self._trend_history = None
        self._level_rate = 20

    def init(self):
        self.init_log()
        ret = self.init_config()
        if not ret:
            return False
        return True

    def init_log(self):
        log_file = "qds_single_xma.log"
        log_backup_file = "qds_single_xma.log.backup"
        # backup a log copy, in case any error would be overwritten in a new run
        if UPath.is_file_exists(log_backup_file):
            UPath.remove(log_backup_file)

        if UPath.is_file_exists(log_file):
            UPath.rename(log_file, log_backup_file)

        logging.basicConfig(level=logging.INFO,  # 控制台打印的日志级别
                            filename=log_file,
                            filemode='w',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                            # a是追加模式，默认如果不写的话，就是追加模式
                            format='%(asctime)s : %(message)s'
                            # '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                            # 日志格式
                            )

    def init_config(self):
        config_file = "config.xml"
        config_instance = ConfigHelper(config_file)
        ret = config_instance.parse()
        if not ret:
            logging.error("Init config file error")
            return False

        logging.info("Init config file successfully")
        logging.info("Current working directory: " + UPath.get_root_dir())
        self._config = config_instance
        return True

    def start(self):
        ret = self.init()
        if not ret:
            exit(-1)

        while 1:
            ret = self.run()
            if not ret:
                time.sleep(20)
            else:
                time.sleep(60)

    def convert_timestamp(self, milliseconds):
        timestamp = float(milliseconds / 1000)
        time_local = time.localtime(timestamp)
        time_YmdHMS = time.strftime("%Y%m%d %H:%M", time_local)
        return time_YmdHMS

    def convert_timestamp_s(self, seconds):
        timestamp = int(seconds)
        time_local = time.localtime(timestamp)
        time_YmdHMS = time.strftime("%Y%m%d_%H%M%S", time_local)
        return time_YmdHMS

    def parse_kline_data(self, kline_list):
        org = Organized()
        kline_list.sort(key=lambda x: x['id'])
        for kline in kline_list:
            org.id_list.append(kline['id'])
            org.timestamp.append(self.convert_timestamp_s(kline['id']))
            org.open_list.append(kline['open'])
            org.close_list.append(kline['close'])
            org.high_list.append(kline['high'])
            org.low_list.append(kline['low'])
        return org

    def get_essential_data_table(self, key_list=[], data=[], log_str=''):
        ret = []
        row_count = len(data)
        column_count = len(key_list)
        if row_count > 0:
            ret.append(key_list)
            logging.info(log_str + " row_count=%d" % row_count)
            for r in range(0, row_count):
                i = []
                for c in range(0, column_count):
                    if 'created_at' == key_list[c]:
                        ts_str = self.convert_timestamp(data[r][key_list[c]])
                        i.append(ts_str)
                    else:
                        i.append(data[r][key_list[c]])
                logging.info(pformat({'row': r, 'data': i}, width=200, compact=True, sort_dicts=False))
                ret.append(i)
        else:
            logging.info(log_str + " row_count=0")
        return ret

    def get_all_holding_orders(self, notify=True):
        """
        {
        'status': 'ok',
        'data':
            [{
            'symbol': 'BTC',
            'contract_code': 'BTC201225',
            'contract_type': 'quarter',
            'volume': 1.0,
            'available': 0.0,
            'frozen': 1.0,
            'cost_open': 10650.0,
            'cost_hold': 10650.0,
            'profit_unreal': 3.83672482014e-05,
            'profit_rate': 0.04086111933445634,
            'lever_rate': 10,
            'position_margin': 0.000942803860970371,
            'direction': 'sell',
            'profit': 3.83672482014e-05,
            'last_price': 10606.66
            }],
        'ts': 1601645027078
        }
        """
        ret = self._dm.get_contract_position_info(self._symbol_type)
        if not ru.is_ok(ret):
            logging.warning("get_all_holding_orders failed, ret={0}".format(pformat(ret)))
            return None
        if notify:
            key_list = ['symbol',
                        'contract_code',
                        'contract_type',
                        'volume',
                        'cost_open',
                        'cost_hold',
                        'lever_rate',
                        'direction',
                        'last_price']
            ret_table = self.get_essential_data_table(key_list, ret['data'], 'Holdings orders')
        return ret

    def get_holding_orders_overview(self):
        ret = self.get_all_holding_orders()
        if ret:
            holding_buy_count = cpi_helper.get_orders_count('buy', ret)
            holding_buy_price = cpi_helper.get_price('buy', ret)
            holding_sell_count = cpi_helper.get_orders_count('sell', ret)
            holding_sell_price = cpi_helper.get_price('sell', ret)
            return holding_buy_count, holding_buy_price, holding_sell_count, holding_sell_price
        else:
            return 0, 0, 0, 0

    def run(self):
        url = self._config.config_data.url
        timeout = self._config.config_data.timeout
        access_key = self._config.config_data.access_key
        secret_key = self._config.config_data.secret_key

        dm = HuobiDM(url, access_key, secret_key)
        self._dm = dm

        ret = dm.get_contract_kline(symbol=self._symbol_period, period=self._period, size=300)
        if not ru.is_ok(ret):
            logging.error("get_contract_kline failed, ret={0}".format(pformat(ret)))
            return False

        global_data = Organized()
        global_data = self.parse_kline_data(ret['data'])
        global_data.calculate_ema(self._xma_value)

        last_index = global_data.get_len() - 2
        last_open = global_data.get_open(last_index)
        last_close = global_data.get_close(last_index)
        last_xma = global_data.get_ema(self._xma_value, last_index)
        ts = global_data.get_timestamp(last_index)

        trend = None
        if last_open < last_xma < last_close:
            trend = 'long'
        elif last_open > last_xma > last_close:
            trend = 'short'
        else:
            trend = self._trend_history

        # 趋势发生变化，撤销所有的限价挂单以及委托挂单
        logging.info(
            "routine: xma{0} time={1} open={2} xma={3} close={4}".format(self._xma_value, ts, last_open, last_xma,
                                                                         last_close))
        if self._trend_history != trend:
            logging.info("trend={0}".format(trend))
            # 获取持仓情况
            holding_buy_count, holding_buy_price, holding_sell_count, holding_sell_price = \
                self.get_holding_orders_overview()
            logging.info(
                "get_holding_orders_overview: buy count={0} price={1}, sell count={2} price={3}".format(
                            holding_buy_count, holding_buy_price, holding_sell_count, holding_sell_price))
            if trend == 'long':
                limit_holding_against_trend_count = holding_sell_count
                limit_holding_against_trend_close_direction = 'buy'
                limit_holding_on_trend_count = holding_buy_count
            elif trend == 'short':
                limit_holding_against_trend_count = holding_buy_count
                limit_holding_against_trend_close_direction = 'sell'
                limit_holding_on_trend_count = holding_sell_count
            else:
                logging.error("unexpected trend")
                return False

            # 平掉逆势持仓
            if limit_holding_against_trend_count > 0:
                logging.info("limit_holding_against_trend_count={0}".format(limit_holding_against_trend_count))
                ret = dm.send_lightning_close_position(self._symbol_type, self._contract_type_period, '',
                                                       int(limit_holding_against_trend_count),
                                                       limit_holding_against_trend_close_direction,
                                                       '', None)
                if ru.is_ok(ret):
                    limit_holding_against_trend_count = 0
                    logging.info("send_lightning_close_position successfully, direction={0}, volume={1}".format(
                        limit_holding_against_trend_close_direction, limit_holding_against_trend_count))
                else:
                    logging.error("send_lightning_close_position failed, ret={0}".format(pformat(ret)))
                    return False

            # 开顺势仓
            if limit_holding_on_trend_count == 0:
                ret = dm.send_contract_order(symbol=self._symbol_type, contract_type=self._contract_type_period, contract_code='',
                                               client_order_id='', price=None, volume=int(self._max_number),
                                               direction=limit_holding_against_trend_close_direction, offset='open', lever_rate=self._level_rate,
                                               order_price_type='opponent')
                if ru.is_ok(ret):
                    logging.info(
                        "send_contract_order successfully, volume={0} direction={1}".format(
                            int(self._max_number), limit_holding_against_trend_close_direction))
                else:
                    logging.error("send_contract_order failed, ret={0}".format(pformat(ret)))
                    return False

            self._trend_history = trend

        return True


if __name__ == "__main__":
    qds = Qds_Single_XMA()
    qds.start()