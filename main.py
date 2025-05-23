from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from routes import register_blueprints
from werkzeug.utils import secure_filename
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')


# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'  # Database configuration
app.config['SECRET_KEY'] = 'mysecretkey'  # Required for Flask-Admin sessions
app.config['BABEL_DEFAULT_LOCALE'] = 'en'  # Default language
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'  # Default timezone
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
db = SQLAlchemy(app)
register_blueprints(app)

# Initialize Babel for Flask
babel = Babel(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<User {self.username}"

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Checks the provided password against the stored hash."""
        return check_password_hash(self.password, password)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<Role {self.name}>'

class Enkhuils(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    dob = db.Column(db.String(120), nullable=True)
    hobby = db.Column(db.String(120), nullable=True)
    grade = db.Column(db.String(120), nullable=True)
    age = db.Column(db.String(120), nullable=True)


    def __repr__(self):
        return f'<Role {self.name}>'

# New Post Model
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    author_name = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Post {self.id} by {self.author_name}>"
    
# Protect Admin
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

# Initialize Flask-Admin
admin = Admin(app, name="My Admin Panel", template_mode="bootstrap3")
admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(Role, db.session))
admin.add_view(SecureModelView(Enkhuils, db.session))
admin.add_view(SecureModelView(Post, db.session))



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# Routes
@app.route('/')
def home():
    users = Enkhuils.query.first()
    if users:
        greating = f"Hi, I am testing my back-end. My name is {users.name}"
    else:
        greating = "Hi, I am testing my back-end."
    return render_template('index.html', message=greating)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('about.about'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already registered', 'danger')
            return redirect(url_for('register'))

        # Create a new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Show all posts
@app.route('/posts')
def show_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('posts.html', posts=posts)

# Create new post
@app.route('/posts/new', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        post_content = request.form['post']
        author_id = request.form['author_id']
        author_name = request.form['author_name']
        image = request.files['image']
        image_filename = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename
            
        new_post = Post(
            post=post_content,
              author_id=author_id, 
              author_name=author_name,
              image_path=image_filename
              )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('show_posts'))

    return render_template('new_post.html')
# Create database tables and run the app
if __name__ == '__main__':
    with app.app_context():
        Post.__table__.drop(db.engine)
        db.create_all()  # Ensure tables are created
    app.run(debug=True)
