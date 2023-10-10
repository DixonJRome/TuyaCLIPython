import os
import argparse
from tuya_connector import TuyaOpenAPI
import json

# Определяем путь к папке ProgramData и подпапке для вашей программы
CONFIG_DIR = os.path.join(os.getenv('PROGRAMDATA'), 'TuyaCLIPython')

ENDPOINT = "https://openapi.tuyaeu.com"


# Функция для сохранения авторизационных данных в файл
def save_credentials(account_name, access_id, access_key, device_id):
    data = {
        'ACCESS_ID': access_id,
        'ACCESS_KEY': access_key,
        'DEVICE_ID': device_id
    }

    # Убеждаемся, что папка существует
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    config_path = os.path.join(CONFIG_DIR, f"{account_name}.json")

    with open(config_path, 'w') as file:
        json.dump(data, file)

    print(f"Credentials saved to {config_path}")


# Функция для загрузки авторизационных данных из файла
def load_credentials(account_name):
    config_path = os.path.join(CONFIG_DIR, f"{account_name}.json")

    with open(config_path, 'r') as file:
        data = json.load(file)

    return data['ACCESS_ID'], data['ACCESS_KEY'], data['DEVICE_ID']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tuya CLI tool')
    parser.add_argument('--save-credentials', action='store_true', help='Save credentials to a file')
    parser.add_argument('--access-id', type=str, help='Access ID for Tuya API')
    parser.add_argument('--access-key', type=str, help='Access Key for Tuya API')
    parser.add_argument('--device-id', type=str, help='Device ID for Tuya API')
    parser.add_argument('-acc_name', required=True, type=str, help='Account name for the configuration file')

    args = parser.parse_args()

    if args.save_credentials:
        save_credentials(args.acc_name, args.access_id, args.access_key, args.device_id)
    else:
        try:
            ACCESS_ID, ACCESS_KEY, DEVICE_ID = load_credentials(args.acc_name)
        except FileNotFoundError:
            print(
                f"Error: Configuration file for account {args.acc_name} not found. Please use --save-credentials first.")
            exit(1)

    openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
    openapi.connect()

    # Get the status of a single device
    response = openapi.get("/v1.0/iot-03/devices/{}/status".format(DEVICE_ID))

    commands = {'commands': [{'code': 'switch_1', 'value': True}]}

    openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)