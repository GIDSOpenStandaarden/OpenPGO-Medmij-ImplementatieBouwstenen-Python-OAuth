from medmij_oauth.server import MedMijUUID

def test_med_mij_uuid_required_format():
    """
        Test if uuid is in required format: xxxxxxxx-xxxx-4xxx-Nxxx-xxxxxxxxxxxx

        N = 10bb
        x = random hexadecimal
        b = random bit
    """
    uuid_bytes = bytearray(MedMijUUID().uuid.bytes)

    assert uuid_bytes[6] & 0xf0 == 0x40
    assert uuid_bytes[8] & 0xc0 == 0x80
