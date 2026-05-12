
def handle_fw_version(raw_value: bytearray) -> str:
    return raw_value[:8].split(sep=b'\x00')[0].decode(encoding='utf-8')