import logging


class ContractPositionInfoHelper:
    """
    请求参数
    参数名称	是否必须	类型	描述	默认值	取值范围
    symbol	false	string	品种代码		支持大小写,""BTC","ETH"...如果缺省，默认返回所有品种
    
    Response:
    {
      "status": "ok",
      "data": [
        {
          "symbol": "BTC",
          "contract_code": "BTC180914",
          "contract_type": "this_week",
          "volume": 1,
          "available": 0,
          "frozen": 0.3,
          "cost_open": 422.78,
          "cost_hold": 422.78,
          "profit_unreal": 0.00007096,
          "profit_rate": 0.07,
          "profit": 0.97,
          "position_margin": 3.4,
          "lever_rate": 10,
          "direction":"buy",
          "last_price":7900.17
         }
        ],
     "ts": 158797866555
    }
    
    返回参数
    参数名称	        是否必须	类型	描述	取值范围
    status	        true	string	请求处理结果	"ok" , "error"
    <list>(属性名称: data)				
    symbol	        true	string	品种代码	"BTC","ETH"...
    contract_code	true	string	合约代码	"BTC180914" ...
    contract_type	true	string	合约类型	当周:"this_week", 次周:"next_week", 当季:"quarter", 次季:"next_quarter"
    volume	        true	decimal	持仓量	
    available	    true	decimal	可平仓数量	
    frozen	        true	decimal	冻结数量	
    cost_open	    true	decimal	开仓均价	
    cost_hold	    true	decimal	持仓均价	
    profit_unreal	true	decimal	未实现盈亏	
    profit_rate	    true	decimal	收益率	
    profit	        true	decimal	收益	
    position_margin	true	decimal	持仓保证金	
    lever_rate	    true	int	杠杠倍数	
    direction	    true	string	"buy":买 "sell":卖	
    last_price	    true	decimal	最新价	
    </list>				
    ts	            true	long	响应生成时间点，单位：毫秒	
    """

    """
    @staticmethod
    def log_all_orders(direction, ret):
        for i in range(0, ru.get_data_list_size(ret)):
            if ru.get_data_item_field(i, 'direction', ret) == direction:
                logging.debug("contract_position_info: direction={0} symbol={1}.{2} volume={3} cost_hold={4}".format(
                    ru.get_data_item_field(i, 'direction', ret),
                    ru.get_data_item_field(i, 'symbol', ret),
                    ru.get_data_item_field(i, 'contract_type', ret),
                    ru.get_data_item_field(i, 'volume', ret),
                    ru.get_data_item_field(i, 'cost_hold', ret)))
    """

    @staticmethod
    def get_orders_count(direction, ret):
        count = 0
        for i in range(0, len(ret['data'])):
            if ret['data'][i]['direction'] == direction:
                count += ret['data'][i]['volume']
        return count

    @staticmethod
    def get_price(direction, ret):
        data = 0
        for i in range(0, len(ret['data'])):
            if ret['data'][i]['direction'] == direction:
                data += ret['data'][i]['cost_hold']
        return data
