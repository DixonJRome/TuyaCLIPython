# TuyaCLIPython

TuyaCLIPython - инструмент ~~hardcode~~ командной строки для управления устройством Tuya с использованием их API.

## Установка

Для установки TuyaCLIPython, склонируйте этот репозиторий и установите необходимые зависимости:

```bash
pip install tuya-connector-python
git clone https://github.com/DixonJRome/TuyaCLIPython
cd TuyaCLIPython
```
## Конфигурация (Обязательно!)
Пример создания json файла рядом с main.py. ОБЯЗАТЕЛЬНО УКАЖИТЕ ВАШ ДАТА-ЦЕНТР! (Дата-центр в примере указан в самом конце команды).
```python
python main.py --save-credentials --access-id YOUR_ACCESS_ID --access-key YOUR_ACCESS_KEY --device-id YOUR_DEVICE_ID --acc_name YOUR_ACCOUNT_NAME --eu
```
___В "--acc_name" указать имя файла без .json (~~YOUR_ACCOUNT_NAME.json~~)___

Аргументы дата центров
```bash
  --cn                  Use China Data Center endpoint
  --us_west             Use Western America Data Center endpoint
  --us_east             Use Eastern America Data Center endpoint
  --eu                  Use Central Europe Data Center endpoint
  --eu_west             Use Western Europe Data Center endpoint
  --in                  Use India Data Center endpoint
```

## Использование
Включить розетку
```python
python main.py --acc_name YOUR_ACCOUNT_NAME --turn_on
```
Выключить розетку
```python
python main.py --acc_name YOUR_ACCOUNT_NAME --turn_off
```
Сменить состояние розетки
```python
python main.py --acc_name YOUR_ACCOUNT_NAME --switch_state
```

## Благодарности
Этот проект использует [tuya-connector-python](https://github.com/tuya/tuya-connector-python). Спасибо Tuya за библиотеку.


#### Автор
@dixonjrome
