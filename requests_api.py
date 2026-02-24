import requests

HOST = 'http://127.0.0.1:8000'


def post():
    post_data = {
        'title': 'Selling an aquarium fish',
        'description': 'Neon fish, really cool',
        'owner': 'Valerchik'
    }
    response = requests.post(f'{HOST}/advertisements', json=post_data)
    print(f'POST {response.status_code}')
    print(response.json())
    return response.json().get('id')


def get(ad_id: int):
    response = requests.get(f'{HOST}/advertisements/{ad_id}/')
    print(f'GET {response.status_code}')
    print(response.json())


def patch(ad_id: int):
    update_data = {
        'title': 'Selling a rare neon fish',
        'description': 'Very cool, price down'
    }
    response = requests.patch(f'{HOST}/advertisements/{ad_id}/', json=update_data)
    print(f'PATCH {response.status_code}')
    print(response.json())


def delete(ad_id: int):
    response = requests.delete(f'{HOST}/advertisements/{ad_id}/')
    print(f'DELETE {response.status_code}')
    print(response.json())


if __name__ == '__main__':
    print("=== TESTING API ===")
    ad_id = post()
    if ad_id:
        get(ad_id)
        patch(ad_id)
        get(ad_id)
        delete(ad_id)
        get(ad_id)
