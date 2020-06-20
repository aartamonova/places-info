import json
import os

from flask import Blueprint, render_template, flash, url_for, request, session
from flask_api.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired

from config import Config
from places_info.places_info_utils import login_required, get_all_places_helper, get_place_helper, \
    add_place_helper, get_all_tags_helper, get_tags_place_helper, add_place_tags_helper, \
    delete_place_helper, edit_place_helper, edit_place_tags_helper, get_search_places_helper, \
    get_places_tag_helper, get_tag_helper, send_statistic_helper

bp = Blueprint('places', __name__)


class PlaceSearchForm(FlaskForm):
    name = StringField('Название места', validators=[DataRequired("Пожалуйста, введите название")])
    submit = SubmitField(' Найти ')


class PlaceAddForm(FlaskForm):
    name = StringField('Название места', validators=[DataRequired("Пожалуйста, введите название")])
    type = StringField('Тип места', validators=[DataRequired("Пожалуйста, введите тип")])
    description = TextAreaField('Описание', validators=[DataRequired("Пожалуйста, введите описание")])
    address = StringField('Адрес', validators=[DataRequired("Пожалуйста, введите адрес")])
    phone = StringField('Контактный телефон', validators=[DataRequired("Пожалуйста, введите телефон")])
    tags = SelectMultipleField('Теги', choices=[], )
    submit = SubmitField(' Добавить ')


class PlaceEditForm(FlaskForm):
    name = StringField('Название места', validators=[DataRequired("Пожалуйста, введите название")])
    type = StringField('Тип места', validators=[DataRequired("Пожалуйста, введите тип")])
    description = TextAreaField('Описание', validators=[DataRequired("Пожалуйста, введите описание")])
    address = StringField('Адрес', validators=[DataRequired("Пожалуйста, введите адрес")])
    phone = StringField('Контактный телефон', validators=[DataRequired("Пожалуйста, введите телефон")])
    tags = SelectMultipleField('Теги', choices=[], )
    submit = SubmitField(' Сохранить ')


class PlaceDeleteForm(FlaskForm):
    submit = SubmitField('  Удалить  ')


@bp.route('/places/all', methods=['GET'])
def places_all():
    page = request.args.get('page', type=int, default=1)
    response = get_all_places_helper(page)
    if response.status_code == HTTP_200_OK:
        places = json.loads(response.content)['places']

        prev_url = None
        next_url = None
        if places is not None:
            if page > 1:
                prev_response = get_all_places_helper(page - 1)
                if prev_response.status_code == HTTP_200_OK:
                    prev_url = url_for('places.places_all', page=page - 1)

            next_response = get_all_places_helper(page + 1)
            if next_response.status_code == HTTP_200_OK:
                next_url = url_for('places.places_all', page=page + 1)

        return render_template('places/places_all.html',
                               places=places,
                               prev_url=prev_url,
                               next_url=next_url)
    elif response.status_code == HTTP_404_NOT_FOUND:
        flash('База данных мест пуста', 'danger')
        return render_template('places/places_all.html')
    else:
        try:
            flash(json.loads(response.data), 'danger')
        except:
            flash('Неизвестная ошибка', 'danger')
        return render_template('places/places_all.html')


@bp.route('/places/search/<string:search_str>', methods=['GET'])
def places_search_result(search_str):
    page = request.args.get('page', type=int, default=1)
    response = get_search_places_helper(page, search_str)
    if response.status_code == HTTP_200_OK:
        places = json.loads(response.content)['places']
        prev_url = None
        next_url = None
        if places is not None:
            if page > 1:
                prev_response = get_search_places_helper(page - 1, search_str)
                if prev_response.status_code == HTTP_200_OK:
                    prev_url = url_for('places.places_search_result', search_str=search_str, page=page - 1)

            next_response = get_search_places_helper(page + 1, search_str)
            if next_response.status_code == HTTP_200_OK:
                next_url = url_for('places.places_search_result', search_str=search_str, page=page + 1)

        return render_template('places/places_search_result.html',
                               search_str=search_str,
                               places=places,
                               prev_url=prev_url,
                               next_url=next_url)
    elif response.status_code == HTTP_404_NOT_FOUND:
        flash('Ничего не найдено', 'danger')
        return render_template('places/places_search_result.html')
    else:
        try:
            flash(json.loads(response.data), 'danger')
        except:
            flash('Неизвестная ошибка', 'danger')
        return render_template('places/places_search_result.html')


