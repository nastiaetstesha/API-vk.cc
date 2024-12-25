import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlparse


def is_shorten_link(url):
    parsed_url = urlparse(url)  
    if parsed_url.netloc == 'vk.cc' and parsed_url.path:  
        short_url_key = parsed_url.path.lstrip('/')
        
        api_url = "https://api.vk.com/method/utils.getLinkStats"
        
        params = {
            'key': short_url_key,  
            'interval': 'forever',  
            'intervals_count': 1,  
            'extended': 0,  
            'v': '5.199',  
            'access_token': token  
        }
        
        response = requests.get(api_url, params=params)
        response.raise_for_status()  

        link_info = response.json()

        if 'error' in link_info:
            error_message = link_info['error'].get('error_msg', 'Неизвестная ошибка')
            print(f"Ошибка: {error_message}")
            return None
        
        return bool(link_info and link_info.get('response'))
    return False

def shorten_link(token, url, private=0):
    api_url = "https://api.vk.com/method/utils.getShortLink"
    
    params = {
        'url': url,  
        'private': private,  
        'v': '5.199',  
        'access_token': token  
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()  

    link_info = response.json()

    if 'error' in link_info:
        error_message = link_info['error'].get('error_msg', 'Неизвестная ошибка')
        print(f"Ошибка: {error_message}")
        return None
    if link_info:
        return link_info['response']['short_url']
    return None

def count_clicks(token, original_url, access_key=None, interval='forever', intervals_count=1, extended=0):
    parsed_url = urlparse(original_url)  
    short_url_key = parsed_url.path.lstrip('/')

    api_url = "https://api.vk.com/method/utils.getLinkStats"
    
    params = {
        'key': short_url_key,  
        'source': None, 
        'access_key': access_key, 
        'interval': interval,  
        'intervals_count': intervals_count,  
        'extended': extended,  
        'v': '5.199',  
        'access_token': token 
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()  

    link_info = response.json()

    if 'error' in link_info:
        error_message = link_info['error'].get('error_msg', 'Неизвестная ошибка')
        print(f"Ошибка: {error_message}")
        return None
        
    if link_info:
        stats = link_info['response']['stats']
        print(f"Статистика по ссылке {original_url}:")
        total_views = sum(stat['views'] for stat in stats)
        return total_views
    return None


if __name__ == '__main__':
    load_dotenv()

    original_url = input("Введите ссылку для сокращения: ")
    token = os.environ['VK_TOKEN']
    try:
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
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
    except ValueError as e:
        print(f"Ошибка обработки JSON: {e}")
