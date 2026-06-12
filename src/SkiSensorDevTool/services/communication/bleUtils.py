from logging import Logger
import json
from pathlib import Path
from typing import Any
import logging
import SkiSensorDevTool.utils.logging

logger: Logger = logging.getLogger(name=__name__)
logger.setLevel(level=logging.INFO)
logger.debug(msg=f'Logging started from {__name__}')


def map_gatt_UUID(param_name : str) -> str:
    '''Takes in the name of a GATT parameter and returns the correct UUID for that parameter'''
    
    logger.debug(msg=f"Mapping parameter {param_name} to gatt aatribute uuid")

    config: dict[Any, Any] = load_ble_config()
    uuid : str = ""
    
    if param_name in  config:
        uuid = config[param_name]["uuid"]
    else:
        uuid = get_nested_value(dictionary=config,key=param_name)   # pyright: ignore[reportAssignmentType]

    logger.debug(msg=f"Parameter name {param_name} found and mapped to uuid {uuid}")
    
    return uuid

def load_ble_config() -> dict:
    '''Loads the BLE config and returns a dictionary with those values'''
    
    current_file: Path = Path(__file__).resolve()

    ble_config: Path = current_file.parent / 'bleConfig.json'

    config_dict: dict = {}
    
    with open(file=ble_config) as jsonfile:
        config_dict = json.load(fp=jsonfile)

    logger.debug(msg=f"BLE config file opened and loaded from {ble_config}")
    logger.debug(msg=f"BLE Config: {config_dict}")

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
    import SkiSensorDevTool.utils.logging

    map_gatt_UUID(param_name="device_information_service")



