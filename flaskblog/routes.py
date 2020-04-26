import os
import secrets
from flask import render_template,url_for, flash,  redirect, request, abort, session
from flaskblog.forms import CommentForm, MessageForm, LoginForm, RegistrationForm, PostForm, UpdateForm, RequestResetForm, ResetPasswordForm, SearchForm, UpvoteForm, BookmarkForm
from flaskblog.models import User, Post, Comment
from flaskblog.__innit__ import app, db, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message



@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
	blist = None
	posts = Post.query.order_by(Post.upvotes.desc()).all()
	form = SearchForm()
	form2 = UpvoteForm()
	form3 = BookmarkForm()
	if current_user.is_authenticated:
		blist = current_user.bookmarks 
	if form.validate_on_submit():
		x = form.select.data
		y = form.search.data
		return redirect(url_for('searchresult', ref = x, arg = y))
	return render_template('home.html', posts=posts, form = form, form2 = form2, form3 = form3, blist = blist)


@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		
		user = User(username = form.username.data, email=form.email.data, password = form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! you can now log in!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user and str(form.password.data) == str(user.password):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))

		else:
			flash('Login Unsuccessful', 'danger')
	return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))


def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	f_name, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	form_picture.save(picture_path)
	return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	form = UpdateForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Info has been updated', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('account.html', title='Account', form = form, image_file = image_file)



@app.route("/createpost", methods=['GET', 'POST'])
@login_required
def new():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(content = form.content.data, title = form.title.data, summary = form.summary.data, author = current_user)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post', form = form, legend = 'New Post')



@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post_display(post_id):
	test_id = post_id
	post = Post.query.get(int(post_id))
	coms = post.comments
	form = CommentForm()
	x = current_user.id
	if form.validate_on_submit():
		comment = Comment(text=form.text.data, user = x)
		db.session.add(comment)
		comment.posted_on.append(post)
		db.session.commit()
		flash('Comment added succesfully', 'success')
		return redirect(url_for('home'))
	return render_template('display_post.html', title='post.id', post = post, comments = coms, form = form)



@app.route("/myposts")
@login_required
def myposts():
	posts = Post.query.filter_by(author = current_user)
	return render_template('myposts.html', title='myposts', posts = posts)



@app.route("/myposts/<int:post_id>", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get(int(post_id))
	form = PostForm()


	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		post.summary = form.summary.data
		db.session.commit()
		flash('Your post has been updated successfully', 'success')
		return redirect(url_for('myposts'))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
		form.summary.data = post.summary
		

	return render_template('create_post.html', title='Update Post', form=form, legend = 'Update Post')



@app.route("/myposts/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted', 'success')
	return redirect(url_for('myposts'))


def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
	msg.body = f'''To reset your password, visit the following link: 
	{url_for('reset_token', token = token, _external=True)}
	If you did not make this request, please ignore this message.
	'''
	mail.send(msg)

@app.route("/resetpassword", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent to you with instructions to reset password', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/resetpassword/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	user = User.verify_reset_token(token)
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.password = form.password.data
		db.session.commit()
		flash('Your password has been updated', 'success')
		return redirect(url_for('login'))
	
	return render_template('reset_token.html', title='Reset Password', form=form)





@app.route("/upvote/<post_id>", methods=['POST','GET'])
@login_required
def upvote(post_id):
	post = Post.query.get(post_id)
	setattr(post, "upvotes", post.upvotes+1)
	db.session.commit()
	flash('post upvoted', 'success')
	return redirect(url_for('home'))


@app.route("/bookmark/<post_id>", methods=['POST', 'GET'])
@login_required
def bookmark(post_id):
	post = Post.query.get(post_id)
	post.users.append(current_user)
	db.session.commit()
	flash('Bookmark added! Visit "Bookmarks" to visit all your saved posts', 'success')
	return redirect(url_for('home'))


@app.route("/bookmarks/<int:user_id>")
@login_required
def bookmarks(user_id):
	if session.new:
		flash('login to observe better functionality', 'info')
	elif current_user.is_authenticated:
		posts = current_user.bookmarks
	return render_template('bookmarks.html', title='Bookmarks', posts=posts)
		

@app.route("/bookmarks/<int:post_id>", methods=['POST', 'GET'])
@login_required
def removebmark(post_id):
	post = Post.query.get(post_id)
	post.users.remove(current_user)
	db.session.commit()
	flash('bookmark removed successfully', 'success')
	return redirect(url_for('home'))

@app.route("/user/<int:user_id>")
def displayuser(user_id):
	user = User.query.get(user_id)
	return render_template('userinfo.html', title='user info', user = user)

@app.route("/message/<int:user_id>", methods=['GET', 'POST'])
@login_required
def message(user_id):
	form = MessageForm()
	receiver = User.query.get(user_id)
	x = current_user.id
	if form.validate_on_submit():
		message = Message(sender=x, received=user_id, text = form.text.data)
		db.session.add(message)
		db.session.commit()
		flash('message sent successfully', 'success')
		return redirect(url_for('home'))
	return render_template('message.html', title= 'Message', form = form, user = receiver)

	

@app.route("/searchresult/<int:ref>/arg")
def searchresult(ref, arg):
	if ref == 1:
		posts = Post.query.filter_by(author = arg)
	else :
		posts = Post.query.filter_by(title = arg)
	return render_template('searchresult.html', title = 'Results', posts = posts)