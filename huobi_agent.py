import logging
import time
from pprint import pformat

from exchange.agent import Agent
from exchange.huobi.HuobiDMService import HuobiDM
from exchange.huobi.ReliableHuobiDMService import ReturnUtil as hru
from exchange.huobi.helpers.contract_position_info_helper import ContractPositionInfoHelper as cpi_helper
from exchange.huobi.helpers.contract_openorders_helper import ContractOpenOrdersHelper as coo_helper
from exchange.huobi.helpers.contract_trigger_openorders_helper import ContractTriggerOpenOrdersHelper as ctoo_helper
from exchange.huobi.helpers.huobi_return_helper import HuobiReturnHelper
from models.exchange import Category, Period, PeriodDict, Exchange, get_period_str_by_period
from models.globals import set_global_holding_orders, set_global_limit_pending_orders, \
    set_global_trigger_pending_orders, set_global_timeout
from models.mixed import SysParams
from models.organized import Organized


class HuobiAgent(Agent):
    def __init__(self, sys_params=SysParams()):
        url = sys_params.get_url()
        timeout = sys_params.get_timeout()
        set_global_timeout(timeout)
        access_key = sys_params.get_access_key()
        secret_key = sys_params.get_secret_key()
        if Category.BTC_CQ == sys_params.get_category():
            self._symbol_type = 'BTC'
            self._symbol_period = 'BTC_CQ'
            self._contract_type_period = 'quarter'
        elif Category.BTC_CW == sys_params.get_category():
            self._symbol_type = 'BTC'
            self._symbol_period = 'BTC_CW'
            self._contract_type_period = 'week'
        else:
            logging.warning("Not support category {0}".format(sys_params.get_category()))

        if 0:
            ### ONLY for test
            self._symbol_type = 'ETH'
            self._symbol_period = 'ETH_CQ'
            ###

        self._period = get_period_str_by_period(Exchange.HUOBI, sys_params.get_period())
        if not self._period:
            logging.warning("Not support period {0}".format(sys_params.get_period()))

        self._return_helper = HuobiReturnHelper()
        self._trading_agent = HuobiDM(url, access_key, secret_key)

    @property
    def trading_agent(self):
        return self._trading_agent

    @property
    def return_helper(self):
        return self._return_helper

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

    def parse_kline_data_ex(self, kline_list, org=None):
        if not org:
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
        ret = self._trading_agent.get_contract_position_info(self._symbol_type)
        if not hru.is_ok(ret):
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
            set_global_holding_orders(ret_table)
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

    def get_all_limit_pending_orders(self, notify=True):
        """
        {
            'symbol': 'BTC',
            'contract_code': 'BTC201225',
            'contract_type': 'quarter',
            'volume': 1,
            'price': 10793.0,
            'order_price_type': 'limit',
            'order_type': 1,
            'direction': 'sell',
            'offset': 'open',
            'lever_rate': 10,
            'order_id': 761634144437858305, 'client_order_id': None,
            'created_at': 1601629330512,
            'trade_volume': 0, 'trade_turnover': 0,
            'fee': 0, 'trade_avg_price': None, 'margin_frozen': 0.000926526452330214,
            'profit': 0, 'status': 3, 'order_source': 'api',
            'order_id_str': '761634144437858305', 'fee_asset': 'BTC',
            'liquidation_type': None, 'canceled_at': None
        }
        """
        ret = self._trading_agent.get_contract_open_orders(self._symbol_type)
        if not hru.is_ok(ret):
            logging.warning("get_all_limit_pending_orders failed, ret={0}".format(pformat(ret)))
            return None
        if notify:
            key_list = ['symbol',
                        'contract_code',
                        'contract_type',
                        'volume',
                        'price',
                        'direction',
                        'offset',
                        'lever_rate',
                        'created_at']
            ret_table = self.get_essential_data_table(key_list, ret['data']['orders'], 'Limit pending orders')
            set_global_limit_pending_orders(ret_table)
        return ret

    def get_limit_pending_orders_overview(self):
        ret = self.get_all_limit_pending_orders()
        # coo_helper.log_all_orders('buy', ret)
        # coo_helper.log_all_orders('sell', ret)
        if ret:
            limit_pending_buy_open_count = coo_helper.get_orders_count('buy', 'open', ret)
            limit_pending_buy_close_count = coo_helper.get_orders_count('buy', 'close', ret)
            limit_pending_buy_open_price_list = coo_helper.get_price('buy', 'open', ret)
            limit_pending_sell_open_count = coo_helper.get_orders_count('sell', 'open', ret)
            limit_pending_sell_close_count = coo_helper.get_orders_count('sell', 'close', ret)
            limit_pending_sell_open_price_list = coo_helper.get_price('sell', 'open', ret)
            return limit_pending_buy_open_count, limit_pending_buy_open_price_list, limit_pending_buy_close_count, \
                   limit_pending_sell_open_count, limit_pending_sell_open_price_list, limit_pending_sell_close_count
        else:
            return 0, 0, 0, 0, 0, 0

    def get_all_trigger_pending_orders(self, notify=True):
        """
        {
        'orders':
            [{
            'symbol': 'BTC',
            'contract_code': 'BTC201225',
            'contract_type': 'quarter',
            'trigger_type': 'le',
            'volume': 1.0,
            'order_type': 1,
            'direction': 'buy',
            'offset': 'close',
            'lever_rate': 10,
            'order_id': 18139462,
            'order_id_str': '18139462',
            'order_source': 'api',
            'trigger_price': 10599.0,
            'order_price': 10589.0,
            'created_at': 1601646410298,
            'order_price_type': 'limit',
            'status': 2
            }],
        'total_page': 1,
        'current_page': 1,
        'total_size': 3
        }
        """
        ret = self._trading_agent.get_contract_trigger_openorders(self._symbol_type)
        if not hru.is_ok(ret):
            logging.warning("get_all_trigger_pending_orders failed, ret={0}".format(pformat(ret)))
            return None
        if notify:
            key_list = ['symbol',
                        'contract_code',
                        'contract_type',
                        'volume',
                        'direction',
                        'offset',
                        'lever_rate',
                        'trigger_price',
                        'order_price',
                        'created_at']
            ret_table = self.get_essential_data_table(key_list, ret['data']['orders'], 'Trigger pending orders')
            set_global_trigger_pending_orders(ret_table)
        return ret

    def get_trigger_pending_orders_overview(self):
        ret = self.get_all_trigger_pending_orders()
        # ctoo_helper.log_all_orders('buy', ret)
        # ctoo_helper.log_all_orders('sell', ret)
        if ret:
            trigger_pending_buy_close_count = ctoo_helper.get_orders_count('buy', 'close', ret)
            trigger_pending_sell_close_count = ctoo_helper.get_orders_count('sell', 'close', ret)
            return trigger_pending_buy_close_count, trigger_pending_sell_close_count
        else:
            return 0, 0

    def get_kline(self, size=300):
        ret = self._trading_agent.get_contract_kline(symbol=self._symbol_period, period=self._period, size=size)
        return ret

    def get_kline_ex(self, fromtime, totime):
        ret = self._trading_agent.get_contract_kline_ex(symbol=self._symbol_period, period=self._period, size=0,
                                                        fromtime=fromtime, totime=totime)
        return ret

    def send_open_limit_contracts(self, direction, price, volume, level_rate):
        ret = self._trading_agent.send_contract_order(symbol=self._symbol_type, contract_type=self._contract_type_period,
                                       contract_code='',
                                       client_order_id='', price=price, volume=int(volume),
                                       direction=direction, offset='open',
                                       lever_rate=level_rate,
                                       order_price_type='limit')
        return ret

    def send_close_limit_contracts(self, direction='', volume=0):
        ret = self._trading_agent.send_lightning_close_position(self._symbol_type, self._contract_type_period, '',
                                                                volume, direction, '', None)
        return ret

    def cancel_all_limit_pending_contracts(self):
        ret = self._trading_agent.cancel_all_contract_order(self._symbol_type)
        return ret

    def send_open_trigger_contracts(self, trigger_type, trigger_price, order_price, volume, direction, level_rate):
        ret = self._trading_agent.send_contract_trigger_order(symbol=self._symbol_type, contract_type=self._contract_type_period,
                                               contract_code=None,
                                               trigger_type=trigger_type,
                                               trigger_price=round(trigger_price),
                                               order_price=round(order_price),
                                               order_price_type='limit',
                                               volume=int(volume),
                                               direction=direction,
                                               offset='close',
                                               lever_rate=level_rate)
        return ret

    def cancel_all_trigger_contracts(self):
        ret = self._trading_agent.cancel_all_contract_trigger(self._symbol_type)
        return ret
