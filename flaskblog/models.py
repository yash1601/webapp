
from datetime import datetime 
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog.__innit__ import db, login_manager, app
from flask_login import UserMixin
from flask_script import Manager 
from flask_migrate import Migrate, MigrateCommand




migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

user_bookmarks = db.Table('user_bookmarks',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

post_comments = db.Table('post_comments',
	db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
	db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'))
)
	

class User(db.Model, UserMixin):
	
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(20), unique = True, nullable = False)
	email = db.Column(db.String(120), unique = True, nullable = False)
	image_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
	password = db.Column(db.String(60), nullable = False)
	posts = db.relationship('Post', backref = 'author', lazy = True)
	bookmarks = db.relationship('Post', secondary=user_bookmarks, backref=db.backref('users', lazy='dynamic'))
	comments = db.relationship('Comment', backref = 'commenter', lazy= True)
	messages = db.relationship('Message', backref = 'sender', lazy = 'dynamic', foreign_keys = 'Message.uidsender')
	receiver = db.relationship('Message', backref = 'received', lazy = 'dynamic', foreign_keys = 'Message.uidreceiver')


	def __repr__(self):
		return f"User('{self.username}', '{self.email}',  '{self.image_file}' )"

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)
		if user is None:
			flash('invalid token or token has been expired', 'warning')
			return redirect(url_for('reset_request'))


class Post(db.Model):
	
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(100), nullable = False)
	summary = db.Column(db.String(100), nullable = False)
	date_posted = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable = False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
	upvotes = db.Column(db.Integer, default=0)
	downvotes = db.Column(db.Integer, default=0)
	comments = db.relationship('Comment', secondary=post_comments, backref=db.backref('posted_on', lazy='dynamic'))

	
	def __repr__(self):
		return f"User('{self.title}', '{self.date_posted}' )"


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.Text)
	user = db.Column(db.Integer, db.ForeignKey('user.id'))

class Message(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	uidsender = db.Column(db.Integer, db.ForeignKey('user.id'))
	uidreceiver = db.Column(db.Integer, db.ForeignKey('user.id'))
	text = db.Column(db.Text)
	

db.create_all()

