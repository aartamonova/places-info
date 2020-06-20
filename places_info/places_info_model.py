from jwt import ExpiredSignatureError

from config import Config
from places_info import db
from flask_jwt_extended import decode_token


class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    source_app = db.Column(db.String(64), default=Config.SOURCE_APP)
    request_app = db.Column(db.String(64))
    access_token = db.Column(db.String(512))


class TokenData:
    @staticmethod
    def get_by_apps(source_app, request_app):
        try:
            db.session.commit()
            token = Token.query.filter_by(source_app=source_app, request_app=request_app).first()
        except:
            return None
        return token

    @staticmethod
    def check_token(token):
        try:
            decode_token(token.access_token)
        except ExpiredSignatureError:
            return False
        except:
            return True
        return True

    @staticmethod
    def save(source_app, request_app, access_token):
        old_token = TokenData.get_by_apps(source_app, request_app)
        if old_token:
            old_token.access_token = access_token
            db.session.commit()
            return old_token
        else:
            token = Token(source_app=source_app, request_app=request_app, access_token=access_token)
            if not token:
                return None
            db.session.add(token)
            db.session.commit()
            return token
