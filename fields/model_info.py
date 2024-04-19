class ModelInfo(object):
    
    def __init__(self,
                 data,
                 status,
                 message):
                 
        # used to identify model
        self.result = data
        self.status = status
        self.message = message


    def to_json(self):
        return self.__clean_none(self.__dict__)

    def __clean_none(self, json_dict):
        result = dict()
        
        for key, value in json_dict.items():
            if isinstance(value, dict):
                value = self.__clean_none(value)
                result[key] = value
                continue

            if value is not None:
                result[key] = value
        return result
