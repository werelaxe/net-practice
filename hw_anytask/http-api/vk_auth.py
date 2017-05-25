import listener
import webbrowser
import multiprocessing
import re

APP_ID = 5331245


class VKAuthException(Exception):
    pass


def build_auth_url(scope, redirect_uri):
    return "https://oauth.vk.com/authorize?client_id={}&scope={}&redirect_uri={}&display=page&v=5.52&response_type=token".format(APP_ID, scope, redirect_uri)


def get_auth_response(scope):
    first_end, second_end = multiprocessing.Pipe()
    multiprocessing.Process(target=listener.start_auth_server, args=(first_end, )).start()
    port = second_end.recv()
    auth_url = build_auth_url(scope, "localhost:{}".format(port))
    webbrowser.open_new(auth_url)
    return second_end.recv()


def parse_token(auth_response: str):
    return re.search("access_token=(.{85})", auth_response).group(1)


def get_token(scope):
    auth_response = get_auth_response(scope)
    token = parse_token(auth_response)
    return token
