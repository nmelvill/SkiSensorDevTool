import SkiSensorDevTool.utils.logging
from logging import Logger
import logging

logger: Logger = logging.getLogger(name=__name__)
logger.setLevel(level=logging.DEBUG)
logger.debug(msg=f"Logging started from {__name__}")

class Encoder:
    
    commandSize: int = 8
    dummyChar: str = '\x7E'
    
    @staticmethod
    def buildCommand(command : str, params : tuple = ()) -> bytes:
        logger.debug(msg=f"Starting to build bytes for command {command} with parameters {params}")
        
        if len(command) != 4:
            logger.error(msg=f"Commands must be 4 characters {command} is {len(command)} characters")
            raise ValueError(f"Commands must be 4 characters {command} is {len(command)} characters")
        
        encodedName: bytes = (command.encode(encoding='utf-8'))

        param_num: int = len(params)

        logger.debug(f"Parameter number: {param_num}")

        if param_num > 2:
            logger.error(msg="Commands cannot have more than 2 parameters of 2 bytes each ex: ('id', 'up)")
            raise ValueError("Commands cannot have more than 2 parameters of 2 bytes each ex: ('id', 'up)")

        for param in range(param_num):
            logger.debug(msg=f"Adding parameter {params[param]} to encoded command {encodedName}")
            encodedName += params[param].encode(encoding='utf-8')

        logger.debug(msg=f"Encoded command without dummy chars {encodedName}")

        if len(encodedName) < Encoder.commandSize:
            for i in range(Encoder.commandSize - len(encodedName)):
                encodedName += Encoder.dummyChar.encode(encoding='utf-8')
            
        logger.debug(msg=f'Encoded command {encodedName}')
        
        return encodedName


if __name__ == '__main__':

    testcmd : str = 'ssss'
    params : tuple = ("id","up")

    cmd: bytes = Encoder.buildCommand(command=testcmd, params=params)

