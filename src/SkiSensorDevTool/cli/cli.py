import click
from bleak.backends.device import BLEDevice
from SkiSensorDevTool.services.ble.bleController import BLEController
import SkiSensorDevTool.utils.return_handler as return_handler


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    click.echo(message="Hello")


def _blconnect() -> BLEController:
    controller: BLEController = BLEController()

    device: BLEDevice = controller.scan()

    controller.connect(device)

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


@cli.command()
def fwver() -> None:
    """Gets the firmware version of the ski sensor"""
    controller: BLEController = _blconnect()

    raw_value: bytearray = controller.read_char(char_name="fw_version")
    fw_version: str = return_handler.handle_fw_version(raw_value=raw_value)

    click.echo(message=f"Firware Version: {fw_version}")
