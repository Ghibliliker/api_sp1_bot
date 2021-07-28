import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
from dotenv import load_dotenv
from telegram import Bot

logging.basicConfig(
    level=logging.DEBUG,
    filename='homework_bot_log.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'homework_bot_log.log',
    maxBytes=50_000_000,
    backupCount=5
)
logger.addHandler(handler)

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_YAND = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
PAUSE_CHECK = 300
PAUSE_ER = 5

bot = Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    if homework['homework_name']:
        homework_name = homework['homework_name']
    else:
        homework_name = 'название неизвестно'
    if homework['status'] == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework['status'] == 'reviewing':
        verdict = 'Работа взята на ревью.'
    elif homework['status'] == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    else:
        logging.info(homework['status'])
        return f'Ваша работа {homework_name} пришла с неизвестным статусом'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = URL_YAND
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
    except requests.exceptions.RequestException as e:
        logging.exception(f'ошибка{e}')
    except Exception as e:
        logging.exception(f'ошибка{e}')
    try:
        homework_statuses.json()
    except SyntaxError as e:
        logging.exception(f'ошибка{e}')
    else:
        return homework_statuses.json()


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            homeworks_all = get_homeworks(current_timestamp)
            homeworks = homeworks_all['homeworks']
            if homeworks:
                for homework in homeworks:
                    message = parse_homework_status(homework)
                    send_message(message)
                    logging.info('Сообщение отправлено!')
            time.sleep(PAUSE_CHECK)
            current_timestamp = int(time.time())

        except Exception as e:
            exc = f'Бот упал с ошибкой: {e}'
            logging.exception(f'ошибка{e}')
            send_message(exc)
            logging.info('Сообщение отправлено!')
            time.sleep(PAUSE_ER)


if __name__ == '__main__':
    main()
