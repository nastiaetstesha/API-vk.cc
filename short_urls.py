import requests
import os
from dotenv import load_dotenv


def is_shorten_link(url):
    if url.startswith("https://vk.cc/") or url.startswith("vk.cc/"):
        short_url_key = url.split("vk.cc/")[1]
        
        api_url = "https://api.vk.com/method/utils.getLinkStats"
        
        params = {
            'key': short_url_key,  # Сокращенная ссылка
            'interval': 'forever',  # За всё время
            'intervals_count': 1,  # Один период
            'extended': 0,  # Без расширенной статистики
            'v': '5.199',  # Версия API
            'access_token': token  # Токен доступа
        }
        
        link_info = handle_request(api_url, params)
        
        if link_info and 'response' in link_info and link_info['response']:
            return True
    return False

def shorten_link(token, url, private=0):
    api_url = "https://api.vk.com/method/utils.getShortLink"
    
    params = {
        'url': url,  # Оригинальная ссылка
        'private': private,  # (0 — общедоступная, 1 — приватная)
        'v': '5.199',  # Версия API
        'access_token': token  # Токен доступа
    }
    link_info = handle_request(api_url, params)
    if link_info:
        return link_info['response']['short_url']
    return None

def count_clicks(token, original_url, access_key=None, interval='forever', intervals_count=1, extended=0):
    short_url_key = original_url.split("vk.cc/")[1]

    api_url = "https://api.vk.com/method/utils.getLinkStats"
    
    params = {
        'key': short_url_key,  # Сокращенная ссылка (часть URL после "vk.cc/")
        'source': None, 
        'access_key': access_key,  # Ключ для доступа к статистике для приватных ссылок
        'interval': interval,  # Единица времени для подсчета (hour, day, week, month, forever)
        'intervals_count': intervals_count,  # Длительность периода
        'extended': extended,  # Расширенная статистика (пол, возраст, страна, город)
        'v': '5.199',  # Версия API
        'access_token': token  # Токен доступа
    }
    link_info = handle_request(api_url, params)
    if link_info:
        stats = link_info['response']['stats']
        print(f"Статистика по ссылке {original_url}:")
        total_views = sum(stat['views'] for stat in stats)
        return total_views
    return None

def handle_request(api_url, params):
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  

        link_info = response.json()

        if 'error' in link_info:
            error_message = link_info['error'].get('error_msg', 'Неизвестная ошибка')
            print(f"Ошибка: {error_message}")
            return None
        
        return link_info
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None
    except ValueError as e:
        print(f"Ошибка обработки JSON: {e}")
        return None

if __name__ == '__main__':
    load_dotenv()

    original_url = input("Введите ссылку для сокращения: ")
    token = os.environ['VK_TOKEN']
    
    if is_shorten_link(original_url):
        total_views = count_clicks(token, original_url, interval='forever', intervals_count=1, extended=0)
        
        if total_views is not None:
            print(f"Общее количество переходов по короткой ссылке: {total_views}")
        else:
            print("Не удалось получить статистику по ссылке.")
    else:
        short_url = shorten_link(token, original_url)
        if short_url:
            print(f"Сокращенная ссылка: {short_url}")
        else:
            print("Не удалось сократить ссылку.")