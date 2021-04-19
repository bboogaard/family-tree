import requests


def call_api(request, method, endpoint, data):
    scheme = 'https' if request.is_secure() else 'http'
    url = scheme + '://' + request.get_host() + str(endpoint)
    func = getattr(requests, method)
    response = func(
        url,
        data,
        headers={
            'Authorization': 'Token {}'.format(request.user.auth_token)
        }
    )
    try:
        content = response.json()
    except ValueError:
        content = {}
    return response.status_code, content
