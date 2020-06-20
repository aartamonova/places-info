import json

from flask import Blueprint, render_template, request, url_for, flash
from flask_api.status import HTTP_200_OK
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import SelectField, SubmitField

from config import Config
from places_info.places_info_utils import admin_required, get_statistic_helper, get_accounts_helper

bp = Blueprint('statistic', __name__)


class SelectUserForm(FlaskForm):
    login = SelectField('Пользователь:', choices=[])
    submit = SubmitField(' Показать ')


@bp.route('/statistic', methods=['GET', 'POST'])
@admin_required
def statistic():
    select_user_form = SelectUserForm()

    if request.method == 'GET':
        response = get_accounts_helper()
        if response.status_code == HTTP_200_OK:
            accounts = json.loads(response.content)['accounts']
            logins = [a['login'] for a in accounts]
            select_user_form.login.choices = logins

            login = request.args.get('login', type=str, default=None)
            if login:
                select_user_form.login.data = login

            actions_tag = None
            response = get_statistic_helper(login, Config.ACTION_TYPE_TAG)
            if response.status_code == HTTP_200_OK:
                actions_tag = json.loads(response.content)['actions']

            actions_place = None
            response = get_statistic_helper(login, Config.ACTION_TYPE_PLACE)
            if response.status_code == HTTP_200_OK:
                actions_place = json.loads(response.content)['actions']

            actions_search = None
            response = get_statistic_helper(login, Config.ACTION_TYPE_SEARCH)
            if response.status_code == HTTP_200_OK:
                actions_search = json.loads(response.content)['actions']

            return render_template('statistic/statistic.html',
                                   form=select_user_form,
                                   login=login,
                                   actions_tag=actions_tag,
                                   actions_place=actions_place,
                                   actions_search=actions_search)
        else:
            try:
                flash(json.loads(response.data), 'danger')
            except:
                flash('Неизвестная ошибка', 'danger')
            return render_template('statistic/statistic.html', form=select_user_form)

    elif request.method == 'POST':
        login = request.form["login"]
        return redirect(url_for('statistic.statistic', login=login))
