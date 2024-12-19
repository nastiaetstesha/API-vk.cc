import requests
import os
from dotenv import load_dotenv


def is_shorten_link(url):
    # Проверка, является ли ссылка короткой (согласно формату vk.cc)
    return url.startswith("https://vk.cc/") or url.startswith("vk.cc/")

def shorten_link(token, url, private=0):
    # Адрес для API ВКонтакте
    api_url = "https://api.vk.com/method/utils.getShortLink"
    
    # Параметры для запроса
    params = {
        'url': url,  # Оригинальная ссылка
        'private': private,  # (0 — общедоступная, 1 — приватная)
        'v': '5.199',  # Версия API
        'access_token': token  # Токен доступа
    }

    try:
        # Отправка запроса
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Проверка на успешный HTTP-ответ

        data = response.json()
        
        # Проверка на наличие ошибки в ответе API
        if 'error' in data:
            error_message = data['error'].get('error_msg', 'Неизвестная ошибка')
            print(f"Ошибка: {error_message}")
            return None
        else:
            # Возвращаем сокращенную ссылку
            short_url = data['response']['short_url']
            return short_url
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None
    except ValueError as e:
        print(f"Ошибка обработки JSON: {e}")
        return None

def count_clicks(token, original_url, access_key=None, interval='forever', intervals_count=1, extended=0):
    short_url_key = original_url.split("vk.cc/")[1]

    # Адрес для API ВКонтакте
    api_url = "https://api.vk.com/method/utils.getLinkStats"
    
    # Параметры для запроса
    params = {
        'key': short_url_key,  # Сокращенная ссылка (часть URL после "vk.cc/")
        'source': None,  # ?
        'access_key': access_key,  # Ключ для доступа к статистике для приватных ссылок
        'interval': interval,  # Единица времени для подсчета (hour, day, week, month, forever)
        'intervals_count': intervals_count,  # Длительность периода
        'extended': extended,  # Расширенная статистика (пол, возраст, страна, город)
        'v': '5.199',  # Версия API
        'access_token': token  # Токен доступа
    }

    try:
        # Отправка запроса
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Проверка на успешный HTTP-ответ

        data = response.json()
        
        # Проверка на наличие ошибки в ответе API
        if 'error' in data:
            error_message = data['error'].get('error_msg', 'Неизвестная ошибка')
            print(f"Ошибка: {error_message}")
            return None
        
        # Статистика переходов
        stats = data['response']['stats']
        print(f"Статистика по ссылке {original_url}:")
        # for stat in stats:
            # print(f"Время: {stat['timestamp']}, Количество переходов: {stat['views']}")
        # Возвращаем общее количество переходов
        total_views = sum(stat['views'] for stat in stats)
        return total_views

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None
    except ValueError as e:
        print(f"Ошибка обработки JSON: {e}")
        return None
    
if __name__ == '__main__':
    load_dotenv()

    original_url = input("Введите ссылку для сокращения: ")
    token = os.environ['TOKEN']
    
    if is_shorten_link(original_url):
        total_views = count_clicks(token, original_url, interval='forever', intervals_count=1, extended=0)
        
        if total_views is not None:
            print(f"Общее количество переходов по короткой ссылке: {total_views}")
        else:
            print("Не удалось получить статистику по ссылке.")
    else:
        # Если ссылка длинная, сокращаем её
        short_url = shorten_link(token, original_url)
        if short_url:
            print(f"Сокращенная ссылка: {short_url}")
        else:
            print("Не удалось сократить ссылку.")