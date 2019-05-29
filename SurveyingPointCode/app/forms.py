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

# forms.py
# Module containing file forms
#
# Required Flask . BSD Licence. Copyright © 2010 by the Pallets team
# Required WTForms.  BSD Licence. Copyright © 2008 by the WTForms team


from app.models import User
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')


class UploadForm(FlaskForm):
    topographical_file = FileField('Topographical data file', validators=[
        FileRequired(), FileAllowed(['txt', 'csv'], 'File type must be: .txt or .csv.')])
    config_file = FileField('User configuration file', validators=[
        FileAllowed(['txt', 'csv'], 'File type must be: .txt or .csv.')])
    symbols_file = FileField('CAD symbols file', validators=[
        FileAllowed(['dxf'], 'File type must be: \'dxf\'.')])
    submit = SubmitField('Upload')
