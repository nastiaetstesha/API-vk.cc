import requests
import os
import argparse
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
            error_message = link_info['error'].get(
                'error_msg', 'Неизвестная ошибка'
                )
            raise Exception(error_message)

        return bool(link_info.get('response'))
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
        error_message = link_info['error'].get(
            'error_msg', 'Неизвестная ошибка'
            )
        raise Exception(error_message)
    if link_info:
        return link_info['response']['short_url']
    return None


def count_clicks(
    token,
    original_url,
    access_key=None,
    interval='forever',
    intervals_count=1,
    extended=0
):

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
        error_message = link_info['error'].get(
            'error_msg', 'Неизвестная ошибка'
            )
        raise Exception(error_message)
    if link_info:
        stats = link_info['response']['stats']
        total_views = sum(stat['views'] for stat in stats)
        return total_views
    return None


if __name__ == '__main__':
    load_dotenv()

    # original_url = input("Введите ссылку для сокращения: ")

    # token = os.environ['VK_TOKEN']
    parser = argparse.ArgumentParser(
        description="Сокращение ссылок и получение статистики по ним."
        )
    parser.add_argument(
        'url',
        type=str,
        help="Введите ссылку для сокращения или проверки."
        )
    parser.add_argument(
        '--token',
        type=str,
        default=os.environ.get('VK_TOKEN'),
        help="Токен для доступа к VK API."
        )

    args = parser.parse_args()

    try:
        original_url = args.url
        token = args.token
        if is_shorten_link(original_url):
            total_views = count_clicks(
                token, original_url,
                interval='forever',
                intervals_count=1,
                extended=0
                )
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
    except Exception as e:
        print(f"Ошибка: {e}")
