import requests
import datetime
import json

class BlueLink():
    def __init__(self, credentials):
        self.BASE_URL = 'https://owners.hyundaiusa.com'
        self.DASHBOARD_URL = f'{self.BASE_URL}/us/en/page/dashboard.html'
        self.CREDENTIALS = credentials

        self.identity = dict()


    def create_token(self):
        token_url = f'{self.BASE_URL}/etc/designs/ownercommon/us/token.json'
        old_time = datetime.datetime(1970,1,1,0,0,0,0)
        new_time = datetime.datetime.now()
        delta_time = old_time - new_time

        response = requests.get(url=f'{token_url}?reg={delta_time}')
        return response.json()

    
    def validate_token(self, token):
        auth_url = f'{self.BASE_URL}/libs/granite/csrf/token.json'
        response = requests.get(url=auth_url, headers={'csrf_token': token})

        return response.status_code == 200


    def login(self):

        token = self.create_token()

        if not self.validate_token(token['token']):
            print('ERR: Could not validate token')
        else:
            print('Token validated')

        url = f'{self.BASE_URL}/bin/common/connectCar'

        response = requests.post(url=url, data={
            ':cq_csrf_token': token,
            'username': self.CREDENTIALS['username'],
            'password': self.CREDENTIALS['password'],
            'url': f'{self.BASE_URL}/us/en/index.html'
        }).json()

        if response['E_IFRESULT'] != 'Z:Success':
            return

        access_token = response['Token']['access_token']

        url = f'{self.BASE_URL}/bin/common/MyAccountServlet'

        response = requests.post(url=url, data={
            'username': self.CREDENTIALS['username'],
            'token': access_token,
            'url': self.DASHBOARD_URL,
            'service': 'getOwnerInfoService'
        }).json()

        if response['E_IFRESULT'] != 'Z:Success':
            return
        
        reg_id = response['RESPONSE_STRING']['OwnersVehiclesInfo'][0]['RegistrationID']

        self.identity = {
            'username': self.CREDENTIALS['username'],
            'password': self.CREDENTIALS['password'],
            'pin': self.CREDENTIALS['pin'],
            'vin': self.CREDENTIALS['vin'],
            'token': access_token,
            'regId': reg_id
        }

        return self.identity


    def remote_action(self, service_info):
        url = f'{self.BASE_URL}/bin/common/remoteAction'

        response = requests.post(url=url, data=service_info)

        response = response.json()

        if response['E_IFRESULT'] != 'Z:Success':
            print(response)
            return

        print('Request sent successfully')


    def lock(self):
        service_info = {
            'vin': self.CREDENTIALS['vin'],
            'username': self.CREDENTIALS['username'],
            'pin': self.CREDENTIALS['pin'],
            'token': self.identity['token'],
            'url': self.DASHBOARD_URL,
            'gen': 2,
            'regId': self.identity['regId'],
            'service': 'remotelock'
        }

        return self.remote_action(service_info)


    def unlock(self):
        service_info = {
            'vin': self.CREDENTIALS['vin'],
            'username': self.CREDENTIALS['username'],
            'pin': self.CREDENTIALS['pin'],
            'token': self.identity['token'],
            'url': self.DASHBOARD_URL,
            'gen': 2,
            'regId': self.identity['regId'],
            'service': 'remoteunlock'
        }

        return self.remote_action(service_info)
    

    def start(self, preset):
        service_info = {
            'winter': {
                'vin': self.CREDENTIALS['vin'],
                'username': self.CREDENTIALS['username'],
                'pin': self.CREDENTIALS['pin'],
                'token': self.identity['token'],
                'url': self.DASHBOARD_URL,
                'gen': 2,
                'regId': self.identity['regId'],
                'service': 'ignitionstart',
                'airCtrl': 'true',
                'igniOnDuration': '10',
                'airTempvalue': 'HI',
                'defrost': 'false',
                'heating1': '2',
                'seatHeaterVentInfo': json.dumps({'drvSeatHeatState': '8', 'astSeatHeatState': '8'})
            },
            'winter2': {
                'vin': self.CREDENTIALS['vin'],
                'username': self.CREDENTIALS['username'],
                'pin': self.CREDENTIALS['pin'],
                'token': self.identity['token'],
                'url': self.DASHBOARD_URL,
                'gen': 2,
                'regId': self.identity['regId'],
                'service': 'ignitionstart',
                'airCtrl': 'true',
                'igniOnDuration': '10',
                'airTempvalue': 'HI',
                'defrost': 'true',
                'heating1': '2',
                'seatHeaterVentInfo': json.dumps({'drvSeatHeatState': '8', 'astSeatHeatState': '8'})
            },
            'summer': {
                'vin': self.CREDENTIALS['vin'],
                'username': self.CREDENTIALS['username'],
                'pin': self.CREDENTIALS['pin'],
                'token': self.identity['token'],
                'url': self.DASHBOARD_URL,
                'gen': 2,
                'regId': self.identity['regId'],
                'service': 'ignitionstart',
                'airCtrl': 'true',
                'igniOnDuration': '10',
                'airTempvalue': 'LO',
                'defrost': 'false',
                'heating1': '0',
                'seatHeaterVentInfo': json.dumps({'drvSeatHeatState': '4', 'astSeatHeatState': '4'})
            }
        }

        return self.remote_action(service_info[preset])
    

    def stop(self):
        service_info = {
            'vin': self.CREDENTIALS['vin'],
            'username': self.CREDENTIALS['username'],
            'pin': self.CREDENTIALS['pin'],
            'token': self.identity['token'],
            'url': self.DASHBOARD_URL,
            'gen': 2,
            'regId': self.identity['regId'],
            'service': 'ignitionstop'
        }

        return self.remote_action(service_info)