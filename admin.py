import os
from flask import Flask, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Secret key for CSRF protection
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Admin user model
class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

# Custom AdminIndexView to handle login
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return super(MyAdminIndexView, self).index()

# Initialize the admin
admin = Admin(app, name='ChatAI Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())

# Custom ModelView to check for authentication
class AuthModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

# Reflect the database
with app.app_context():
    db.Model.metadata.reflect(db.engine)

# Create model classes dynamically
for table_name in db.Model.metadata.tables.keys():
    if table_name != 'admin_user':  # Skip the AdminUser model
        class_name = ''.join(word.capitalize() for word in table_name.split('_'))
        globals()[class_name] = type(class_name, (db.Model,), {
            '__tablename__': table_name,
            '__table_args__': {'extend_existing': True}
        })
        admin.add_view(AuthModelView(globals()[class_name], db.session))

@app.route('/')
def index():
    return 'Welcome to the ChatAI Admin Panel. <a href="/admin/">Click here</a> to access the admin interface.'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid email or password')
    return '''
        <form method="POST">
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Log In">
        </form>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def update_admin_user_table():
    with app.app_context():
        # Alter the table to increase password column length
        with db.engine.connect() as connection:
            connection.execute(text('ALTER TABLE admin_user ALTER COLUMN password TYPE VARCHAR(255);'))
            connection.commit()
        
        # Update the existing user's password
        admin_user = AdminUser.query.filter_by(email=os.getenv('ADMIN_EMAIL')).first()
        if admin_user:
            admin_user.password = generate_password_hash(os.getenv('ADMIN_PASSWORD'), method='pbkdf2:sha256')
            db.session.commit()
            print("Admin user password updated successfully.")
        else:
            print("Admin user not found.")

def init_admin_user():
    with app.app_context():
        admin_user = AdminUser.query.filter_by(email=os.getenv('ADMIN_EMAIL')).first()
        if not admin_user:
            admin_user = AdminUser(
                email=os.getenv('ADMIN_EMAIL'),
                password=generate_password_hash(os.getenv('ADMIN_PASSWORD'), method='pbkdf2:sha256')
            )
            db.session.add(admin_user)
            db.session.commit()
            print("New admin user created.")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    update_admin_user_table()
    init_admin_user()
    app.run(debug=True, host="0.0.0.0", port=5120)