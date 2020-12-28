import logging
import time
from enum import IntEnum
from pprint import pformat

from config_helper import ConfigHelper
from huobi.HuobiDMService import HuobiDM
from organized import Organized
from test_single_xma import TestSingleXMALoop, TestSingleXMA, XMAType
from upath import UPath
from huobi.helpers.huobi_return_helper import HuobiReturnHelper as ru
from huobi.helpers.contract_position_info_helper import ContractPositionInfoHelper as cpi_helper


class Period(IntEnum):
    PERIOD_INVALID = -1
    MINUTES_1 = 0
    MINUTES_5 = 1
    MINUTES_10 = 2
    MINUTES_15 = 3
    MINUTES_30 = 4
    HOURS_1 = 5
    HOURS_2 = 6
    HOURS_4 = 7
    HOURS_6 = 8
    HOURS_12 = 9
    DAYS_1 = 10
    DAYS_2 = 11
    DAYS_3 = 12
    DAYS_5 = 13
    WEEKS_1 = 14


PeriodDict = {
    Period.MINUTES_1: '1min',
    Period.MINUTES_5: '5min',
    Period.MINUTES_15: '15min',
    Period.MINUTES_30: '30min',
    Period.HOURS_1: '60min',
    Period.HOURS_4: '4hour',
    Period.DAYS_1: '1day',
    Period.WEEKS_1: '1week',
}


class Qds_Single_XMA_Tester:
    def __init__(self, xma_type, xma_value):
        self._config = None
        self._dm = None
        self._symbol_type = 'BTC'
        self._symbol_period = 'BTC_CQ'  # BTC_NQ
        self._contract_type_period = 'quarter'  # next_quarter
        self._period = Period.HOURS_4
        self._period_str = PeriodDict.get(self._period)
        self._xma_type = xma_type
        self._xma_value = xma_value
        self._max_number = 1
        self._trend_history = None
        self._level_rate = 20
        self._log_file = "{0}_{1}_{2}_{3}_test_result.log".format(self._symbol_type, self._period_str,
                                                                  self._xma_type, self._xma_value)

    def init(self):
        self.init_log()
        ret = self.init_config()
        if not ret:
            return False
        return True

    def init_log(self):
        log_file = self._log_file

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
        self.run()

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

    def datatime_to_seconds(self, str):
        import time, datetime
        timeDateStr = str # "2014-07-29 00:00:00"
        time1 = datetime.datetime.strptime(timeDateStr, "%Y-%m-%d %H:%M:%S")
        seconds_from_1970 = time.mktime(time1.timetuple())
        return seconds_from_1970

    def get_kline_data(self, fromtime='', totime=''):
        # fromtime = "2019-01-01 00:00:00"
        # totime = "2019-10-01 00:00:00"
        fromtime_seconds = int(self.datatime_to_seconds(fromtime))
        totime_seconds = int(self.datatime_to_seconds(totime))
        a = self.convert_timestamp_s(fromtime_seconds)
        b = self.convert_timestamp_s(totime_seconds)
        ret = self.get_kline_ex(fromtime_seconds, totime_seconds)
        return ret

    def get_kline_ex(self, fromtime, totime):
        ret = self._dm.get_contract_kline_ex(symbol=self._symbol_period, period=self._period_str, size=0,
                                                        fromtime=fromtime, totime=totime)
        return ret

    def get_end_time_of_day_by_period(self, period=Period.PERIOD_INVALID):
        ret = ''
        if period == Period.HOURS_4:
            ret = "20:00:00"
        elif period == Period.HOURS_1:
            ret = "23:00:00"
        elif period == Period.MINUTES_30:
            ret = "23:30:00"
        else:
            pass

        return ret

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

    def get_kline_monthly(self, period, y, m, fromD, toD, org_data):
        if fromD:
            start_datetime = "{0}-{1}-{2} 00:00:00".format(y, m, fromD)
        else:
            fromD = 1
            start_datetime = "{0}-{1}-{2} 00:00:00".format(y, m, fromD)

        end_time = self.get_end_time_of_day_by_period(period)
        if toD:
            end_datetime = "{0}-{1}-{2} {3}".format(y, m, toD, end_time)
        else:
            if m == 1 or m == 3 or m == 5 or m == 7 or m == 8 or m == 10 or m == 12:
                toD = 31
            elif m == 2:
                if y == 2020:  # 闰年
                    toD = 29
                else:
                    toD = 28
            else:
                toD = 30
            end_datetime = "{0}-{1}-{2} {3}".format(y, m, toD, end_time)

        logging.info("get_kline: {0} -> {1}".format(start_datetime, end_datetime))

        ret = self.get_kline_data(start_datetime, end_datetime)
        while not ru.is_ok(ret):
            time.sleep(5)
            logging.error("get_kline failed: {0} -> {1}, ret={2}".format(start_datetime, end_datetime, pformat(ret)))
            ret = self.get_kline_data(start_datetime, end_datetime)

        self.parse_kline_data_ex(ret['data'], org_data)

    def get_all_kline(self, period=Period.HOURS_1):
        # 最大2000条数据
        # 单位    每次可获取
        # 天：    2000/365=5 5年，2000足够
        # 4hour： 2000/6=333 6个月
        # 60min： 2000/24=83 2个月
        # 30min： 2000/48=41 1个月
        fromY = 2018
        fromM = 11
        fromD = 10
        toY = 2020
        toM = 12
        toD = 20

        org_data = Organized()
        if fromY != toY:
            # 获取第一个月的K线
            if fromM < 12:
                self.get_kline_monthly(period, fromY, fromM, fromD, None, org_data)
            # 获取第一年的剩余整月K线
            for m in range(fromM + 1, 13):
                fromD = 1
                self.get_kline_monthly(period, fromY, m, fromD, None, org_data)
        # 获取第二年整年整月K线
        if (fromY + 1) < toY:
            for y in range(fromY + 1, toY):
                for m in range(1, 13):
                    self.get_kline_monthly(period, y, m, None, None, org_data)
        # 获取最后一年整月K线
        for m in range(1, toM):
            self.get_kline_monthly(period, toY, m, None, None, org_data)
        # 获取最后一年最后一个月K线
        self.get_kline_monthly(period, toY, toM, None, toD, org_data)

        return org_data

    def run(self):
        url = self._config.config_data.url
        timeout = self._config.config_data.timeout
        access_key = self._config.config_data.access_key
        secret_key = self._config.config_data.secret_key

        dm = HuobiDM(url, access_key, secret_key)
        self._dm = dm

        if 0:
            ret = dm.get_contract_kline(symbol=self._symbol_period, period=self._period_str, size=2000)
            if not ru.is_ok(ret):
                logging.error("get_contract_kline failed, ret={0}".format(pformat(ret)))
                return False

            global_data = Organized()
            global_data = self.parse_kline_data(ret['data'])

        global_data = Organized()
        global_data = self.get_all_kline(self._period)

        if self._xma_type == XMAType.XMA_INVALID:
            TestSingleXMALoop(global_data)
        else:
            test_obj = TestSingleXMA(self._xma_type, self._xma_value, global_data)
            test_obj.run()


if __name__ == "__main__":
    qds = Qds_Single_XMA_Tester(XMAType.XMA_INVALID, 0)
    qds.start()
