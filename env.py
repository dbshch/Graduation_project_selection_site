import yaml

def get_env():
    f = open('config.yaml')
    config = yaml.safe_load(f)
    f.close()
    return config
