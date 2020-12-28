import logging


class ContractTriggerOpenOrdersHelper:
    """
    获取计划委托当前委托
    POST api/v1/contract_trigger_openorders
    请求参数
    属性	        数据类型	是否必填	说明
    symbol	        String	true	支持大小写,BTC,LTC...
    contract_code	String	false	支持大小写,合约code
    page_index	    int	    false	第几页，不填默认第一页
    page_size	    int	    false	不填默认20，不得多于50
    Response:
    {
     "data": {
      "current_page": 1,
      "orders": [{
       "contract_code": "BTC200925",
       "contract_type": "quarter",
       "created_at": 1585564594107,
       "direction": "buy",
       "lever_rate": 1,
       "offset": "open",
       "order_id": 1582,
       "order_id_str": "1582",
       "order_price": 100.0,
       "order_price_type": "limit",
       "order_source": "api",
       "order_type": 1,
       "status": 2,
       "symbol": "BTC",
       "trigger_price": 500.0,
       "trigger_type": "le",
       "volume": 1.0
      }],
      "total_page": 1,
      "total_size": 1
     },
     "status": "ok",
     "ts": 1585564594712
    }

    返回参数
    参数名称	            是否必须	类型	描述	取值范围
    status	            true	string	请求处理结果	"ok" , "error"
    data	            true	object	返回数据
    ts	                true	long	响应生成时间点，单位：毫秒
    data详情：
    参数名称	            是否必须	类型	描述	取值范围
    total_page	        int	true	总页数
    current_page	    int	true	当前页
    total_size	        int	true	总条数
    <list>(属性名称: orders)
    symbol	            string	true	合约品种
    contract_code	    string	true	合约代码
    contract_type	    string	true	合约类型
    trigger_type	    string	true	触发类型： ge大于等于；le小于等于
    volume	            decimal	true	委托数量
    order_type	        int	    true	订单类型：1、报单 2、撤单
    direction	        string	true	订单方向 [买(buy),卖(sell)]
    offset	            string	true	开平标志 [开(open),平(close)]
    lever_rate	        int	t   rue	    杠杆倍数 1\5\10\20
    order_id	        int	    true	计划委托单订单ID
    order_id_str	    string	true	字符串类型的订单ID
    order_source	    string	true	来源
    trigger_price	    decimal	true	触发价
    order_price	        decimal	true	委托价
    created_at	        long	true	订单创建时间
    order_price_type	string	true	订单报价类型 "limit":限价，"optimal_5":最优5档，"optimal_10":最优10档，"optimal_20":最优20档
    status	            int	    true	订单状态：1:准备提交、2:已提交、3:报单中、8：撤单未找到、9：撤单中、10：失败'
    </list>
    """

    @staticmethod
    def log_all_orders(direction, ret):
        for i in range(0, ret['data']['total_size']):
            if ret['data']['orders'][i]['direction'] == direction == direction:
                logging.info("contract_trigger_openorders: direction={0} symbol={1}.{2} volume={3} order_price={4}".format(
                    ret['data']['orders'][i]['direction'],
                    ret['data']['orders'][i]['symbol'],
                    ret['data']['orders'][i]['contract_type'],
                    ret['data']['orders'][i]['volume'],
                    ret['data']['orders'][i]['order_price']))

    @staticmethod
    def get_orders_count(direction, offset, ret):
        count = 0
        for i in range(0, ret['data']['total_size']):
            if ret['data']['orders'][i]['direction'] == direction and ret['data']['orders'][i]['offset'] == offset:
                count += ret['data']['orders'][i]['volume']
        return count

    """
    @staticmethod
    def get_order_price(direction, ret):
        data = 0
        for i in range(0, ret['data']['total_size']):
            if ret['data']['orders'][i]['direction'] == direction:
                # 理论上所有委托挂单的order_price是一样的，所以只要从其中一条记录读取就可以了
                data = ret['data']['orders'][i]['order_price']
                break
        return data
    """