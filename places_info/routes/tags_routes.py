import json

from flask import Blueprint, render_template, flash, url_for, request, session
from flask_api.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from config import Config
from places_info.places_info_utils import login_required, get_all_tags_helper, add_tag_helper, get_tag_helper, \
    delete_tag_helper, send_statistic_helper

bp = Blueprint('tags', __name__)


class TagAddForm(FlaskForm):
    name = StringField('Имя тега', validators=[DataRequired("Пожалуйста, введите имя тега")])
    submit = SubmitField(' Добавить ')


class TagDeleteForm(FlaskForm):
    submit = SubmitField('  Удалить  ')


@bp.route('/tags/all', methods=['GET'])
def tags_all():
    response = get_all_tags_helper()
    if response.status_code == HTTP_200_OK:
        tags = json.loads(response.content)['tags']
        return render_template('tags/tags_all.html', tags=tags)
    elif response.status_code == HTTP_404_NOT_FOUND:
        flash('База данных тегов пуста', 'danger')
        return render_template('tags/tags_all.html')
    else:
        try:
            flash(json.loads(response.data), 'danger')
        except:
            flash('Неизвестная ошибка', 'danger')
        return render_template('tags/tags_all.html')


@bp.route('/tags/search', methods=['GET'])
def tags_search():
    response = get_all_tags_helper()
    if response.status_code == HTTP_200_OK:
        tags = json.loads(response.content)['tags']
        return render_template('tags/tags_search.html', tags=tags)
    elif response.status_code == HTTP_404_NOT_FOUND:
        flash('База данных тегов пуста', 'danger')
        return render_template('tags/tags_search.html')
    else:
        try:
            flash(json.loads(response.data), 'danger')
        except:
            flash('Неизвестная ошибка', 'danger')
        return render_template('tags/tags_search.html')


@bp.route('/tags/add', methods=['GET', 'POST'])
@login_required
def tags_add():
    add_tag_form = TagAddForm()

    if request.method == 'GET':
        return render_template('tags/tags_add.html', form=add_tag_form)

    elif request.method == 'POST':
        name = request.form["name"]
        if len(name) > 20:
            flash('Длина имени тега не должна превышать 20 символов', 'warning')
            return redirect(url_for('tags.tags_add'))

        response = add_tag_helper(name, session['login'])

        if response.status_code == HTTP_200_OK:
            tag = json.loads(response.content)
            send_statistic_helper(Config.ACTION_ADD_TAG, Config.ACTION_SUCCESS, name)
            flash('Новый тег успешно добавлен', 'info')
            return redirect(url_for('tags.tag_info', tag_id=tag['id']))

        elif response.status_code == HTTP_404_NOT_FOUND:
            flash('Тег с таким именем уже существует', 'info')
            return redirect(url_for('tags.tags_add'))
        else:
            try:
                flash(json.loads(response.data), 'danger')
            except:
                flash('Неизвестная ошибка', 'danger')
            return redirect(url_for('tags.tags_add'))


@bp.route('/tags/<int:tag_id>', methods=['GET', 'POST'])
def tag_info(tag_id):
    response = get_tag_helper(tag_id)

    if request.method == 'GET':
        if response.status_code == HTTP_200_OK:
            tag = json.loads(response.content)
            tag_delete_form = None
            try:
                is_admin = session['admin']
            except:
                pass
            else:
                if is_admin:
                    tag_delete_form = TagDeleteForm()

            return render_template('tags/tag_info.html', tag=tag, form=tag_delete_form)

        elif response.status_code == HTTP_404_NOT_FOUND:
            flash('Тег не найден', 'danger')
            return render_template('tags/tag_info.html', tag=None)
        else:
            try:
                flash(json.loads(response.data), 'danger')
            except:
                flash('Неизвестная ошибка', 'danger')
            return render_template('tags/tag_info.html', tag=None)

    elif request.method == 'POST':
        if response.status_code == HTTP_200_OK:
            tag = json.loads(response.content)

            try:
                is_admin = session['admin']
            except:
                is_admin = None

            if not is_admin:
                flash('У вас нет прав администратора', 'danger')
                return redirect(url_for('tags.tag_info', tag_id=tag['id']))

            response = delete_tag_helper(tag['id'])
            if response.status_code == HTTP_200_OK:
                send_statistic_helper(Config.ACTION_DELETE_TAG, Config.ACTION_SUCCESS, tag['name'])
                flash('Тег успешно удален', 'info')
                return redirect(url_for('tags.tags_all'))
            else:
                send_statistic_helper(Config.ACTION_DELETE_TAG, Config.ACTION_ERROR, tag['name'])
                flash('Не удалось удалить тег', 'danger')
                return redirect(url_for('tags.tag_info', tag_id=tag['id']))
        else:
            return redirect(url_for('tags.tag_info', tag_id=tag_id))
