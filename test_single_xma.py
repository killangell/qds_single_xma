import logging
from enum import IntEnum
from pprint import pprint, pformat
import pandas as pd

from organized import Organized


class XMAType(IntEnum):
    XMA_INVALID = -1
    MA = 0
    EMA = 1


XMATypeDict = {
    XMAType.XMA_INVALID: 'xma',
    XMAType.MA: 'ma',
    XMAType.EMA: 'ema',
}

class Operate:
    def __init__(self, price, direction, time):
        self._price = price
        self._direction = direction
        self._time = time


class TestSingleXMA:
    def __init__(self, xma_type, xma_value, data=Organized(), verbose=False):
        self._xma_type = xma_type
        self._period = xma_value
        self._kline_data = data
        self._verbose = verbose

    def run(self):
        profit_sum = 0
        positive_cnt = 0
        negative_cnt = 0
        opt_cnt = 0
        opt_list = []
        opt_cur = Operate(0, 0, 0)
        opt_his = Operate(0, 0, 0)
        data_len = self._kline_data.get_len()
        for i in range(0, data_len):
            xma = 0
            if self._xma_type == XMAType.MA:
                xma = self._kline_data.get_ma(self._period, i)
            else:
                xma = self._kline_data.get_ema(self._period, i)

            if pd.isnull(xma):
                continue
            open = self._kline_data.get_open(i)
            close = self._kline_data.get_close(i)
            high = self._kline_data.get_high(i)
            low = self._kline_data.get_low(i)
            time = self._kline_data.get_timestamp(i)
            # if low <= xma <= high:
            if open <= xma <= close or close <= xma <= open:
                if close > xma:
                    opt_cur = Operate(close, True, time)
                else:
                    opt_cur = Operate(close, False, time)

                if opt_his._price > 0:
                    profit = 0
                    if opt_his._direction != opt_cur._direction:
                        if close > xma:
                            profit = opt_his._price - opt_cur._price
                        else:
                            profit = opt_cur._price - opt_his._price

                        profit_sum += profit
                        opt_cnt += 1
                        opt_item = [opt_his, opt_cur, profit, profit_sum]
                        opt_list.append(opt_item)
                        if profit > 0:
                            positive_cnt += 1
                        else:
                            negative_cnt += 1

                        opt_his = opt_cur
                else:
                    if close > xma:
                        opt_his = Operate(close, True, time)
                    else:
                        opt_his = Operate(close, False, time)

        if self._verbose:
            print("profit:{0} positive:{1} negative:{2}".format(profit_sum, positive_cnt, negative_cnt))
            for i in range(0, len(opt_list)):
                his, cur, prft, prft_sum = opt_list[i][0], opt_list[i][1], opt_list[i][2], opt_list[i][3]
                print("open:{0},{1} close:{2},{3} dir={4} profit={5} profit_sum={6} ".format(his._time, his._price,
                                                                             cur._time, cur._price, his._direction,
                                                                             prft, prft_sum))
        return profit_sum, positive_cnt, negative_cnt


def TestSingleXMALoop(data=Organized()):
    ret_list = []
    xma_value_range = range(5, 300)
    for xma_value in xma_value_range:
        data.calculate_ema(xma_value)
        data.calculate_ma(xma_value)

    for xma_value in xma_value_range:
        test_obj = TestSingleXMA(XMAType.MA, xma_value, data)
        ret = test_obj.run()
        ret_list.append({'type': 'ma{0}'.format(xma_value), 'result': ret})

    for xma_value in xma_value_range:
        test_obj = TestSingleXMA(XMAType.EMA, xma_value, data)
        ret = test_obj.run()
        ret_list.append({'type': 'ema{0}'.format(xma_value), 'result': ret})

    ret_list.sort(key=lambda x: x['result'])
    for ret in ret_list:
        pprint(ret)
        logging.info("{0}".format(pformat(ret)))
