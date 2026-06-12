from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional
from datetime import datetime
from SkiSensorDevTool.services.communication.protocol.commands import Command, CommandName, command_map
import SkiSensorDevTool.utils.logging
from logging import Logger
import logging
from SkiSensorDevTool.services.communication.exceptions import DeviceErrorName

logger: Logger = logging.getLogger(name=__name__)
logger.setLevel(level=logging.DEBUG)
logger.debug(msg=f"Logging started from {__name__}")

"""The data models module is a series of types that hold the data for all of the responses from the ski sensor parsed into typed 
attributes for use across the application.  Additionally in order to handle the translation from raw data to useable data each 
type has a class method asscociated with it that returns the type and takes a raw tuple to perform the translation"""

class DeviceState(Enum):
    INTIALIZING = 0
    IDLE = 1
    UPHILL = 2
    DOWNHILL = 3
    ERROR = 4
    SLEEP = 5
    RECOVERY = 6
    MAG_CALIBRATING = 7
    IMU_CALIBRATING = 8
    UNKNOWN = 9

class EventType(Enum):
    NONEALL = 0       #Used to indicate no event, also used to inform the event dispatcher that the subscriber is interested in all events
    COMMAND = auto()
    EVENT = auto()
    INPUT = auto()
    OUTPUT = auto()
    STATECHANGE = auto()
    CALIBRATION = auto()
    MOTION = auto()
    CONNECTION = auto()
    ERROR = auto()
    COUNT = auto()       #Used to determine the number of event types always keep at the end
    UNKNOWN = auto()

class EventName(Enum):
    NONE = 0
    STATECHANGE = auto()
    SLEEPDETECTED = auto()
    WAKEDETECTED = auto()
    FREE_FALL_DETECTED = auto()
    STEP_DETECTED = auto()
    SIG_MOTION_DETECTED = auto()
    TURN_DETECTED = auto()
    UP_DOWN_DETECTED = auto()
    MAG_CALIBRATED = auto()
    MAG_CALIBRATION_FAILED = auto()
    IMU_CALIBRATED = auto()
    IMU_CALIBRATION_FAILED = auto()
    BLE_CONNECTED = auto()
    BLE_DISCONNECTED = auto()
    BLE_ADVERTISING_STARTED = auto()
    ERROR = auto()
    UNKNOWN = auto()



def find_dict_key(value : Any, dict : dict) -> Any:
    """Helper function to find a key for a given value (reverse dictioary lookup), will only work when there is a 1:1 
    map of key:value pairs otherwise will return the first key for a given value

    Args:
        value (Any): Value to use to find a key
        dict (dict): Dictionary to search over

    Raises:
        ValueError:If the valus is not present in the dictionary

    Returns:
        Any: The key for a given value
    """

    return next(k for k,v in dict.items() if v == value)


@dataclass(frozen=True)
class DeviceError():
    code : DeviceErrorName

    @classmethod
    def from_message(cls, raw_input : tuple) -> list[DeviceError]:
        logger.debug(msg="Converting raw message to a list device error type")

        error_list: list[DeviceError] = []
        for err in raw_input:
            if err == 0:
                continue  #Do not add "no error" to the list

            error_list.append(DeviceError(code=DeviceErrorName(value=err)))

        logger.debug(msg=f"Build list of errors {error_list}")

        return error_list


@dataclass(frozen=True)
class DeviceStatus():
    state : DeviceState
    battery_level : float
    connection_status : bool
    error_status : bool
    calibration_status : bool

    @classmethod
    def from_message(cls, raw_message : tuple[int, ...]) -> 'DeviceStatus':

        logger.debug(msg="Converting raw message to the device status type")

        state: DeviceState = DeviceState(value=raw_message[0])
        batt_lvl: float = raw_message[1]/256
        conn: bool = bool(raw_message[2])
        err: bool = bool(raw_message[3])
        cal: bool = bool(raw_message[4])

        logger.debug(msg=f"Raw input: {raw_message} converted to State: {state} | Battery Level: {batt_lvl} | Connected: {conn} | Error Present: {err} | Calibrated: {cal}")

        return DeviceStatus(state=state, 
        battery_level=batt_lvl,
        connection_status=conn,
        error_status=err,
        calibration_status=cal)


@dataclass(frozen=True)
class DeviceEvent():
    type : EventType
    name : EventName
    data : str

    @classmethod
    def from_message(cls,raw_message : tuple) -> 'DeviceEvent':
        logger.debug(msg="Converting raw message to the Event Type")

        type: EventType = EventType(value=raw_message[0])
        name: EventName = EventName(value=raw_message[1])
        data: str = raw_message[2].decode('utf-8')

        logger.debug(msg=f"Event Type: {type} | Event Name: {name} | Event Data: {data}")

        return DeviceEvent(type, name, data)



@dataclass(frozen=True)
class CommandResponse():
    command : CommandName
    data : str

    @classmethod
    def from_message(cls, raw_message : tuple[bytes, ...]) -> 'CommandResponse':
        logger.debug(msg="Converting raw message to the Command Response Type")
        
        raw_command: str = raw_message[0].decode(encoding='utf-8')
        data: str = raw_message[1].decode(encoding='utf-8')

        logger.debug(msg=f"Converted from {raw_message} to {raw_command} and {data}")

        try:
            command_name: CommandName = find_dict_key(value=raw_command, dict=command_map)
            logger.debug(f'Found the command name {command_name} that matches the raw value {raw_command}')

        except Exception as e:
            raise ValueError(f'Command {raw_command} is not present in the command map dictionary exception: {e}')

        return CommandResponse(command=command_name,data=data)

if __name__ == '__main__':

    from SkiSensorDevTool.services.communication.protocol.decoder import Message, MessageSource
    
    
    raw_status: bytes = b'\x04\x00\x01\x01\x00'
    raw_error_array: bytes = b'\x13\x00\x13\x00\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    raw_cmd_resp: bytes = b'ssss\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    raw_event: bytes = b'\x05\x01idle\x00'
    
    status_message: Message = Message(msg_source=MessageSource.DEVICE_STATUS, payload=raw_status)
    status_tuple: tuple[Any, ...] = status_message.parse()
    status: DeviceStatus = DeviceStatus.from_message(raw_message=status_tuple)

    error_array : Message = Message(msg_source=MessageSource.ERRORS, payload=raw_error_array)
    error_tuple: tuple[Any, ...] = error_array.parse()
    error_list: list[DeviceError] = DeviceError.from_message(raw_input=error_tuple)

    cmd_resp_array : Message = Message(msg_source=MessageSource.COMMAND_RESP, payload=raw_cmd_resp)
    cmd_resp_tuple: tuple[bytes, ...]= cmd_resp_array.parse()
    cmd_resp: CommandResponse = CommandResponse.from_message(raw_message=cmd_resp_tuple)

    event_array : Message = Message(msg_source=MessageSource.EVENT, payload=raw_event)
    event_tuple : tuple = event_array.parse()
    event: DeviceEvent = DeviceEvent.from_message(raw_message=event_tuple)

    




    


