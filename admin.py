from flask import render_template, redirect, url_for, request, flash
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required, login_user

class SecureAdminIndexView(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        if not current_user.is_admin:
            return redirect(url_for('index'))
        return super(SecureAdminIndexView, self).index()

class UserModelView(ModelView):
    column_list = ('id', 'email', 'is_admin')
    column_searchable_list = ['email']
    column_filters = ['is_admin']
    form_columns = ('email', 'is_admin')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

def init_admin(app, db, User):
    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3', index_view=SecureAdminIndexView())
    admin.add_view(UserModelView(User, db.session))

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password) and user.is_admin:
                login_user(user)
                return redirect(url_for('admin.index'))
            else:
                flash('Invalid email or password')
        return render_template('admin_login.html')

    return admin