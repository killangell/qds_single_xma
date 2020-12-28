import logging


class ContractOpenOrdersHelper:
    """
    返回参数
    参数名称	            是否必须	类型	描述	取值范围
    status	            true	string	请求处理结果
    <list>(属性名称: data)
    <orders>
    symbol	            true	string	品种代码
    contract_type	    true	string	合约类型	当周:"this_week", 次周:"next_week", 当季:"quarter",次季:"next_quarter"
    contract_code	    true	string	合约代码	"BTC180914" ...
    volume	            true	decimal	委托数量
    price	            true	decimal	委托价格
    order_price_type	true	string	订单报价类型 "limit":限价 "opponent":对手价 "post_only":只做maker单,post only下单只受用户持仓数量限制
    order_type	        true	int	订单类型，1:报单 、 2:撤单 、 3:强平、4:交割
    direction	        true	string	"buy":买 "sell":卖
    offset	            true	string	"open":开 "close":平
    lever_rate	        true	int	杠杆倍数	1\5\10\20
    order_id	        true	bigint	订单ID
    order_id_str	    true	string	String订单ID
    client_order_id	    true	long	客户订单ID
    created_at	        true	long	订单创建时间
    trade_volume	    true	decimal	成交数量
    trade_turnover	    true	decimal	成交总金额
    fee	                true	decimal	手续费
    trade_avg_price	    true	decimal	成交均价
    margin_frozen	    true	decimal	冻结保证金
    profit	            true	decimal	收益
    status	            true	int	订单状态	(3未成交 4部分成交 5部分成交已撤单 6全部成交 7已撤单)
    order_source	    true	string	订单来源
    fee_asset	        true	string	手续费币种	（"BTC","ETH"...）
    </orders>
    total_page	        true	int	总页数
    current_page	    true	int	当前页
    total_size	        true	int	总条数
    </list>
    ts	                true	long	时间戳
    """

    @staticmethod
    def log_all_orders(direction, ret):
        for i in range(0, ret['data']['total_size']):
            if ret['data']['orders'][i]['direction'] == direction:
                logging.info("contract_openorders: direction={0} symbol={1}.{2} volume={3} price={4}".format(
                    ret['data']['orders'][i]['direction'],
                    ret['data']['orders'][i]['symbol'],
                    ret['data']['orders'][i]['contract_type'],
                    ret['data']['orders'][i]['volume'],
                    ret['data']['orders'][i]['price']))

    @staticmethod
    def get_orders_count(direction, offset, ret):
        count = 0
        for i in range(0, ret['data']['total_size']):
            if ret['data']['orders'][i]['direction'] == direction and ret['data']['orders'][i]['offset'] == offset:
                count += ret['data']['orders'][i]['volume']
        return count

    @staticmethod
    def get_price(direction, offset, ret):
        data = []
        for i in range(0, ret['data']['total_size']):
            if ret['data']['orders'][i]['direction'] == direction and ret['data']['orders'][i]['offset'] == offset:
                price = ret['data']['orders'][i]['price']
                data.append(price)
        return data