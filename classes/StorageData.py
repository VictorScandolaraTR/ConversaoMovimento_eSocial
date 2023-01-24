class StorageData:
    
    def __init__(self):
        self.__data = {}
    
    def add(self, value, keys=[]):
        auxiliary_data = self.__data
        for key in keys[:-1]:
            auxiliary_data = auxiliary_data.setdefault(key, {})
        auxiliary_data[keys[-1]] = auxiliary_data.get(keys[-1], value)
            
    
    def exist(self, keys=[]):
        auxiliary_data = self.__data
        number_keys = len(keys)
        number_existing_keys = 0
        for key in keys:
            if key in auxiliary_data.keys():
                auxiliary_data = auxiliary_data[key]
                number_existing_keys += 1
        
        return (number_keys == number_existing_keys)


    def get(self, keys=[]):
        value = ''
        auxiliary_data = self.__data
        number_keys = len(keys)
        number_existing_keys = 0
        for key in keys:
            if key in auxiliary_data.keys():
                auxiliary_data = auxiliary_data[key]
                number_existing_keys += 1
                if number_keys == number_existing_keys:
                    value = auxiliary_data

        return value