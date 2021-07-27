import os
import time
from datetime import timedelta, datetime
import requests
from telegram import Bot
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler


# деплой бота не выполнял на Heroku, но если необходимо
# для сдачи проекта, то все будет к следующему разу
# не хочется деплоить этот ужас, чтобы он мне присылал
# ошибки в час ночи и пугал :))))
logging.basicConfig(
    level=logging.DEBUG,
    filename='homework_bot_log.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'homework_bot_log.log',
    maxBytes=50000000,
    backupCount=5
)
logger.addHandler(handler)

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


bot = Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    now = datetime.now()
    from_date = now - timedelta(hours=1)
    unix_date = int(time.mktime(from_date.timetuple()))

    while True:
        try:
            homeworks_all = get_homeworks(unix_date)
            homeworks = homeworks_all['homeworks']
            if homeworks != []:
                for homework in homeworks:
                    message = parse_homework_status(homework)
                    send_message(message)
                    logging.info('Сообщение отправлено!')
            time.sleep(5 * 60)

        except Exception as e:
            exc = f'Бот упал с ошибкой: {e}'
            print(exc)
            logging.exception(f'ошибка{e}')
            send_message(exc)
            logging.info('Сообщение отправлено!')
            time.sleep(5)


if __name__ == '__main__':
    main()
