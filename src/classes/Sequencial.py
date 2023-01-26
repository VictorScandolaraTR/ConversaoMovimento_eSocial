class Sequencial:

    def __init__(self):
        self.__sequencial = {}
    
    def add(self, keys=[]):
        auxiliary_data = self.__sequencial
        for key in keys[:-1]:
            auxiliary_data = auxiliary_data.setdefault(key, {})

        auxiliary_data[keys[-1]] = auxiliary_data.get(keys[-1], 0) + 1

        return auxiliary_data[keys[-1]]

    def get(self, keys=[]):
        value = 0
        auxiliary_data = self.__sequencial
        number_keys = len(keys)
        number_existing_keys = 0
        for key in keys:
            if key in auxiliary_data.keys():
                auxiliary_data = auxiliary_data[key]
                number_existing_keys += 1
                if number_keys == number_existing_keys:
                    value = auxiliary_data

        return value