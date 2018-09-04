import uuid
import secrets

class MedMijUUID():
    """
        UUID in MedMij format: xxxxxxxx-xxxx-4xxx-Nxxx-xxxxxxxxxxxx

        N = 10bb
        x = random hexadecimal
        b = random bit
    """
    def __init__(self):
        _bytes = bytearray.fromhex(secrets.token_hex(16))

        _bytes[6] = (_bytes[6] & 0xF) | 0x40
        _bytes[8] = (_bytes[8] & 0x3F) | 0x80

        self.uuid = uuid.UUID(bytes=bytes(_bytes))

    def __str__(self):
        return str(self.uuid)
