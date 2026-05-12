from pyclbr import Function
from SkiSensorDevTool.utils.ss_message import SSMessage
from asyncio.locks import Event
from bleak.backends.device import BLEDevice
from asyncio.events import AbstractEventLoop
from bleak.backends.service import BleakGATTServiceCollection
from logging import Logger
import SkiSensorDevTool.utils.logging
from typing import Any, Callable
import logging
import logging.config
import traceback
from . import bleUtils
import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from threading import Thread


logger: Logger = logging.getLogger(name=__name__)
logger.setLevel(level=logging.DEBUG)
logger.info(f"Logging from {__name__}")

#The bluez backend logs too much
bleaklogger: Logger = logging.getLogger("bleak.backends.bluezdbus.manager")
bleaklogger.setLevel(level=logging.INFO)




class BLEController:
    """Class to manage the BLE connection with the ski sensor device, operates
    syncronously within the module and blocks before executing the next task,
    but does not block the caller by operating in another thread"""

    def __init__(self) -> None:
        self.scan_stop_event: Event = asyncio.Event()
        self.ble_loop: AbstractEventLoop = asyncio.new_event_loop()
        self.thread: Thread = Thread(
            target=self._run_loop, daemon=True, name="BLE_EventLoop"
        )
        self.thread.start()

        logger.debug(
            msg=f"Thread: {self.thread.name} created and is running?: {self.thread.is_alive()}"
        )
        logger.debug(
            msg=f"Eventloop {self.ble_loop} initialized and is running?:{self.ble_loop.is_running()}"
        )

        self.onEvent_cb: Function
        self.onCommandResponse_cb: Function

    def __del__(self) -> None:

        logger.debug("Attmpting to clean up connection and threads safely")
        if self.ble_client.is_connected:
            try:
                self.disconnect()
            except Exception as e:
                logger.error(f"Exception when attempting to disconnect from {self.ble_client.address}: {e}")
                raise e

            try:
                self.thread.join()
            except Exception as e:
                logger.error(msg=f"Exception when attempting to close the BLE thread: {e}")
                raise e

            

    def _run_loop(self) -> None:
        asyncio.set_event_loop(loop=self.ble_loop)
        self.ble_loop.run_forever()

    def _run_sync(self, coro, timeout=15):
        """Helper to run async code synchronously from the background thread."""
        future = asyncio.run_coroutine_threadsafe(coro, loop=self.ble_loop)

        try:
            result: Any = future.result(timeout=timeout)
            return result
        except asyncio.TimeoutError as e:
            logger.error(msg="The operation timed out waiting for the thread.")
            raise e
        except Exception as e:
            # This catches the BleakError raised in the coroutine
            print(f"Sync call failed with: {e}")
            raise e

    # --- Callback functions ---

    def scanner_callback(self, device, advertising_data) -> None:
        """Callack that is called when a ski sensor device has been found"""
        # logger.info(msg=f"Device found: {device} with advertising data {advertising_data}, stopping scan")
        pass
        # self.scan_stop_event.set()

    def disconnected_callback(self, client: BleakClient) -> None:

        logger.info(msg=f"Device {client.name} disconnected {client}")

    def device_event_callback(
        self, sender: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Callback function to handle events from the device."""

        logger.debug(msg=f"Event received from {sender}: {data}")
        # data_: bytearray = data[
        #     2:-1
        # ]  # Exclude the last byte which is a null terminator`

    def command_response_callback(
        self, sender: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Callback function to handle command responses from the device."""

        logger.debug(msg=f"Command response received from {sender}: {data}")

    # --- Internal async functions ---

    async def _scan(self) -> BLEDevice:
        """Scan for available ble devices and stop when a ski sensor is found, return that device"""

        dev_info_service_uuid = bleUtils.map_gatt_UUID(
            param_name="device_information_service"
        )

        logger.debug(msg="Starting to scan for available BLE devices..")

        scanner: BleakScanner = BleakScanner(
            detection_callback=self.scanner_callback,
            service_uuids=[dev_info_service_uuid],
        )
        await scanner.start()

        async for device, adv_data in scanner.advertisement_data():
            logger.debug(
                msg=f"Scanning successful found {device} with advertising data: {adv_data}, stopping scan"
            )

            await scanner.stop()
            break

        return device

    async def _connect(self, ble_device: BLEDevice, onEvent_cb=None, onCommandResponse_cb=None) -> BleakClient:
        """Connect to a target ble device, returns the connections as a Bleak Client
        
        Argumemts:
            ble_device: Instance of a ble_device type from Bleak that was found during the scanning function
            onEvent_cb: Callback function that will trigger when an event occurs on the ski sensor (default = {None})
            onCommandResponse_cb: Callback function that will trigger when the response from a command call returns from the ski sensor (default = {None})

        Returns:
            BleakClient: instance of a Bleak Client that holds the connection information
        """
        logger.debug(msg=f"Attempting to connect to device: {ble_device}")

        self.ble_client: BleakClient = BleakClient(
            address_or_ble_device=ble_device,
            disconnected_callback=self.disconnected_callback,
        )

        try:
            await self.ble_client.connect()
        except Exception as e:
            logger.error(
                f"Error connecting to BLE Device {ble_device.name} {ble_device.address}. Exception: {e}"
            )

        logger.info(
            msg=f"BLE connection state of ski_sensor: {self.ble_client.is_connected}"
        )

        self.services: BleakGATTServiceCollection = self.ble_client.services

        for service in self.services:
            logger.debug(f"Service: {service}")
            for characteristic in service.characteristics:
                logger.debug(f"  Characteristic: {characteristic}")

        logger.debug(msg="Enabling notifications")


        eventcb: Callable[..., None] = self.device_event_callback

        if onEvent_cb:
            eventcb = onEvent_cb

            logger.debug("Event callback is not none, assigning it to notify caller")

        commandcb: Callable[..., None] = self.command_response_callback

        if onCommandResponse_cb:

            commandcb = self.command_response_callback
            logger.debug("Command response callback is not none, assigning it to notify caller")

        try:
            await self.ble_client.start_notify(
                char_specifier=bleUtils.map_gatt_UUID(param_name="event"),
                callback=eventcb,
            )
        except Exception as e:
            logger.error(
                f"Error registering for notifications from event characterisitic. Exception {e}",
                stack_info=True,
            )
            raise

        try:
            await self.ble_client.start_notify(
                char_specifier=bleUtils.map_gatt_UUID(param_name="command_response"),
                callback=commandcb,
            )
        except Exception as e:
            logger.error(
                msg=f"Error registering for notifications from command response characterisitic. Exception {e}",
                stack_info=True,
            )
            raise

        logger.debug(
            msg="Notifications enabled on the event and command response characterisitics"
        )

        return self.ble_client

    async def _disconnect(self) -> None:
        """Disconnects an active connection with a ble device"""

        if self.ble_client.is_connected:
            logger.debug(
                f"Attempting to disconnect from the ski sensor device {self.ble_client.name}"
            )

            try:
                await self.ble_client.disconnect()
                logger.info(f"Successfully disconnected from {self.ble_client.name}")
                logger.debug(msg=f"Connection status {self.ble_client.is_connected}")

            except Exception as e:
                logger.error(
                    f"Error occured when disconnecting from device. Exception: {e}"
                )

    async def _pair(self, client: BleakClient):
        logger.debug(msg="Pairing with device...")

        try:
            await client.pair()
            logger.info(msg="Paired successfully.")

        except Exception as e:
            logger.error(msg=f"Error pairing with device: {e}")
            traceback_str: str = traceback.format_exc()
            logger.error(msg=f"Traceback: {traceback_str}")
            raise e

    async def _write_char(self, char_name, payload, response) -> None:
        """Writes to a specified characteristic"""

        logger.debug(msg=f"Writing {payload} to {char_name}")
        if self.ble_client.is_connected:
            try:
                await self.ble_client.write_gatt_char(
                    char_specifier=bleUtils.map_gatt_UUID(param_name=char_name),
                    data=payload,
                    response=response,
                )

                logger.debug(msg="Writing succeeded")
            except Exception as e:
                logger.error(msg=f"Exception writing to characteristing {char_name}: {e}")

        else:
            logger.warning(msg=f"Device {self.ble_client.name} is not connected")

    async def _read_char(self, char_name) -> bytearray:
        """Reads from a specified characterisitic"""

        char_uuid: str = bleUtils.map_gatt_UUID(param_name=char_name)
        logger.debug(
            msg=f"Reading from characteristic: {char_name} with uuid: {char_uuid} using {self.ble_client.address}"
        )

        data: bytearray

        if self.ble_client.is_connected:
            try:
                data = await self.ble_client.read_gatt_char(char_specifier=char_uuid)
                logger.info(msg=f"Data read from characteristic : {char_name}: {data}")

            except Exception as e:
                logger.error(msg=f"Reading {char_name} failed with Exception: {e}")
                raise e

        else:
            logger.warning(msg=f"Device {self.ble_client.name} is not connected")

        return data

    # --- Synchronous Public API ---

    def scan(self) -> BLEDevice:
        return self._run_sync(coro=self._scan(), timeout=120)

    def connect(self, device: BLEDevice,onEvent_cb=None, onCommandResponse_cb=None) -> BleakClient:
        return self._run_sync(coro=self._connect(ble_device=device,onEvent_cb=onEvent_cb, onCommandResponse_cb=onCommandResponse_cb))

    def read_char(self, char_name) -> bytearray:
        return self._run_sync(coro=self._read_char(char_name=char_name))

    def write_char(self,char_name, payload, response=False) -> None:
        return self._run_sync(coro=self._write_char(char_name=char_name, payload=payload, response=response))

    def disconnect(self) -> None:
        return self._run_sync(coro=self._disconnect())


if __name__ == "__main__":
    import SkiSensorDevTool.utils.logging  # pyright: ignore[reportUnusedImport]  # noqa: F401
    from SkiSensorDevTool.utils.ss_message import SSMessage
    import SkiSensorDevTool.utils.return_handler as handler
    import time

    controller: BLEController = BLEController()

    def event_callback(sender: BleakGATTCharacteristic, data: bytearray) -> None:
        logger.debug(msg=f"Event received to the CALLER from {sender}: {data}")

    # asyncio.run(main=controller.start_ble(), debug=True)
    ss_ble_device: BLEDevice = controller.scan()
    ss_client: BleakClient = controller.connect(device=ss_ble_device, onEvent_cb=event_callback)

    data: bytearray = controller.read_char(char_name="fw_version")

    fw_version: str = handler.handle_fw_version(raw_value=data)

    logger.debug(f"Firmware version: {fw_version}")

    message: SSMessage = SSMessage(name="ssssid")

    controller.write_char(char_name='control_point', payload=message.name)

    time.sleep(10)


    controller.disconnect()
