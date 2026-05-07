class BLEController:

    def __init__(self) -> None:
        pass

    def scan(self) -> None:
        ''' Scan for available ble devices and stop when a ski sensor is found, return that device'''
        pass

    def connect(self) -> None:
        '''Connect to a target ble device, returns the connection'''
        pass

    def disconnect(self) -> None:
        '''Disconnects an active connection with a ble device'''
        pass

    def write_char(self, char_name, payload) -> None:
        '''Writes to a specified characteristic'''
        pass

    def read_char(self, char_name) -> None:
        '''Reads from a specified characterisitic'''
        pass

    
