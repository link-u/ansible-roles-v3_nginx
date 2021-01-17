from ansible.errors import AnsibleError

class FilterModule(object):
    def filters(self):
        return {
            'combine_dict_list': self.combine_dict_list,
            'search_from_dict_list': self.search_from_dict_list,
        }

    def combine_dict_list(self, dict_list: list, key: str = 'key') -> list:
        result_list = []
        for item in dict_list:
            i = self.search(result_list, item[key])
            merge_mode = self.get(item, 'merge_mode')
            if merge_mode == 'append' or i == -1:
                result_list.append(item)
            else:
                result_list[i] = item
        return result_list

    def search_from_dict_list(self, dict_list: list, search_key: str, key: str = 'key', value: str = 'value') -> list:
        result_list = []
        for item in dict_list:
            if item[key] == search_key:
                result_list.append(item[value])
        return result_list

    def search(self, dict_list: list, search_key: str, key: str = 'key') -> int:
        for i, item in enumerate(dict_list):
            if item[key] == search_key:
                return i
        return -1

    def get(self, item: dict, key: str):
        if key in item.keys():
            return item[key]
        else:
            return None
