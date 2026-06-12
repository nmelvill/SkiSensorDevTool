from enum import Enum, auto

class DeviceErrorName(Enum):
    """Type that represents the error on the ski sensor device, this list needs to be kept updated with the list on the firmware
    """
    NO_ERROR = 0
    CONFIG_ERROR = auto()
    ARGUMENT_OUT_OF_RANGE = auto()
    UART_NOT_READY = auto()
    IO_ERROR = auto()
    BLOCKING_ERROR = auto()
    IMU_NOT_READY = auto()
    MAG_NOT_READY = auto()
    FLASH_NOT_READY = auto()
    # BLE Errors 
    BLE_ERROR_INIT_FAILED = auto()
    BLE_ERROR_ENABLE_FAILED = auto()
    BLE_ERROR_ADVERTISING_FAILED = auto()
    BLE_ERROR_CONNECTION_FAILED = auto()
    BLE_ERROR_DISCONNECTED = auto()
    BLE_ERROR_UNKNOWN = auto()
    BLE_ERROR_NOTIFY_FAILED = auto()
    BLE_ERROR_WRITE_FAILED = auto()
    BLE_ERROR_READ_FAILED = auto()
    BLE_ERROR_INDICATE_FAILED = auto()
    TEST_ERROR = auto()
    INVALID_ARGUMENT = auto()

dev_error_string_map: dict[DeviceErrorName, str] = {DeviceErrorName.NO_ERROR:"No Error",
   DeviceErrorName.CONFIG_ERROR:"Configuration Error",
   DeviceErrorName.ARGUMENT_OUT_OF_RANGE:"Argument Out of Range",
   DeviceErrorName.UART_NOT_READY:"UART Not Ready",
   DeviceErrorName.IO_ERROR:"IO Error",
   DeviceErrorName.BLOCKING_ERROR:"Blocking Error",
   DeviceErrorName.IMU_NOT_READY:"IMU Not Ready",
   DeviceErrorName.MAG_NOT_READY:"Magnetometer Not Ready",
   DeviceErrorName.FLASH_NOT_READY:"Flash Not Ready",
   DeviceErrorName.BLE_ERROR_INIT_FAILED:"BLE Initialization Failed",
   DeviceErrorName.BLE_ERROR_ENABLE_FAILED:"BLE Enable Failed",
   DeviceErrorName.BLE_ERROR_ADVERTISING_FAILED:"BLE Advertising Failed",
   DeviceErrorName.BLE_ERROR_CONNECTION_FAILED:"BLE Connection Failed",
   DeviceErrorName.BLE_ERROR_DISCONNECTED:"BLE Disconnected",
   DeviceErrorName.BLE_ERROR_UNKNOWN:"BLE Unknown Error",
   DeviceErrorName.TEST_ERROR:"Test Error"}


class ConnectionError(Exception):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field: str = field