@bp.route('/places/search/tag/<int:tag_id>', methods=['GET'])
def places_search_tag_result(tag_id):
    response = get_tag_helper(tag_id)
    if response.status_code == HTTP_200_OK:
        tag = json.loads(response.content)
    else:
        tag = None

    response = get_places_tag_helper(tag_id)
    if response.status_code == HTTP_200_OK:
        place_list = json.loads(response.content)['places']
        places = []
        for place_id in place_list:
            response = get_place_helper(place_id['id'])
            if response.status_code == HTTP_200_OK:
                place = json.loads(response.content)
                places.append(place)

        if len(places) > 0 and tag:
            send_statistic_helper(Config.ACTION_SEARCH_PLACE_TAG, Config.ACTION_SUCCESS, tag['name'])
            return render_template('places/places_search_tag_result.html',
                                   tag=tag,
                                   places=places)

        flash('Ничего не найдено', 'danger')
        send_statistic_helper(Config.ACTION_SEARCH_PLACE_TAG, Config.ACTION_NOT_FOUND, tag['name'])
        return render_template('places/places_search_tag_result.html', tag=tag, places=None)
    elif response.status_code == HTTP_404_NOT_FOUND:
        flash('Ничего не найдено', 'danger')
        send_statistic_helper(Config.ACTION_SEARCH_PLACE_TAG, Config.ACTION_NOT_FOUND, tag['name'])
        return render_template('places/places_search_tag_result.html', tag=tag, places=None)
    else:
        send_statistic_helper(Config.ACTION_SEARCH_PLACE_TAG, Config.ACTION_ERROR)
        try:
            flash(json.loads(response.data), 'danger')
        except:
            flash('Неизвестная ошибка', 'danger')
        return render_template('places/places_search_tag_result.html', tag=None, places=None)


@bp.route('/places/search', methods=['GET', 'POST'])
def places_search():
    place_search_form = PlaceSearchForm()
    if request.method == 'GET':
        return render_template('places/places_search.html', form=place_search_form)
    elif request.method == 'POST':
        name = request.form["name"]
        response = get_search_places_helper(1, name)
        if response.status_code == HTTP_200_OK:
            send_statistic_helper(Config.ACTION_SEARCH_PLACE_NAME, Config.ACTION_SUCCESS, name)
            return redirect(url_for('places.places_search_result', search_str=name))
        if response.status_code == HTTP_404_NOT_FOUND:
            flash('По данному запросу ничего не найдено', 'danger')
            send_statistic_helper(Config.ACTION_SEARCH_PLACE_NAME, Config.ACTION_NOT_FOUND, name)
            return redirect(url_for('places.places_search'))
        else:
            send_statistic_helper(Config.ACTION_SEARCH_PLACE_NAME, Config.ACTION_ERROR, name)
            try:
                flash(json.loads(response.data), 'danger')
            except:
                flash('Неизвестная ошибка', 'danger')
            return redirect(url_for('places.places_search'))


@bp.route('/places/add', methods=['GET', 'POST'])
@login_required
def place_add():
    place_add_form = PlaceAddForm()
    response = get_all_tags_helper()
    if response.status_code == HTTP_200_OK:
        tags = json.loads(response.content)['tags']
        choices = []
        for tag in tags:
            choices.append((tag['id'], tag['name']))
        place_add_form.tags.choices = choices
    else:
        del place_add_form.tags

    if request.method == 'GET':
        return render_template('places/place_add.html', form=place_add_form)

    elif request.method == 'POST':
        name = request.form["name"]
        place_type = request.form["type"]
        description = request.form["description"]
        phone = request.form["phone"]
        address = request.form["address"]

        try:
            selected_tags = place_add_form.tags.data
        except:
            selected_tags = None

        response = add_place_helper(name, place_type, description,
                                    phone, address, session['login'])

        if response.status_code == HTTP_200_OK:
            place = json.loads(response.content)
            send_statistic_helper(Config.ACTION_ADD_PLACE, Config.ACTION_SUCCESS, name)
            flash('Новое место успешно добавлено', 'info')

            response = add_place_tags_helper(place['id'], selected_tags)
            if response.status_code != HTTP_200_OK:
                flash('Ошибка добавления тегов', 'warning')

            return redirect(url_for('places.place_info', place_id=place['id']))
        elif response.status_code == HTTP_404_NOT_FOUND:
            send_statistic_helper(Config.ACTION_ADD_PLACE, Config.ACTION_ERROR, name)
            flash('Место с таким названием уже существует', 'info')
            return redirect(url_for('places.place_add'))
        else:
            send_statistic_helper(Config.ACTION_ADD_PLACE, Config.ACTION_ERROR, name)
            try:
                flash(json.loads(response.data), 'danger')
            except:
                flash('Неизвестная ошибка', 'danger')
            return redirect(url_for('places.place_add'))


