import os
import argparse
from tuya_connector import TuyaOpenAPI
import json

# Определяем путь к директории текущего исполняемого файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

endpoints = {
    'cn': 'https://openapi.tuyacn.com',
    'us_west': 'https://openapi.tuyaus.com',
    'us_east': 'https://openapi-ueaz.tuyaus.com',
    'eu_central': 'https://openapi.tuyaeu.com',
    'eu_west': 'https://openapi-weaz.tuyaeu.com',
    'in': 'https://openapi.tuyain.com'
}


# Функция для сохранения авторизационных данных в файл
def save_credentials(account_name, access_id, access_key, device_id, endpoint_key):
    data = {
        'ACCESS_ID': access_id,
        'ACCESS_KEY': access_key,
        'DEVICE_ID': device_id,
        'ENDPOINT_KEY': endpoint_key  # Теперь сохраняем только ключ
    }

    config_path = os.path.join(BASE_DIR, f"{account_name}.json")

    with open(config_path, 'w') as file:
        json.dump(data, file)

    print(f"Credentials saved to {config_path}")


# Функция для загрузки авторизационных данных из файла
def load_credentials(account_name):
    config_path = os.path.join(BASE_DIR, f"{account_name}.json")

    with open(config_path, 'r') as file:
        data = json.load(file)

    endpoint = endpoints[data['ENDPOINT_KEY']]  # Извлекаем полный URL из словаря endpoints

    return data['ACCESS_ID'], data['ACCESS_KEY'], data['DEVICE_ID'], endpoint


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tuya CLI tool')
    parser.add_argument('--save-credentials', action='store_true', help='Save credentials to a file')

    parser.add_argument('--access-id', type=str, help='Access ID for Tuya API')
    parser.add_argument('--access-key', type=str, help='Access Key for Tuya API')
    parser.add_argument('--device-id', type=str, help='Device ID for Tuya API')

    parser.add_argument('--acc_name', required=True, type=str, help='Account name for the configuration file')

    parser.add_argument('--turn_on', action='store_true', help='Turn on the device')
    parser.add_argument('--turn_off', action='store_true', help='Turn off the device')

    parser.add_argument('--cn', action='store_const', dest='endpoint_key', const='cn',
                        help='Use China Data Center endpoint')
    parser.add_argument('--us_west', action='store_const', dest='endpoint_key', const='us_west',
                        help='Use Western America Data Center endpoint')
    parser.add_argument('--us_east', action='store_const', dest='endpoint_key', const='us_east',
                        help='Use Eastern America Data Center endpoint')
    parser.add_argument('--eu', action='store_const', dest='endpoint_key', const='eu_central',
                        help='Use Central Europe Data Center endpoint')
    parser.add_argument('--eu_west', action='store_const', dest='endpoint_key', const='eu_west',
                        help='Use Western Europe Data Center endpoint')
    parser.add_argument('--in', action='store_const', dest='endpoint_key', const='in',
                        help='Use India Data Center endpoint')

    args = parser.parse_args()

    if args.save_credentials:
        if not args.endpoint_key:
            print(
                "Ошибка: Пожалуйста, укажите endpoint, используя один из аргументов endpoint (например, --cn, --us_west и т.д.)")
            exit(1)
        save_credentials(args.acc_name, args.access_id, args.access_key, args.device_id, args.endpoint_key)
    else:
        try:
            ACCESS_ID, ACCESS_KEY, DEVICE_ID, ENDPOINT = load_credentials(args.acc_name)

            openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
            openapi.connect()

            # Get the status of a single device
            response = openapi.get("/v1.0/iot-03/devices/{}/status".format(DEVICE_ID))

            if args.turn_on:
                commands = {'commands': [{'code': 'switch_1', 'value': True}]}
                openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
                print("Устройство включено.")

            elif args.turn_off:
                commands = {'commands': [{'code': 'switch_1', 'value': False}]}
                openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
                print("Устройство выключено.")
        except FileNotFoundError:
            print(
                f"Ошибка: Конфигурационный файл для аккаунта {args.acc_name} не найден. Пожалуйста, сначала используйте --save-credentials.")
            exit(1)
