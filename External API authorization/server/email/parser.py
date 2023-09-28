import json

settings: dict

with open('./.config.json', 'r') as settings_file:
    settings = json.load(settings_file)
