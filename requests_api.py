import requests

HOST = 'http://127.0.0.1:8000'


def register(username, password):
    resp = requests.post(f'{HOST}/register', json={'username': username, 'password': password})
    print(f'Register: {resp.status_code}')
    if resp.status_code == 201:
        print('User created')
    else:
        print(resp.json())


def login(username, password):
    resp = requests.post(f'{HOST}/login', json={'username': username, 'password': password})
    print(f'Login: {resp.status_code}')
    if resp.status_code == 200:
        token = resp.json()['access_token']
        print('Token:', token)
        return token
    else:
        print(resp.json())
        return None


def create_ad(token, title, description):
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.post(f'{HOST}/advertisements', json={'title': title, 'description': description}, headers=headers)
    print(f'Create ad: {resp.status_code}')
    print(resp.json())
    return resp.json().get('id')


def get_ad(ad_id):
    resp = requests.get(f'{HOST}/advertisements/{ad_id}/')
    print(f'Get ad {ad_id}: {resp.status_code}')
    print(resp.json())


def get_ads_list():
    resp = requests.get(f'{HOST}/advertisements')
    print(f'Get ads list: {resp.status_code}')
    if resp.status_code == 204:
        print('No ads')
    else:
        print(resp.json())


def patch_ad(token, ad_id, updates):
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.patch(f'{HOST}/advertisements/{ad_id}/', json=updates, headers=headers)
    print(f'Patch ad {ad_id}: {resp.status_code}')
    print(resp.json())


def delete_ad(token, ad_id):
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.delete(f'{HOST}/advertisements/{ad_id}/', headers=headers)
    print(f'Delete ad {ad_id}: {resp.status_code}')
    if resp.status_code == 204:
        print('Deleted (no content)')
    else:
        print(resp.json())


if __name__ == '__main__':
    print('=== Регистрация и логин ===')
    register('testuser', 'secret123')
    token = login('testuser', 'secret123')
    if not token:
        exit(1)

    print('\n=== Список объявлений (пуст) ===')
    get_ads_list()

    print('\n=== Создание объявления ===')
    ad_id = create_ad(token, 'Велосипед', 'Горный, 26 дюймов')

    if ad_id:
        print('\n=== Список объявлений (одно) ===')
        get_ads_list()

        print('\n=== Получение объявления ===')
        get_ad(ad_id)

        print('\n=== Обновление объявления ===')
        patch_ad(token, ad_id, {'title': 'Супер горный велосипед'})

        print('\n=== Удаление объявления ===')
        delete_ad(token, ad_id)

        print('\n=== Список объявлений (снова пуст) ===')
        get_ads_list()

        print('\n=== Проверка удаления ===')
        get_ad(ad_id)
