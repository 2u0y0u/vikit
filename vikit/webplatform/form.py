'''
    Author: Conan0xff
    Function: user login
    Created: 08/03/17
'''

#coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember me', default=False)

class ChangePassForm(FlaskForm):
    old_pass = StringField('old password', validators=[DataRequired()])
    new_pass = PasswordField('new password', validators=[DataRequired()])
    confirm_new_pass = PasswordField('confirm new password', validators=[DataRequired()])

class AddUserForm(FlaskForm):
    username = StringField('old password', validators=[DataRequired()])
    password = PasswordField('new password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm new password', validators=[DataRequired()])

class DelUserForm(FlaskForm):
    username = StringField('old password', validators=[DataRequired()])



