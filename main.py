import os
import argparse
from tuya_connector import TuyaOpenAPI
import json
import sys

# Определяем путь к директории текущего исполняемого файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

endpoints = {
    'eu_central': 'https://openapi.tuyaeu.com',
    'eu_west': 'https://openapi-weaz.tuyaeu.com',
    'us_west': 'https://openapi.tuyaus.com',
    'us_east': 'https://openapi-ueaz.tuyaus.com',
    'in': 'https://openapi.tuyain.com',
    'cn': 'https://openapi.tuyacn.com'
}


# Функция для сохранения авторизационных данных в файл
def save_credentials(account_name, access_id, access_key, device_id, endpoint_key, device_type):
    data = {
        'ACCESS_ID': access_id,
        'ACCESS_KEY': access_key,
        'DEVICE_ID': device_id,
        'ENDPOINT_KEY': endpoint_key,  # Теперь сохраняем только ключ
        'DEVICE_TYPE': device_type  # Сохраняем тип устройства
    }

    config_path = os.path.join(BASE_DIR, f"{account_name}.json")

    with open(config_path, 'w') as file:
        json.dump(data, file)

    print(f"Credentials saved to {config_path}")


# Функция для загрузки авторизационных данных из файла
def load_credentials(account_name):
    if getattr(sys, 'frozen', False):
        # Если приложение работает как standalone, найдем абсолютный путь к файлу
        config_path = os.path.join(os.path.dirname(sys.executable), f"{account_name}.json")
    else:
        # Иначе, если работает в режиме скрипта, используем текущий рабочий каталог
        config_path = os.path.join(BASE_DIR, f"{account_name}.json")

    with open(config_path, 'r') as file:
        data = json.load(file)

    endpoint = endpoints[data['ENDPOINT_KEY']]  # Извлекаем полный URL из словаря endpoints

    return data['ACCESS_ID'], data['ACCESS_KEY'], data['DEVICE_ID'], endpoint, data['DEVICE_TYPE']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TuyaCLIPython')

    parser.add_argument('--save-credentials', action='store_true', help='Save credentials to a file')

    parser.add_argument('--acc_name', required=True, type=str, help='Account name for the configuration file')
    parser.add_argument('--access-id', type=str, help='Access ID for Tuya API')
    parser.add_argument('--access-key', type=str, help='Access Key for Tuya API')
    parser.add_argument('--device-id', type=str, help='Device ID for Tuya API')

    parser.add_argument('--socket', action='store_true', help='Use socket device type')
    parser.add_argument('--bulb', action='store_true', help='Use bulb device type')

    parser.add_argument('--turn_on', action='store_true', help='Turn on the device')
    parser.add_argument('--turn_off', action='store_true', help='Turn off the device')
    parser.add_argument('--switch_state', action='store_true', help='Switch the state of the device to reverse')
    parser.add_argument('--brightness', '--br', metavar='BRIGHTNESS',
                        help='Set brightness level (0 to 100) or use keywords: min, max')

    parser.add_argument('--response', action='store_true', help='Print API response details')

    parser.add_argument('--eu', action='store_const', dest='endpoint_key', const='eu_central',
                        help='Use Central Europe Data Center endpoint')
    parser.add_argument('--eu_west', action='store_const', dest='endpoint_key', const='eu_west',
                        help='Use Western Europe Data Center endpoint')
    parser.add_argument('--us_west', action='store_const', dest='endpoint_key', const='us_west',
                        help='Use Western America Data Center endpoint')
    parser.add_argument('--us_east', action='store_const', dest='endpoint_key', const='us_east',
                        help='Use Eastern America Data Center endpoint')
    parser.add_argument('--in', action='store_const', dest='endpoint_key', const='in',
                        help='Use India Data Center endpoint')
    parser.add_argument('--cn', action='store_const', dest='endpoint_key', const='cn',
                        help='Use China Data Center endpoint')

    args = parser.parse_args()

    if args.save_credentials:
        if args.socket and args.bulb:
            print("Ошибка: Нельзя использовать аргументы --socket и --bulb одновременно при сохранении.")
            sys.exit(1)
        if not args.endpoint_key:
            print(
                "Ошибка: Пожалуйста, укажите endpoint, используя один из аргументов endpoint (например, --eu, "
                "--us_west и т.д.)")
            sys.exit(1)

        if args.socket:
            DEVICE_TYPE = 'socket'
        elif args.bulb:
            DEVICE_TYPE = 'bulb'
        else:
            DEVICE_TYPE = 'socket'

        save_credentials(args.acc_name, args.access_id, args.access_key, args.device_id, args.endpoint_key, DEVICE_TYPE)

    else:
        try:
            ACCESS_ID, ACCESS_KEY, DEVICE_ID, ENDPOINT, DEVICE_TYPE = load_credentials(args.acc_name)

            if DEVICE_TYPE == 'socket':
                command_code = 'switch_1'
            elif DEVICE_TYPE == 'bulb':
                command_code = 'switch_led'
            else:
                command_code = 'switch_1'  # По умолчанию используем 'switch_1'

            openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
            openapi.connect()

            # Get the status of a single device
            # Пример запроса
            # response = openapi.get("/v1.0/iot-03/devices/{}/status".format(DEVICE_ID))

            if args.switch_state:
                response = openapi.get("/v1.0/iot-03/devices/{}/status".format(DEVICE_ID))
                # Получим текущее состояние устройства из ответа API
                current_state = None
                for item in response['result']:
                    if 'code' in item and item['code'] == command_code:
                        current_state = item['value']
                        break

                # Проверим, удалось ли определить текущее состояние
                if current_state is not None:
                    # Переключим состояние на противоположное
                    commands = {'commands': [{'code': command_code, 'value': not current_state}]}
                    openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
                    print("Device state switched.")
                else:
                    print("Error: Couldn't determine the current state of the device.")

            if args.turn_on:
                commands = {'commands': [{'code': command_code, 'value': True}]}
                openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
                print("Устройство включено.")
            elif args.turn_off:
                commands = {'commands': [{'code': command_code, 'value': False}]}
                openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
                print("Устройство выключено.")

            if args.response:
                response = openapi.get("/v1.0/iot-03/devices/{}/status".format(DEVICE_ID))
                print(response)

            if args.brightness:
                brightness_value = None
                try:
                    brightness_value = int(args.brightness)
                except ValueError:
                    pass  # Если не удалось преобразовать в число, оставляем None

                if args.brightness.lower() == 'min':
                    brightness_value = 0
                elif args.brightness.lower() == 'max':
                    brightness_value = 1000

                if brightness_value is not None:
                    brightness_value = max(10, min(1000, brightness_value * 10))

                commands = {'commands': [{'code': 'bright_value_v2', 'value': brightness_value}]}
                openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
                print("Установлена яркость:", int(brightness_value / 10))

        except FileNotFoundError:
            print(
                f"Ошибка: Конфигурационный файл для аккаунта {args.acc_name} не найден. Пожалуйста, сначала "
                f"используйте --save-credentials.")
            sys.exit(1)
