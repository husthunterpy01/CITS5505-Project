from functools import update_wrapper

from flask import flash, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User


class AuthService:
    @staticmethod
    def signin_user(email, password):
        """Validate credentials and return (user, error_message)."""
        normalized_email = email.strip().lower()

        if not normalized_email or not password:
            return None, 'Please fill in all the fields.'

        existing_user = User.query.filter_by(email=normalized_email).first()
        if not existing_user:
            return None, 'User does not exist'

        if not check_password_hash(existing_user.password, password):
            return None, 'Incorrect password'

        return existing_user, None

    @staticmethod
    def signup_user(first_name, last_name, email, password):
        """Create user account and return (user, error_message)."""
        cleaned_first_name = first_name.strip()
        cleaned_last_name = last_name.strip()
        normalized_email = email.strip().lower()

        if not cleaned_first_name or not cleaned_last_name or not normalized_email or not password:
            return None, 'Please fill in all the fields.'

        existing_user = User.query.filter_by(email=normalized_email).first()
        if existing_user:
            return None, 'An account with that email already exists.'

        hashed_password = generate_password_hash(password)
        new_user = User(
            first_name=cleaned_first_name,
            last_name=cleaned_last_name,
            email=normalized_email,
            password=hashed_password,
            role='normal',
            is_report=False,
        )

        db.session.add(new_user)
        db.session.commit()
        return new_user, None

    @staticmethod
    def login_user(user):
        """Persist current user identity in session."""
        session['user_id'] = user.user_id
        session['user_name'] = user.first_name
        session['user_role'] = user.role

    @staticmethod
    def logout_user():
        """Clear current user session."""
        session.clear()

    @staticmethod
    def role_accepted(*allowed_roles):
        """Require a signed-in user with one of the allowed roles."""

        return RoleAcceptedView(allowed_roles)

    @staticmethod
    def change_password(user_id, old_password, new_password, confirmed_password):
        user = User.query.get(user_id)
        if not user:
            return 'User not found.'
        if not old_password or not new_password or not confirmed_password:
            return 'Please fill in all password fields.'
        if new_password != confirmed_password:
            return 'New password and confirm password do not match.'
        if not check_password_hash(user.password, old_password):
            return 'Current password is incorrect.'
        
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return None
    
class RoleAcceptedView:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles
        self.view_function = None

    def __call__(self, *args, **kwargs):
        if self.view_function is None and len(args) == 1 and callable(args[0]) and not kwargs:
            self.view_function = args[0]
            update_wrapper(self, self.view_function)
            return self

        if 'user_id' not in session:
            flash('Please sign in to view your profile.', 'error')
            return redirect(url_for('main.signin_page'))

        if self.allowed_roles and session.get('user_role') not in self.allowed_roles:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.home_page'))

        return self.view_function(*args, **kwargs)
