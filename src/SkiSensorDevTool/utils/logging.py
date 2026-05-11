
import logging
import logging.config
import yaml
from typing import Any

config: dict[Any, Any] = {}


with open(file="src/SkiSensorDevTool/log_config.yaml", mode='rt') as logconfig:

    config = yaml.safe_load(stream=logconfig.read())


logging.config.dictConfig(config)
