from datetime import (
    datetime,
    timedelta
)

from . import MedMijUUID

class Token():
    def __init__(self, token, expiration, lifetime):
        self.token = token
        self.expiration = expiration
        self.lifetime = lifetime

    def __str__(self):
        return str(self.token)

def create_token(lifetime=timedelta(seconds=900)):
    return Token(token=str(MedMijUUID()), expiration=datetime.now() + lifetime, lifetime=lifetime)