@bp.route('/places/<int:place_id>/edit', methods=['GET', 'POST'])
@login_required
def place_edit(place_id):
    place_edit_form = PlaceEditForm()

    # Не выводить теги, если сервис тегов недоступен
    response = get_all_tags_helper()
    if response.status_code == HTTP_200_OK:
        tags = json.loads(response.content)['tags']
        choices = []
        for tag in tags:
            choices.append((tag['id'], tag['name']))
        place_edit_form.tags.choices = choices
    else:
        del place_edit_form.tags

    response = get_place_helper(place_id)
    if request.method == 'GET':
        if response.status_code == HTTP_200_OK:
            place = json.loads(response.content)
            place_edit_form.name.data = place['name']
            place_edit_form.type.data = place['type']
            place_edit_form.description.data = place['description']
            place_edit_form.address.data = place['address']
            place_edit_form.phone.data = place['phone']

            response = get_tags_place_helper(place['id'])
            if response.status_code == HTTP_200_OK:
                tags = json.loads(response.content)['tags']
                selected_tags = [str(x['id']) for x in tags]
            else:
                selected_tags = None

            try:
                place_edit_form.tags.data = selected_tags
            except:
                pass

            return render_template('places/place_edit.html', form=place_edit_form)

    elif request.method == 'POST':
        name = request.form["name"]
        place_type = request.form["type"]
        description = request.form["description"]
        phone = request.form["phone"]
        address = request.form["address"]
        response = edit_place_helper(place_id, name, place_type, description, phone, address)
        if response.status_code == HTTP_200_OK:
            try:
                selected_tags = place_edit_form.tags.data
            except:
                selected_tags = None

            response = edit_place_tags_helper(place_id, selected_tags)
            if response.status_code != HTTP_200_OK and response.status_code != HTTP_404_NOT_FOUND:
                print(response.status_code)
                flash('Ошибка изменения тегов', 'warning')

            send_statistic_helper(Config.ACTION_EDIT_PLACE, Config.ACTION_SUCCESS, name)
            return redirect(url_for('places.place_info', place_id=place_id))
        elif response.status_code == HTTP_400_BAD_REQUEST:
            flash('Место с таким названием уже существует', 'danger')
            send_statistic_helper(Config.ACTION_EDIT_PLACE, Config.ACTION_ERROR, name)
            return redirect(url_for('places.place_info', place_id=place_id))
        else:
            send_statistic_helper(Config.ACTION_EDIT_PLACE, Config.ACTION_ERROR, name)
            try:
                flash(json.loads(response.data), 'danger')
            except:
                flash('Неизвестная ошибка', 'danger')
            return redirect(url_for('places.place_add'))


@bp.route('/places/<int:place_id>', methods=['GET', 'POST'])
def place_info(place_id):
    response = get_place_helper(place_id)
    if request.method == 'GET':
        if response.status_code == HTTP_200_OK:
            place = json.loads(response.content)

            place_delete_form = None
            try:
                is_admin = session['admin']
            except:
                pass
            else:
                if is_admin:
                    place_delete_form = PlaceDeleteForm()

            response = get_tags_place_helper(place_id)
            if response.status_code == HTTP_200_OK:
                tags = json.loads(response.content)['tags']
            else:
                tags = None

            if os.path.isfile(Config.GUI_IMAGES_PATH + 'place_' + str(place_id) + '.jpg'):
                image_path = 'images/place_' + str(place_id) + '.jpg'
            else:
                image_path = 'images/no_image.jpg'

            return render_template('places/place_info.html',
                                   place=place,
                                   tags=tags,
                                   form=place_delete_form,
                                   image_path=image_path)
        elif response.status_code == HTTP_404_NOT_FOUND:
            flash('Место не найдено', 'danger')
            return render_template('places/place_info.html', place=None)
        else:
            try:
                flash(json.loads(response.data), 'danger')
            except:
                flash('Неизвестная ошибка', 'danger')
            return render_template('places/place_info.html', place=None)

    elif request.method == 'POST':
        if response.status_code == HTTP_200_OK:
            place = json.loads(response.content)

            try:
                is_admin = session['admin']
            except:
                is_admin = None

            if not is_admin:
                flash('У вас нет прав администратора', 'danger')
                return redirect(url_for('places.place_info', place_id=place_id))

            response = delete_place_helper(place['id'])
            if response.status_code == HTTP_200_OK:
                send_statistic_helper(Config.ACTION_DELETE_PLACE, Config.ACTION_SUCCESS, place['name'])
                flash('Место успешно удалено', 'info')
                return redirect(url_for('places.places_all'))
            else:
                send_statistic_helper(Config.ACTION_DELETE_PLACE, Config.ACTION_ERROR, place['name'])
                flash('Не удалось удалить место', 'danger')
                return redirect(url_for('places.place_info', place_id=place_id))
        else:
            return redirect(url_for('places.place_info', place_id=place_id))
