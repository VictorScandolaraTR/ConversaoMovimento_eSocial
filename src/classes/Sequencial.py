class Sequencial:
    
    def __init__(self):
        self.__sequencial = {}
    
    def add(self, keys=[]):
        value = 0
        if len(keys) == 1:
            if keys[0] not in self.__sequencial.keys():
                self.__sequencial[keys[0]] = 1
            else:
                self.__sequencial[keys[0]] += 1
            
            value = self.__sequencial[keys[0]]

        elif len(keys) == 2:
            if keys[0] not in self.__sequencial.keys():
                self.__sequencial[keys[0]] = {}

            if keys[1] not in self.__sequencial[keys[0]].keys():
                self.__sequencial[keys[0]][keys[1]] = 1
            else:
                self.__sequencial[keys[0]][keys[1]] += 1
            
            value = self.__sequencial[keys[0]][keys[1]]

        elif len(keys) == 3:
            if keys[0] not in self.__sequencial.keys():
                self.__sequencial[keys[0]] = {}

            if keys[1] not in self.__sequencial[keys[0]].keys():
                self.__sequencial[keys[0]][keys[1]] = {}
            else:
                self.__sequencial[keys[0]][keys[1]] += 1

            if keys[2] not in self.__sequencial[keys[0]][keys[1]].keys():
                self.__sequencial[keys[0]][keys[1]][keys[2]] = 1
            else:
                self.__sequencial[keys[0]][keys[1]][keys[2]] += 1
            
            value = self.__sequencial[keys[0]][keys[1]][keys[2]]
        
        return value