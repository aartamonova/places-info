from flask import Blueprint, render_template
from flask_api.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

bp = Blueprint('errors', __name__)


@bp.app_errorhandler(HTTP_404_NOT_FOUND)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
def internal_error(error):
    return render_template('errors/500.html'), 500
