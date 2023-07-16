from interfaces import Credentials, Session, VehicleConfig, SeatClimate
from math import e
import logging
import requests

logging.basicConfig(level=logging.INFO)


class BlueLink():
    """
    Blue Link wrapper class.

    Communicates with BlueLink endpoints and sends HTTP requests.
    :param credentials: Containing your user credentials. the format is as follows:
    {
      'username': '<your_email>',
      'password': '<your_hyundaiusa_password>',
      'pin': '<your_hyundai_pin>',
      'vin': '<your_vehicle_vin>'
    }
    """

    def __init__(self, credentials=None):
        self.HOST = 'api.telematics.hyundaiusa.com'
        self.BASE_URL = f'https://{self.HOST}'

        self.__credentials = credentials
        self.__session = dict()
        self.__vehicle_config = ()

    def __get_default_headers(self):
        return {
            'access_token': self.__session[Session.ACCESS_TOKEN],
            'client_id': self.__credentials[Credentials.CLIENT_ID],
            'Host': self.HOST,
            'User-Agent': 'okhttp/3.12.0',
            'regestrationId': self.__vehicle_config[VehicleConfig.REG_ID],
            'gen': self.__vehicle_config[VehicleConfig.GENERATION],
            'username': self.__credentials[Credentials.USERNAME],
            'vin': self.__vehicle_config[VehicleConfig.VIN],
            'APPCLOUD-VIN': self.__vehicle_config[VehicleConfig.VIN],
            'Language': '0',
            'from': 'SPA',
            'to': 'ISS',
            'encryptFlag': 'false',
            'brandIndicator': self.__vehicle_config[VehicleConfig.BRAND_INDICATOR],
            'bluelinkservicepin': self.__credentials[Credentials.PIN],
            'offset': '-4',
        }

    def __get_desired_cabin_temp(self, outdoor_temp):
        """
        Modified version of a sigmoid function
        This maps an outdoor temperature (x) to a cabin temperature (y) so that
        the cabin temperature automatically adjusts to the outside weather.

        Formula:
                a-b
        a - ------------
              1+e^(6-.09x)

        where a is the highest possible cabin temp
        and b is the lowest possible cabin temp

        :param outdoor_temp: Outdoor temperature
        :type outdoor_temp: int

        :return: Transformed cabin temperature
        :rtype: int
        """
        UPPER_CABIN_TEMP = 82
        LOWER_CABIN_TEMP = 62
        CURVE_HEIGHT = UPPER_CABIN_TEMP - LOWER_CABIN_TEMP

        exponent = 6 - 0.09*outdoor_temp
        return UPPER_CABIN_TEMP - (CURVE_HEIGHT/(1+e**exponent))

    def __get_desired_seat_climate(self, outdoor_temp):
        """
        Takes an outdoor temperature value and recommends the best seat climate setting.

        :param outdoor_temp: Outdoor temperature
        :type outdoor_temp: int

        :return: Recommended seat climate setting
        :rtype: SeatClimate
        """
        CUTOFF_TEMP = 70
        TEMP_OFFSET = 5
        if CUTOFF_TEMP >= outdoor_temp >= CUTOFF_TEMP - TEMP_OFFSET:
            return SeatClimate.HEAT_LOW

        if CUTOFF_TEMP - TEMP_OFFSET >= outdoor_temp >= CUTOFF_TEMP - (TEMP_OFFSET*2):
            return SeatClimate.HEAT_MEDIUM

        if CUTOFF_TEMP - (TEMP_OFFSET*2) >= outdoor_temp:
            return SeatClimate.HEAT_HIGH

        if CUTOFF_TEMP <= outdoor_temp <= CUTOFF_TEMP + TEMP_OFFSET:
            return SeatClimate.COOL_LOW

        if CUTOFF_TEMP + TEMP_OFFSET <= outdoor_temp <= CUTOFF_TEMP + (TEMP_OFFSET*2):
            return SeatClimate.COOL_MEDIUM

        if CUTOFF_TEMP + (TEMP_OFFSET*2) <= outdoor_temp:
            return SeatClimate.COOL_HIGH

        return SeatClimate.OFF

    def login(self, credentials=None):
        """
        Logs in to BlueLink, creates a session, and retrieves vehicle configs.

        :param credentials: User credentials (similar to class param)
        :type credentals: dict
        """
        url = f'{self.BASE_URL}/v2/ac/oauth/token'
        credentials = self.__credentials if not credentials else credentials
        headers = {
            'User-Agent': 'PostmanRuntime/7.26.10',
            'client_id': credentials[Credentials.CLIENT_ID],
            'client_secret': credentials[Credentials.CLIENT_SECRET]
        }
        body = {
            'username': credentials[Credentials.USERNAME],
            'password': credentials[Credentials.PASSWORD],
        }
        logging.info('Logging in to BlueLink')

        response = requests.post(url=url, headers=headers, data=body)

        if response.status_code != 200:
            logging.error('Failed to log in to BlueLink')
            raise ConnectionError(response.content)

        self.__session[Session.ACCESS_TOKEN] = response.json()[
            'access_token']
        self.get_enrolled_vehicle()

    def get_enrolled_vehicle(self):
        """
        Retrieves the vehicle configurations.

        :return: Vehicle configuration
        :rtype: dict
        """
        url = f'{self.BASE_URL}/ac/v2/enrollment/details/{self.__credentials[Credentials.USERNAME]}'
        headers = {
            'access_token': self.__session[Session.ACCESS_TOKEN],
            'client_id': self.__credentials[Credentials.CLIENT_ID],
            'Host': self.HOST,
            'includeNonConnectedVehicles': 'N',
        }

        logging.info('Retrieving vehicle config')

        response = requests.get(url=url, headers=headers)
        response_body = response.json()

        if response.status_code != 200:
            logging.error('Failed to get enrolled vehicles')
            raise ConnectionError(response_body)

        vehicle_details = response_body['enrolledVehicleDetails'][0]['vehicleDetails']

        self.__vehicle_config = {
            'regId': vehicle_details['regid'],
            'generation': vehicle_details['vehicleGeneration'],
            'vin': vehicle_details['vin'],
            'brandIndicator': vehicle_details['brandIndicator'],
        }

        return self.__vehicle_config

    def lock(self):
        """
        Locks the vehicle.

        :return: response status code
        :rtype: int
        """
        url = f'{self.BASE_URL}/ac/v2/rcs/rdo/off'
        headers = self.__get_default_headers()
        body = {
            'userName': self.__credentials[Credentials.USERNAME],
            'vin': self.__vehicle_config[VehicleConfig.VIN],
        }

        logging.info('Locking vehicle')

        response = requests.post(url=url, headers=headers, data=body)

        if response.status_code != 200:
            logging.error('Failed to lock vehicle')
            raise ConnectionError(response.content)

        return response.status_code

    def unlock(self):
        """
        Unlocks the vehicle

        :return: response status code
        :rtype: int
        """
        url = f'{self.BASE_URL}/ac/v2/rcs/rdo/on'
        headers = self.__get_default_headers()
        body = {
            'userName': self.__credentials[Credentials.USERNAME],
            'vin': self.__vehicle_config[VehicleConfig.VIN],
        }

        logging.info('Unlocking vehicle')

        response = requests.post(url=url, headers=headers, data=body)

        if response.status_code != 200:
            logging.error('Failed to unlock vehicle')
            raise ConnectionError(response.content)

        return response.status_code

    def stop(self):
        """
        Stops vehicle.
        Note: This will not work unless the vehicle was started through
        a remote session.

        :return: response status code
        :rtype: int
        """
        url = f'{self.BASE_URL}/ac/v2/rcs/rsc/stop'
        headers = self.__get_default_headers()

        logging.info('Stopping vehicle')

        response = requests.post(url=url, headers=headers)

        if response.status_code != 200:
            logging.error('Failed to stop vehicle')
            raise ConnectionError(response.content)

        return response.status_code

    def start(self, outdoor_temp=70, defrost=False):
        """
        Starts the vehicle with the best possible climate settings.
        This will set the appropriate cabin temperature as well as seat climate
        and defrost, heated steering.

        :param outdoor_temp: Outside temperature
        :type outdoor_temp: int

        :param defrost: Flag whether to turn defrosters on
        :type defrost: bool

        :return: response status code
        :rtype: int
        """
        print(outdoor_temp)
        print(defrost)
        url = f'{self.BASE_URL}/ac/v2/rcs/rsc/start'
        headers = self.__get_default_headers()

        cabin_temp = self.__get_desired_cabin_temp(outdoor_temp)

        seat_climate = self.__get_desired_seat_climate(outdoor_temp)

        body = {
            'Ims': 0,
            'airCtrl': 1,
            'airTemp': {
                'unit': 1,
                'value': f'{round(cabin_temp)}'
            },
            'defrost': defrost,
            'heating1': +(outdoor_temp < 70),
            'igniOnDuration': 10,
            'seatHeaterVentInfo': {
                'drvSeatHeatState': seat_climate,
                'astSeatHeatState': seat_climate,
            },
            'username': self.__credentials[Credentials.USERNAME],
            'vin': self.__credentials[Credentials.VIN],
        }

        logging.info('Starting vehicle')

        response = requests.post(url=url, headers=headers, json=body)

        if response.status_code != 200:
            logging.error('Failed to start vehicle')
            raise ConnectionError(response.content)

        return response.status_code
