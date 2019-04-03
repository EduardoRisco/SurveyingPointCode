# -*- coding: utf-8 -*-
#
# File forms
#
# J. Eduardo Risco 31-03-2019
#

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models import User


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
