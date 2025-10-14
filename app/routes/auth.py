"""Authentication routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.services import AuthService
from app.forms import LoginForm, ChangePasswordForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        admin = AuthService.authenticate(form.username.data, form.password.data)

        if admin:
            login_user(admin)

            # Redirect to next page or games
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.games')

            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')

    return render_template('admin/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password."""
    form = ChangePasswordForm()

    if form.validate_on_submit():
        success = AuthService.change_password(
            current_user,
            form.currentPassword.data,
            form.newPassword.data
        )

        if success:
            flash('Your password has been updated.', 'success')
            return redirect(url_for('main.games'))
        else:
            flash('Current password is incorrect.', 'error')

    return render_template('admin/change_password.html', form=form)