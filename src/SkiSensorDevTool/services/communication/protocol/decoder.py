from dataclasses import dataclass
from enum import Enum
from typing import Any
import struct
import SkiSensorDevTool.utils.logging
from logging import Logger
import logging

logger: Logger = logging.getLogger(name=__name__)
logger.setLevel(level=logging.DEBUG)
logger.debug(msg=f"Logging started from {__name__}")

class MessageSource(Enum):
    DEVICE_STATUS = 0
    FWVERSION = 1
    HWVERSION = 2
    SERIAL_NUMBER = 3
    BATTERY_LEVEL = 4
    LOGS = 5
    ERRORS = 6
    NAME = 7
    MAG = 8
    IMU = 9
    STEPS = 10
    ORIENTATION = 11
    COMMAND_RESP = 12
    EVENT = 13
    MODEL_NUM = 14
    MANUFACTURER = 15
    UNKNOWN = 16


## format_map is used to map a message source to a format string that is used by the struct.unpack function
format_map: dict[MessageSource, str] = {MessageSource.DEVICE_STATUS : '<5B',
    MessageSource.FWVERSION : '<16s',
    MessageSource.HWVERSION : '<16s',
    MessageSource.SERIAL_NUMBER : '<16s',
    MessageSource.BATTERY_LEVEL : '<b',
    MessageSource.LOGS : '',
    MessageSource.ERRORS : '<10H',
    MessageSource.NAME : '<32s',
    MessageSource.MAG : '>Q4i3q',
    MessageSource.IMU : '>Q6i2q',
    MessageSource.STEPS : '<H',
    MessageSource.ORIENTATION : '',
    MessageSource.COMMAND_RESP : '<4s36s',
    MessageSource.EVENT : '<BB',
    MessageSource.UNKNOWN : ''}



@dataclass(frozen=True)
class Message:
    msg_source : MessageSource
    payload : bytes

    def parse(self)-> tuple[Any, ...]:

        logger.debug(f"Parsing {self.payload}")

        format : str

        if self.msg_source == MessageSource.EVENT:
            length: int = len(self.payload)
            format = format_map[self.msg_source] + f"{length-2}s"

        else:
            format = format_map[self.msg_source]
        
        rtn_tuple: tuple[Any, ...] = struct.unpack(format, self.payload)

        logger.debug(msg=f"Raw value {self.payload} parsed to {rtn_tuple}")
        
        return rtn_tuple


if __name__ == '__main__':

    raw_status: bytes = b'\x04\x00\x01\x01\x00'
    raw_error_array: bytes = b'\x13\x00\x13\x00\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    raw_cmd_resp: bytes = b'ssss\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    raw_mag_resp: bytes = b'\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x7f\xff\xff\xff\x80\x00\x00\x00\x00\x00K\xaf\x00\x00\x00\x00\x00\x0f\x870\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\x04\x00\x00\x00'

    # status_message: Message = Message(msg_source=MessageSource.DEVICE_STATUS, payload=raw_status)
    # status_message.parse()

    # error_array : Message = Message(msg_source=MessageSource.ERRORS, payload=raw_error_array)
    # error_array.parse()

    # cmd_resp_array : Message = Message(msg_source=MessageSource.COMMAND_RESP, payload=raw_cmd_resp)
    # cmd_resp_array.parse()

    mag_array : tuple = Message(msg_source=MessageSource.MAG, payload=raw_mag_resp).parse()

   