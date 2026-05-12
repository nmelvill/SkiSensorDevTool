from bleak.backends.device import BLEDevice
from bleak import BleakClient
import SkiSensorDevTool.utils.return_handler as return_handler


import click
from SkiSensorDevTool.services.ble.bleController import BLEController


@click.command()
def blconnect() -> BLEController:
    controller: BLEController = BLEController()

    device: BLEDevice = controller.scan()

    ss_client: BleakClient = controller.connect(device)

    click.echo(message=f"Connection started with {ss_client.name} {ss_client.address}")

    return controller


@click.command()
def fwversion() -> None:
    controller: BLEController = blconnect()

    raw_value: bytearray = controller.read_char(char_name="fw_version")

    fw_version: str = return_handler.handle_fw_version(raw_value=raw_value)

    click.echo(f"Firware Version: {fw_version}")
