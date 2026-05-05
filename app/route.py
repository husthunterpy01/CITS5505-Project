from flask import Blueprint, render_template, flash, request, redirect, url_for, session, jsonify, current_app

from app.extensions import db
from app.models import User
from app.service.auth import AuthService
from app.utils import (
    user_roles,
    products_listing_query,
    serialize_product_for_listing,
    search_products_for_listing,
)

main = Blueprint('main', __name__)


@main.route('/')
def home_page():
    return render_template('index.html')


@main.route('/about')
def about_page():
    return render_template('about.html')


@main.route('/signin', methods=['POST', 'GET'])
def signin_page():
    if 'user_id' in session:
        flash('You are already signed in.', 'error')
        return redirect(url_for('main.home_page'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        existing_user, error = AuthService.signin_user(email, password)
        if error:
            flash(error, 'error')
            return render_template('signinpage.html')

        AuthService.login_user(existing_user)

        flash("Login Successful", 'success')
        return redirect(url_for('main.home_page'))

    return render_template('signinpage.html')


@main.route('/signup', methods=['POST', 'GET'])
def signup_page():
    if 'user_id' in session:
        flash('You are already signed in', 'error')
        return redirect(url_for('main.home_page'))

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        new_user, error = AuthService.signup_user(first_name, last_name, email, password)
        if error:
            flash(error, 'error')
            return render_template('signuppage.html')

        AuthService.login_user(new_user)

        flash('Account created successfully.', 'success')
        return redirect(url_for('main.home_page'))

    return render_template('signuppage.html')


@main.route('/logout')
def logout():
    AuthService.logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.home_page'))


@main.route('/personalprofile', methods=['POST', 'GET'])
@AuthService.role_accepted(*user_roles.keys())
def personal_profile_page():
    current_user_id = session.get('user_id')
    user_profile = User.query.get(current_user_id)
    display_name = ''

    if user_profile:
        display_name = f'{user_profile.first_name} {user_profile.last_name}'.strip()

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'profile_update':
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip().lower()

            if first_name:
                user_profile.first_name = first_name
            if last_name:
                user_profile.last_name = last_name
            if email:
                user_profile.email = email
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('main.personal_profile_page'))

        elif form_type == 'password_update':
            old_pwd = request.form.get('current_password', '')
            new_pwd = request.form.get('new_password', '')
            confirm_pwd = request.form.get('confirm_password', '')
            error = AuthService.change_password(current_user_id, old_pwd, new_pwd, confirm_pwd)
            if error:
                flash(error, 'error')
            else:
                flash('Password updated successfully.', 'success')
                return redirect(url_for('main.personal_profile_page'))

    return render_template('personalprofile.html', user=user_profile, username=display_name)


@main.route('/profile')
def profile_page():
    return redirect(url_for('main.personal_profile_page'))


@main.route('/browse', methods=['POST', 'GET'])
def browse_page():
    default_image = current_app.config.get('LISTING_DEFAULT_IMAGE', 'assets/logo/UWA_logo.webp')
    all_products = products_listing_query().all()
    products = [serialize_product_for_listing(p, default_image) for p in all_products]
    return render_template('browse.html', products=products)


@main.route('/api/products/search', methods=['GET'])
def api_products_search():
    """Full-text style search on title and description; bounded for responsiveness."""
    raw_q = request.args.get('q', '') or ''
    q = raw_q.strip()

    default_image = current_app.config.get('LISTING_DEFAULT_IMAGE', 'assets/logo/UWA_logo.webp')
    search_limit = current_app.config.get('SEARCH_RESULT_LIMIT', 200)
    rows = search_products_for_listing(q, search_limit)
    items = [serialize_product_for_listing(p, default_image) for p in rows]
    payload = {
        'success': True,
        'query': q,
        'products': items,
    }
    if q and not items:
        payload['message'] = 'No products matched your search.'
    return jsonify(payload)
