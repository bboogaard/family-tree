import requests
from django.conf import settings


def call_api(endpoint, data, user):
    response = requests.post(
        settings.API_URL + endpoint,
        data,
        headers={
            'Authorization': 'Token {}'.format(user.auth_token)
        }
    )
    return response.status_code, response.json()
