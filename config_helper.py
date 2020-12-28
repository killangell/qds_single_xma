import logging

from xml_data import ConfigData
from upath import UPath
from xml_helper import *


class ConfigHelper:
    def __init__(self, xml_file):
        self._config_file = xml_file
        self._config_data = ConfigData()
        self._config_tree = None

    def _get_node_value(self, path):
        node = self._get_first_node(path)
        if node != None:
            return node.text

    def parse(self):
        ret = UPath.is_file_exists(self._config_file)
        if not ret:
            logging.error("Config file {0} doesn't exist".format(self._config_file))
            return False

        self._config_tree = read_xml(self._config_file)

        self._config_data.url = self._get_node_value("exchange/huobi/url")
        self._config_data.timeout = int(self._get_node_value("exchange/huobi/timeout"))
        self._config_data.access_key = self._get_node_value("exchange/huobi/access_key")
        self._config_data.secret_key = self._get_node_value("exchange/huobi/secret_key")

        self._config_data.exchange = int(self._get_node_value("params/exchange"))
        self._config_data.category = int(self._get_node_value("params/category"))
        self._config_data.period = int(self._get_node_value("params/period"))
        self._config_data.level_rate = int(self._get_node_value("params/level_rate"))
        self._config_data.max_number = int(self._get_node_value("params/max_number"))

        return True

    def _get_first_node(self, path):
        nodes = find_nodes(self._config_tree, path)
        if len(nodes) > 0:
            return nodes[0]
        else:
            return None

    def write_node(self, path, value):
        node = self._get_first_node(path)
        if node != None:
            node.text = value

    def save(self):
        write_xml(self._config_tree, self._config_file)

    @property
    def config_data(self):
        return self._config_data

if __name__ == "__main__":
    helper = ConfigHelper('config.xml')
    helper.parse()
    test_node_list = {
        "exchange/huobi/url": "testurl.com",
        "exchange/huobi/timeout": "2",
        "exchange/huobi/access_key": "test_access_key",
        "exchange/huobi/secret_key": "test_secret_key",
        "params/exchange": "2",
        "params/category": "2",
        "params/period": "2",
        "params/level_rate": "2",
        "params/max_number": "2",
        "params/strategy/strategy_type": "2",
        "params/strategy/single_xma/xma_type": "2",
        "params/strategy/single_xma/xma_value": "2",
        "params/strategy/single_xma/open_type": "2",
        "params/strategy/single_xma/open_at_str": "test_open_at_str",
        "params/strategy/single_xma/close_type": "2",
        "params/strategy/single_xma/close_at_str": "test_close_at_str"
    }
    for path, value in test_node_list.items():
        helper.write_node(path, 'init')
        helper.save()
    for path, value in test_node_list.items():
        helper.write_node(path, value)
        helper.save()
        reslut = helper._get_node_value(path)
        assert (value == reslut)
        print("{0} test passed".format(path))
