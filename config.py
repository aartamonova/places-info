import os

root_dir = os.path.abspath(os.path.dirname(__file__))
static_dir = root_dir + '/places_info/static'


class Config:
    # Database settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(root_dir, 'places_info_data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Services settings
    PORT = '5000'
    AUTH_SERVICE_URL = 'https://places-info-auth.herokuapp.com'
    TAGS_SERVICE_URL = 'https://places-info-tags.herokuapp.com'
    PLACES_SERVICE_URL = 'https://places-info-places.herokuapp.com'
    STATISTIC_SERVICE_URL = 'https://places-info-statistic.herokuapp.com'

    # Statistic settings
    ACTION_TYPE_TAG = 'tag'
    ACTION_TYPE_PLACE = 'place'
    ACTION_TYPE_SEARCH = 'search'

    ACTION_SUCCESS = 'успешно'
    ACTION_ERROR = 'неуспешно'
    ACTION_NOT_FOUND = 'ничего не найдено'

    ACTION_ADD_TAG = 'добавление нового тега'
    ACTION_DELETE_TAG = 'удаление тега'
    ACTION_ADD_PLACE = 'добавление нового места'
    ACTION_EDIT_PLACE = 'редактирование места'
    ACTION_DELETE_PLACE = 'удаление места'
    ACTION_SEARCH_PLACE_NAME = 'поиск мест по запросу'
    ACTION_SEARCH_PLACE_TAG = 'поиск мест по тегу'

    ACTIONS = {ACTION_ADD_TAG: ACTION_TYPE_TAG,
               ACTION_DELETE_TAG: ACTION_TYPE_TAG,
               ACTION_ADD_PLACE: ACTION_TYPE_PLACE,
               ACTION_EDIT_PLACE: ACTION_TYPE_PLACE,
               ACTION_DELETE_PLACE: ACTION_TYPE_PLACE,
               ACTION_SEARCH_PLACE_NAME: ACTION_TYPE_SEARCH,
               ACTION_SEARCH_PLACE_TAG: ACTION_TYPE_SEARCH}

    # GUI settings
    GUI_IMAGES_PATH = os.path.join(static_dir, 'images/')

    # Other settings
    SOURCE_APP = 'gui'
    PLACES_APP = 'places'
    TAGS_APP = 'tags'
    STATISTIC_APP = 'statistic'
    REDISTOGO_URL = os.environ.get('REDISTOGO_URL') or 'redis://'
    SECRET_KEY = 'places-info-secret-key'
