import hashlib
import json

from flask import g, Blueprint, render_template, request, url_for, flash, session
from flask_api.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from places_info.places_info_utils import login_helper, register_helper

bp = Blueprint('auth', __name__)


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired("Пожалуйста, введите логин")])
    password = PasswordField('Пароль', validators=[DataRequired("Пожалуйста, введите пароль")])
    submit = SubmitField('   Войти   ')


class RegisterForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired("Пожалуйста, введите логин")])
    password = PasswordField('Пароль', validators=[DataRequired("Пожалуйста, введите пароль")])
    password_repeat = PasswordField('Повторите пароль', validators=[DataRequired("Пожалуйста, введите пароль")])
    submit = SubmitField(' Зарегистрироваться ')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        session['login']
    except:
        pass
    else:
        if session['login']:
            flash('Вы уже авторизованы', 'info')
            return redirect(url_for('index.index'))

    login_form = LoginForm()

    if request.method == 'GET':
        return render_template('auth/login.html', form=login_form)

    elif request.method == 'POST':
        user_login = request.form["login"]
        password = request.form["password"]
        password_hash = hashlib.md5(password.encode()).hexdigest()

        response = login_helper(user_login, password_hash)

        if response.status_code == HTTP_200_OK:
            user = json.loads(response.content)
            g.is_authorized = True
            session['login'] = user_login
            session['admin'] = bool(user['admin'])

            flash('Успешный вход', 'info')
            return redirect(url_for('index.index'))
        elif response.status_code == HTTP_403_FORBIDDEN:
            flash('Неверный логин или пароль', 'danger')
            return redirect(url_for('auth.login'))
        else:
            try:
                flash(json.loads(response.data), 'danger')
            except:
                flash('Неизвестная ошибка', 'danger')
            return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        session['login']
    except:
        pass
    else:
        if session['login']:
            flash('Вы уже авторизованы', 'info')
            return redirect(url_for('index.index'))

    register_form = RegisterForm()

    if request.method == 'GET':
        return render_template('auth/register.html', form=register_form)

    elif request.method == 'POST':
        user_login = request.form["login"]
        password = request.form["password"]
        password_repeat = request.form["password_repeat"]

        if password != password_repeat:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('auth.register'))

        password_hash = hashlib.md5(password.encode()).hexdigest()
        response = register_helper(user_login, password_hash)
        if response.status_code == HTTP_200_OK:
            flash('Регистрация прошла успешно', 'info')
            return redirect(url_for('auth.login'))
        elif response.status_code == HTTP_404_NOT_FOUND:
            flash('Пользователь с таким логином уже существует', 'danger')
            return redirect(url_for('auth.register'))
        else:
            try:
                flash(json.loads(response.data), 'danger')
            except:
                flash('Неизвестная ошибка', 'danger')
            return redirect(url_for('auth.register'))


@bp.route('/logout', methods=['GET'])
def logout():
    g.is_authorized = False
    session['login'] = None
    session['admin'] = None
    return redirect(url_for('index.index'))
