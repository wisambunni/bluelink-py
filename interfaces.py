from enum import Enum, EnumMeta
from typing import Any


class DirectValueMeta(EnumMeta):
    '''
    Metaclass that allows for directly getting an enum attribute.
    This avoids having to access the enums by Class.Enum.value
    '''

    def __getattribute__(self, __name: str) -> Any:
        value = super().__getattribute__(__name)
        if isinstance(value, self):
            value = value.value
        return value


class Session(Enum, metaclass=DirectValueMeta):
    ACCESS_TOKEN = 'access_token'


class Credentials(Enum, metaclass=DirectValueMeta):
    USERNAME = 'username'
    PASSWORD = 'password'
    PIN = 'pin'
    VIN = 'vin'
    CLIENT_ID = 'clientId'
    CLIENT_SECRET = 'clientSecret'


class VehicleConfig(Enum, metaclass=DirectValueMeta):
    REG_ID = 'regId'
    GENERATION = 'generation'
    VIN = 'vin'
    BRAND_INDICATOR = 'brandIndicator'


class SeatClimate(Enum, metaclass=DirectValueMeta):
    HEAT_HIGH = '8'
    HEAT_MEDIUM = '7'
    HEAT_LOW = '6'
    COOL_HIGH = '5'
    COOL_MEDIUM = '4'
    COOL_LOW = '3'
    OFF = '2'
