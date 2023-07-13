import yaml

class Config(object):
    def __init__(self):
        with open('env/config.yaml') as file:
            cfg = yaml.load(file, Loader=yaml.FullLoader)
        self.shopee = cfg.get('shopee_api')
        
    def get_shopee_api(self):
        return self.shopee
        
        