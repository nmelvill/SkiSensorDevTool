from typing import Any
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from SkiSensorDevTool.services.communication.protocol.encoder import Encoder
from SkiSensorDevTool.services.communication.protocol.decoder import Message, MessageSource
from SkiSensorDevTool.services.communication.protocol.commands import Command, CommandName
from SkiSensorDevTool.services.communication.transport.bleController import BLEController
from SkiSensorDevTool.services.communication.data_models import CommandResponse, DeviceState, DeviceError, DeviceEvent, DeviceStatus
from bleak.backends.characteristic import BleakGATTCharacteristic
import SkiSensorDevTool.utils.logging
from logging import Logger
from SkiSensorDevTool.utils.event_dispatcher import EventDispatcher
import logging
from SkiSensorDevTool.utils.event_listener import EventListener
from SkiSensorDevTool.services.communication import data_models

logger: Logger = logging.getLogger(name=__name__)
logger.setLevel(level=logging.DEBUG)
logger.debug(msg=f"Logging started from {__name__}")



device_state_map: dict[DeviceState, str] = {DeviceState.IDLE : 'id',
                                            DeviceState.UPHILL: 'up',
                                            DeviceState.DOWNHILL : 'dn',
                                            DeviceState.ERROR : 'er',
                                            DeviceState.SLEEP : 'sp',
                                            DeviceState.RECOVERY : 'rc',
                                            DeviceState.MAG_CALIBRATING : 'cm',
                                            DeviceState.IMU_CALIBRATING : 'ci'}

class Device(EventDispatcher):
    """High level class that controls all of the operations of a ski sensor device once connected.  
    This abstracts away all of the encoding and decoding required to communicate with the ski sensor.
    """

    
    def __init__(self, ble_controller : BLEController) -> None:
        super().__init__()
        self.controller: BLEController = ble_controller
        self.state: DeviceState = DeviceState.UNKNOWN

        
    @staticmethod
    def command_resp_cb(sender: BleakGATTCharacteristic, data: bytes) -> CommandResponse:
        logger.debug(msg=f"Command Response received to the CALLER from {sender}: {data}")

        unpack_command_response: tuple[Any, ...]  = Message(msg_source=MessageSource.COMMAND_RESP,payload=data).parse()

        command_response: CommandResponse = CommandResponse.from_message(raw_message=unpack_command_response)

        return command_response

    @staticmethod
    def device_event_cb(sender: BleakGATTCharacteristic, data: bytes) -> DeviceEvent:
        logger.debug(msg=f"Event received to the CALLER from {sender}: {data}")

        unpack_event: tuple[Any, ...] = Message(msg_source=MessageSource.EVENT,payload=data).parse()

        return DeviceEvent.from_message(raw_message=unpack_event)

    def connect(self) -> bool:

        device: BLEDevice = controller.scan()

        try:
            client: BleakClient = self.controller.connect(device, onEvent_cb=Device.device_event_cb, onCommandResponse_cb=Device.command_resp_cb)

            logger.debug(msg=f"Successfully connected to {device.address} and created local BLE client instance {client.address}")

            return True

        except Exception as e:
            logger.error(msg=f"Error when attempting to connect to {device.address} exception {e}")
            return False

    def set_state(self, state : DeviceState) -> None:
        
        if self.controller.ble_client.is_connected:
        
            logger.debug(msg=f"Setting ski sensor state to {state}")
            cmd: bytes = Command(name=CommandName.SETSTATE, params=(device_state_map[state],)).build()

            self.controller.write_char(char_name='control_point', payload=cmd)

        else:
            logger.warning(msg="BLE Client is not connected to a ski sensor")


    def get_status(self) -> DeviceStatus:
        
        logger.debug(msg="Attempting to retrieve the device status...")

        try:
            raw_status: bytearray = self.controller.read_char(char_name='status')

        except Exception as e:
            
            logger.error(msg=f"Exception occured when reading the device status: {e}")
            raise e

        status_tuple: tuple[int, ...] = Message(msg_source=MessageSource.DEVICE_STATUS, payload=bytes(raw_status)).parse()

        return DeviceStatus.from_message(raw_message=status_tuple)

    def get_raw_mag_data(self) -> None:
        pass

    def get_raw_imu_data(self) -> None:
        pass

    def get_steps(self) -> None:
        pass

    def get_orientation(self) -> None:
        pass

    def get_device_info(self) -> None:
        pass

    def get_errors(self) -> None:
        pass

    def get_logs(self) -> None:
        pass

    def get_battery_level(self) -> None:
        pass

    def calibrate_mag(self) -> None:
        pass


if __name__ == "__main__":
    import time
    
    ## Setup of the classes
    
    test_listener: EventListener = EventListener()

    controller: BLEController = BLEController()

    test_device: Device= Device(ble_controller=controller)
    test_device.add_listener(listener=test_listener)

    
    test_device.connect()

    test_device.set_state(state=DeviceState.IDLE)

    time.sleep(10)
    controller.disconnect()