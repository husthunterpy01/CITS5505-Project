import base64

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.models import User

main = Blueprint('main', __name__)


@main.route('/')
def home_page():
    return render_template('index.html')


@main.route('/about')
def about_page():
    return render_template('about_page.html')


@main.route('/signin', methods=['GET', 'POST'])
def signin_page():
    if request.method == 'POST':
        email = (request.form.get('email') or "").strip().lower()
        password = request.form.get('password') or ""

        user = User.query.filter_by(email=email).first()
        encoded_password = base64.b64encode(password.encode("utf-8")).decode("utf-8")

        if user and user.password == encoded_password:
            initials = f"{user.first_name[:1]}{user.last_name[:1]}".upper()
            session['user_id'] = user.user_id
            session['user_name'] = f"{user.first_name} {user.last_name}"
            session['user_initials'] = initials
            return redirect(url_for('main.home_page'))

    return render_template('signinpage.html')


@main.route('/signup')
def signup_page():
    return render_template('signuppage.html')


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home_page'))


@main.route('/profile')
def profile_page():
    if not session.get('user_id'):
        return redirect(url_for('main.signin_page'))
    return render_template('profilepage.html')


@main.route('/my-listings')
def my_listings_page():
    if not session.get('user_id'):
        return redirect(url_for('main.signin_page'))
    return render_template('mylistingspage.html')


