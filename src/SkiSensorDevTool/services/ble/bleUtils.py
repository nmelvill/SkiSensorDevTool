from logging import Formatter, Logger, StreamHandler


import json
from pathlib import Path
from typing import Any
import logging
import logging.config
import yaml

config: dict[Any, Any] = {}

with open(file="src/SkiSensorDevTool/log_config.yaml", mode='rt') as logconfig:
    config = yaml.safe_load(stream=logconfig.read())

logging.config.dictConfig(config)
logger: Logger = logging.getLogger(name="sslogger")
logger.setLevel(level=logging.DEBUG)


def map_gatt_UUID(param_name : str) -> str:
    '''Takes in the name of a GATT parameter and returns the correct UUID for that parameter'''
    
    logger.debug(f"Mapping parameter {param_name} to gatt aatribute uuid")
    return get_nested_value(dictionary=load_ble_config(),key=param_name)  # pyright: ignore[reportReturnType]

def load_ble_config() -> dict:
    '''Loads the BLE config and returns a dictionary with those values'''
    
    current_file: Path = Path(__file__).resolve()

    ble_config: Path = current_file.parent / 'bleConfig.json'

    config_dict: dict = {}

    with open(file=ble_config) as jsonfile:
        config_dict = json.load(fp=jsonfile)

    logger.info(f"BLE config file opened and loaded from {ble_config}")
    logger.debug(f"BLE Config: {config_dict}")

    return config_dict

def get_nested_value(dictionary : dict, key :str) -> str | None:
    
    if key in dictionary:
        return dictionary[key]  
    else:
        for k, v in dictionary.items():
            if isinstance(v, dict):
                try:
                    return get_nested_value(dictionary=v, key=key)
                except KeyError:
                    continue

        #If loop completes without finding the key raise an error
        raise KeyError(f"Key '{key}' not found in nested dictionary")
    
    



if __name__ == '__main__':

    
    load_ble_config()



