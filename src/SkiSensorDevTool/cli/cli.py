import click
from bleak.backends.device import BLEDevice
from SkiSensorDevTool.services.communication.data_models import deviceState
from SkiSensorDevTool.services.communication.transport.bleController import BLEController
from SkiSensorDevTool.services.communication.device import Device

import time


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    click.echo(message="Starting Ski Sensor CLI")


def _blconnect() -> BLEController:
    controller: BLEController = BLEController()

    device: BLEDevice = controller.scan()

    controller.connect(device)

    return controller

def ___write_control_point(message:str, disconnect:bool=True) -> BLEController:
    
    controller: BLEController = _blconnect()

    payload: bytes = message.encode(encoding='utf-8')

    controller.write_char(char_name='control_point',payload=payload)

    time.sleep(10)

    if disconnect: controller.disconnect()  # noqa: E701

    return controller


@cli.command()
def blconnect() -> None:
    """Connects to the ski sensor.
    NOTE: does not do anything once connected
    """
    controller: BLEController = _blconnect()

    click.echo(
        message=f"Connection started with {controller.ble_client.name} {controller.ble_client.address}"
    )

    controller.disconnect()


# @cli.command()
# def fwver() -> None:
#     """Gets the firmware version of the ski sensor"""

#     click.echo(message=f"Firware Version: {_get_device_info(param_name='fw_version')}")


# @cli.command()
# def hwver() -> None:
#     """Gets the hardware version of the ski sensor"""

#     click.echo(message=f"Hardware Version: {_get_device_info(param_name='hw_version')}")


# @cli.command()
# def sn() -> None:
#     """Gets the serial number of the ski sensor"""

#     click.echo(message=f"Serial Number: {_get_device_info(param_name='serial_number')}")


# @cli.command()
# def battery() -> None:
#     """Gets the battery level of the ski sensor"""

#     click.echo(message=f"Battery Level: {_get_device_info(param_name='battery')}")


# @cli.command()
# def getlogs() -> None:
#     """Gets the logs from the ski sensor"""

#     click.echo(message=f"Logs: {_get_device_info(param_name='logs')}")


# @cli.command()
# def devstatus() -> None:
#     """TODO: Need to parse more here
#     Gets the ski sensor device status"""

#     click.echo(message=f"Logs: {_get_device_info(param_name='status')}")


# @cli.command()
# def geterrors() -> None:
#     """Gets the ski sensor device error list"""

#     click.echo(message=f"Errors: {_get_device_info(param_name='error')}")


# @cli.command()
# def getname() -> None:
#     """Gets the ski sensor device name"""

#     click.echo(message=f"Name: {_get_device_info(param_name='device_name')}")

@cli.command()
@click.argument('device_name', type=str)
def setname(device_name: str) -> None:
    """Sets the name of the device
    
    Usage: ssdt setname DEVICENAME

    DEVICENAME string to set the name of the device
    """
    controller: BLEController = _blconnect()

    payload: bytes = device_name.encode(encoding='utf-8')

    controller.write_char(char_name='device_name', payload=payload)

    controller.disconnect()

    click.echo(message=f"Wrote device name to {device_name}")

@cli.command()
@click.argument('state', type=str)
def setstate(state:str) -> None:
    """Sets the state of the device
    Usage: ssdt setstate STATE

    STATE one of the following states to set the ski sensor to
        id - idle
        up - uphill
        dn - downhill
        er - error
        sp - sleep
        cm - calibrate the magenetometer
        ci - calibrate the imu
        rc- recovery
    """
    controller: BLEController = _blconnect()
    
    device: Device = Device(ble_controller=controller)

    state_map: dict[str, deviceState] = {'id' : deviceState.IDLE,
                                        'up' : deviceState.UPHILL ,
                                        'dn' : deviceState.DOWNHILL ,
                                        'er' : deviceState.ERROR ,
                                        'sp' : deviceState.SLEEP ,
                                        'cm' : deviceState.MAG_CALIBRATING ,
                                        'ci' : deviceState.IMU_CALIBRATING}

    device.set_state(state=state_map[state])
    
    click.echo(message="Set the state of the ski sensor")

    

@cli.command()
@click.option('-r', '--raw',is_flag=True )
def readmag(raw: bool) -> None:
    pass

@cli.command()
def seterror() -> None:
    error_cmd: str = "serr"+"~~~~"

    controller: BLEController = ___write_control_point(error_cmd,disconnect=False)

    raw_value: bytearray = controller.read_char(char_name='status')

    status_: str = return_handler.handle_device_information(raw_value=raw_value)

    click.echo(message=f"Device Status String: {status_}")

    errors: tuple

    try:
        # Unpack as little-endian 16-bit integers (H = unsigned short)
        errors = return_handler.handle_error_array(controller.read_char(char_name='error'))

        click.echo(message=f"Error list from device : {errors}")
    except Exception as e:
        click.echo(message=f"Exception caught when retrieving error list from device : {e}")
    finally:
        controller.disconnect()