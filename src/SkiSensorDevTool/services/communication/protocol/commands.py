from dataclasses import dataclass
import SkiSensorDevTool.utils.logging
from logging import Logger
import logging
from enum import Enum
from SkiSensorDevTool.services.communication.protocol.encoder import Encoder

logger: Logger = logging.getLogger(name=__name__)
logger.setLevel(level=logging.DEBUG)
logger.debug(msg=f"Logging started from {__name__}")

class CommandName(Enum):
    SETSTATE = 0
    GETSTATUS = 1
    GETRAWMAG = 2
    GETRAWIMU = 3
    SETERROR = 4
    

command_map : dict[CommandName,str] = { CommandName.SETSTATE: 'ssss',
                                    CommandName.GETSTATUS: 'gsta',
                                    CommandName.GETRAWMAG: 'grmd',
                                    CommandName.GETRAWIMU: 'grid',
                                    CommandName.SETERROR: 'serr'}

@dataclass(frozen=True)
class Command:
    name : CommandName
    params : tuple = ()

    def build(self) -> bytes:
        logger.debug(msg=f"Building command {self.name} with parameters : {self.params}")
        
        return Encoder.buildCommand(command=command_map[self.name],params=self.params)

        


if __name__ == '__main__':

    setstate: bytes = Command(name=CommandName.SETSTATE, params=('id',)).build()