from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flaskblog.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('This username is taken, please try for another')

	def validate_username(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('This email is taken, please try for another')


class LoginForm(FlaskForm):

	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember me')
	submit = SubmitField('Login')


class PostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	summary = TextAreaField('Summary', validators=[DataRequired()])
	submit = SubmitField('Post')


class UpdateForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

	email = StringField('Email', validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg', 'png'])])
	submit = SubmitField('update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('This username is taken, please try for another')


class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])

	submit = SubmitField('Request password reset')
	
	def validate_email(self, email):
		user = User.query.filter_by(email = email.data).first()
		if user is None:
			raise ValidationError('no account with that email, please enter correct email')




class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')


class SearchForm(FlaskForm):
	choices = [
		(1, 'by author'),
		(2, 'by post title'),
	]
	select = SelectField('Search post by: ', choices = choices)
	search = StringField('Enter title/author', validators = [DataRequired(), Length(min = 5, max = 30)])
	submit = SubmitField('Search')


class UpvoteForm(FlaskForm):
	submit = SubmitField('')
	

class BookmarkForm(FlaskForm):
	submit = SubmitField('')