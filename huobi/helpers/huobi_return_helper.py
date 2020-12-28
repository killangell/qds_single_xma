
class HuobiReturnHelper:
    @staticmethod
    def get_status(return_val):
        return return_val['status']
    @staticmethod
    def is_ok(return_val):
        return HuobiReturnHelper.get_status(return_val) == 'ok'

    def get_err_code(self, return_val):
        return return_val['err_code']

    def get_err_msg(self, return_val):
        return return_val['err_msg']

    def is_no_order(self, return_val):
        return self.get_err_code(return_val) == 1051

    def get_ts(self, return_val):
        return return_val['ts']

    def get_data_all(self, return_val):
        return return_val['data']

    def get_data_list_size(self, return_val):
        return len(self, self.get_data_all(return_val))

    def get_data_item(self, index, return_val):
        return self.get_data_all(return_val)[index]

    def get_data_item_field(self, index, field, return_val):
        return self.get_data_item(index, return_val)[field]
