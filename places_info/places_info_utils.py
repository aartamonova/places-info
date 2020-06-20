import functools
import json
import os

import requests
import rq
from flask import abort, jsonify, make_response, flash, session, url_for, render_template
from flask.cli import ScriptInfo
from flask_api.status import (HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
                              HTTP_500_INTERNAL_SERVER_ERROR, HTTP_504_GATEWAY_TIMEOUT, HTTP_200_OK)
from redis import Redis
from requests.exceptions import ConnectTimeout, ConnectionError, ReadTimeout, Timeout
from werkzeug.utils import redirect

from config import Config
from places_info.places_info_model import TokenData

redis_url = Config.REDISTOGO_URL
redis_connection = Redis.from_url(redis_url)
queue = rq.Queue(connection=redis_connection)


def admin_required(foo):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        try:
            session['admin']
        except:
            return render_template('errors/404.html'), 404

        if not session['admin']:
            return render_template('errors/404.html'), 404
        else:
            return foo(*args, **kwargs)

    return wrapper


def login_required(foo):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        try:
            session['login']
        except:
            flash('Авторизуйтесь, чтобы продолжить', 'info')
            return redirect(url_for('auth.login'))

        if not session['login']:
            flash('Авторизуйтесь, чтобы продолжить', 'info')
            return redirect(url_for('auth.login'))
        else:
            return foo(*args, **kwargs)

    return wrapper


def response_500_error():
    return make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)


def request_error_handler(foo):
    @functools.wraps(foo)
    def wrapper(*args):
        response = None
        try:
            response = foo(*args)
        except ConnectionError:
            response = make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)
        except (Timeout, ConnectTimeout, ReadTimeout):
            return make_response(jsonify('Истекло время ожидания запроса от сервера'), HTTP_504_GATEWAY_TIMEOUT)
        except:
            abort(404)

        if response.status_code == HTTP_401_UNAUTHORIZED:
            abort(403)
        if response.status_code == HTTP_403_FORBIDDEN:
            return make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)
        if response.status_code == HTTP_500_INTERNAL_SERVER_ERROR:
            return make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)
        if response.status_code == HTTP_400_BAD_REQUEST:
            return make_response(jsonify('Неверные данные. Пожалуйста, '
                                         'проверьте введенные данные '
                                         'и попробуйте еще раз'), HTTP_400_BAD_REQUEST)
        else:
            return response

    return wrapper


def form_action_data(action, result, name=None):
    try:
        login = session['login']
    except:
        return None
    if login:
        if name:
            pass

        action_type = Config.ACTIONS[action]

        if name:
            description = action + ' "' + name + '"'
        else:
            description = ''.join(action)

        data = {'login': str(login),
                'type': str(action_type),
                'description': str(description),
                'result': str(result)}
        return data
    return None


def get_access_header(request_app):
    '''Сформировать хедер с access-токеном'''
    # Сначала попробовать прочитать из БД, нет/истек - запросить у сервиса авторизации
    token = TokenData.get_by_apps(Config.SOURCE_APP, request_app)
    if token and TokenData.check_token(token):
        return {'Gui-Token': token.access_token}

    try:
        response = requests.get(Config.AUTH_SERVICE_URL + '/token/get',
                                'source_app=' + Config.SOURCE_APP + '&request_app=' + str(request_app))
        if response.status_code == HTTP_200_OK:
            access_token = json.loads(response.content)['access_token']
            TokenData.save(Config.SOURCE_APP, request_app, access_token)
            return {'Gui-Token': access_token}
    except:
        return None
    return None


@request_error_handler
def get_tag_helper(tag_id):
    '''Получить тег по id'''
    headers = get_access_header(Config.TAGS_APP)
    if headers:
        response = requests.get(Config.TAGS_SERVICE_URL + '/tags/' + str(tag_id), headers=headers)
        return response
    return response_500_error()


@request_error_handler
def get_all_tags_helper():
    '''Получить список всех тегов'''
    headers = get_access_header(Config.TAGS_APP)
    if headers:
        response = requests.get(Config.TAGS_SERVICE_URL + '/tags', headers=headers)
        return response
    return response_500_error()


@request_error_handler
def add_tag_helper(name, login):
    '''Добавить тег'''
    headers = get_access_header(Config.TAGS_APP)
    if headers:
        data = {'name': str(name), 'added_by': str(login)}
        response = requests.post(Config.TAGS_SERVICE_URL + '/tags', data=json.dumps(data), headers=headers)
        return response
    return response_500_error()


@request_error_handler
def get_tags_place_helper(place_id):
    '''Получить теги для выбранного места'''
    headers = get_access_header(Config.TAGS_APP)
    if headers:
        response = requests.get(Config.TAGS_SERVICE_URL + '/places/' + str(place_id) + '/tags', headers=headers)
        return response
    return response_500_error()


@request_error_handler
def get_places_tag_helper(tag_id):
    '''Получить места для выбранного тега'''
    headers = get_access_header(Config.TAGS_APP)
    if headers:
        response = requests.get(Config.TAGS_SERVICE_URL + '/tags/' + str(tag_id) + '/places', headers=headers)
        return response
    return response_500_error()


