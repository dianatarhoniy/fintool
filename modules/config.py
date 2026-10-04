import yaml


def load_profile(path):
    with open(path) as file:
        return yaml.safe_load(file)