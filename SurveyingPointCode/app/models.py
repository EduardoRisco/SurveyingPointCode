"""
 SurveyingPointCode
 Copyright © 2018-2019 J. Eduardo Risco

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.txt>.
"""

# models.py
# Module containing file models
#
# Required flask-login . MIT Licence. Copyright © 2011 Matthew Frazier
# Required SQLAlchemy.  MIT Licence. Copyright © 2005-2019 Michael Bayer and contributors.

from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_access = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Statistic(db.Model):
    __tablename__ = 'statistics'

    id = db.Column(db.DateTime, primary_key=True)
    username_id = db.Column(db.Integer, primary_key=True)
    file_converts = db.Column(db.Integer)
    file_downloads = db.Column(db.Integer)
    _table_args__ = (
        ForeignKeyConstraint(['username_id'], ['users.id']),
        UniqueConstraint(''),
    )


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@login_manager.request_loader
def load_user_from_request(request):
    auth_str = request.headers.get('Authorization')
    token = auth_str.split(' ')[1] if auth_str else ''
    if token:
        user_id = User.decode_token(token)
        user = User.query.get(int(user_id))
        if user:
            return user
    return None