@request_error_handler
def delete_tag_helper(tag_id):
    '''Удалить тег по id'''
    headers = get_access_header(Config.TAGS_APP)
    if headers:
        response = requests.delete(Config.TAGS_SERVICE_URL + '/tags/' + str(tag_id), headers=headers)
        return response
    return response_500_error()


@request_error_handler
def get_place_helper(place_id):
    '''Получить место по id'''
    headers = get_access_header(Config.PLACES_APP)
    if headers:
        response = requests.get(Config.PLACES_SERVICE_URL + '/places/' + str(place_id), headers=headers)
        return response
    return response_500_error()


@request_error_handler
def get_all_places_helper(page):
    '''Получить пагинированный список всех мест'''
    headers = get_access_header(Config.PLACES_APP)
    if headers:
        response = requests.get(Config.PLACES_SERVICE_URL + '/places', 'page=' + str(page), headers=headers)
        return response
    return response_500_error()


@request_error_handler
def get_search_places_helper(page, search_str):
    '''Поиск мест по названию'''
    headers = get_access_header(Config.PLACES_APP)
    if headers:
        response = requests.get(Config.PLACES_SERVICE_URL + '/places/search',
                                'page=' + str(page) + '&name=' + str(search_str), headers=headers)
        return response
    return response_500_error()


@request_error_handler
def get_search_tag_places_helper(page, search_str):
    headers = get_access_header(Config.PLACES_APP)
    if headers:
        response = requests.get(Config.PLACES_SERVICE_URL + '/places/search',
                                'page=' + str(page) + '&name=' + str(search_str), headers=headers)
        return response
    return response_500_error()


@request_error_handler
def add_place_helper(name, place_type, description, phone, address, login):
    '''Добавить место'''
    headers = get_access_header(Config.PLACES_APP)
    if headers:
        data = {'name': str(name),
                'type': str(place_type),
                'description': str(description),
                'phone': str(phone),
                'address': str(address),
                'added_by': str(login)}
        response = requests.post(Config.PLACES_SERVICE_URL + '/places', data=json.dumps(data), headers=headers)
        return response
    return response_500_error()


@request_error_handler
def edit_place_helper(place_id, name, place_type, description, phone, address):
    '''Отредактировать место'''
    headers = get_access_header(Config.PLACES_APP)
    if headers:
        data = {'id': str(place_id),
                'name': str(name),
                'type': str(place_type),
                'description': str(description),
                'phone': str(phone),
                'address': str(address)}
        response = requests.put(Config.PLACES_SERVICE_URL + '/places/' + str(place_id), data=json.dumps(data),
                                headers=headers)
        return response
    return response_500_error()


@request_error_handler
def edit_place_tags_helper(place_id, tags):
    '''Изменить выбранные теги для выбранного места'''
    headers = get_access_header(Config.TAGS_APP)
    if headers:
        data = {'place_id': str(place_id), 'tags': tags}
        response = requests.post(Config.TAGS_SERVICE_URL + '/places/tags/edit', data=json.dumps(data),
                                 headers=headers)
        return response
    return response_500_error()


@request_error_handler
def add_place_tags_helper(place_id, tags):
    '''Добавить выбранные теги к выбранному месту'''
    headers = get_access_header(Config.TAGS_APP)
    if headers:
        data = {'place_id': str(place_id), 'tags': tags}
        response = requests.post(Config.TAGS_SERVICE_URL + '/places/tags/add', data=json.dumps(data),
                                 headers=headers)
        return response
    return response_500_error()


@request_error_handler
def delete_place_helper(tag_id):
    headers = get_access_header(Config.PLACES_APP)
    if headers:
        response = requests.delete(Config.PLACES_SERVICE_URL + '/places/' + str(tag_id), headers=headers)
        return response
    return response_500_error()


@request_error_handler
def get_statistic_helper(login, action_type):
    '''Получить статистику'''
    headers = get_access_header(Config.STATISTIC_APP)
    if headers:
        response = requests.get(Config.STATISTIC_SERVICE_URL + '/statistic',
                                'login=' + str(login) + '&type=' + str(action_type), headers=headers)
        return response
    return response_500_error()


def send_statistic_helper(action, result, name=None):
    '''Отправить действие пользователя в статистику'''
    data = form_action_data(action, result, name)
    if data:
        try:
            requests.post(Config.STATISTIC_SERVICE_URL + '/statistic/add', data=json.dumps(data))
        except:
            pass


def send_statistic(action, result, name=None):
    '''Отправить задачу в очередь'''
    queue.enqueue('places_info.places_info_utils.send_statistic', action, result, name)


@request_error_handler
def get_accounts_helper():
    response = requests.get(Config.AUTH_SERVICE_URL + '/accounts')
    return response


@request_error_handler
def login_helper(login, password_hash):
    response = requests.get(Config.AUTH_SERVICE_URL + '/auth' + '?login=' +
                            login + '&password_hash=' + password_hash)
    return response


@request_error_handler
def register_helper(login, password_hash):
    data = {'login': str(login), 'password_hash': str(password_hash)}
    response = requests.post(Config.AUTH_SERVICE_URL + '/register', data=json.dumps(data))
    return response
