from urllib.request import urlopen
import vk_auth
import json


LINK_TEMPLATE = "https://api.vk.com/method/{}?{}&access_token={}"


def prepare_param(param):
    if type(param[1]) == list:
        return "{}={}".format(param[0], ','.join(map(str, param[1])))
    else:
        return "{}={}".format(param[0], str(param[1]))


def make_params_str(kwargs):
    return '&'.join(map(prepare_param, kwargs.items()))


class _VKCallableObject:
    def __init__(self, method_name, token):
        self.method_name = method_name
        self.token = token

    def __call__(self, **kwargs):
        request_url = LINK_TEMPLATE.format(self.method_name, make_params_str(kwargs), self.token)
        return  json.loads(urlopen(request_url).read().decode())


class _InterClass:
    def __init__(self, name, token):
        self.name = name
        self.token = token

    def __getattr__(self, method_name):
        return _VKCallableObject("{}.{}".format(self.name, method_name), self.token)


class VKApi:
    def __init__(self, scope: str, token=None):
        self.scope = scope
        self._token = vk_auth.get_token(scope) if token is None else token

    def __getattr__(self, inter_name):
        return _InterClass(inter_name, self._token)
