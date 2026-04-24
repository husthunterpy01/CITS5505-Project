from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db

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

        if not email or not password:
            flash('Please fill in all the fields.', 'error')
            return render_template('signinpage.html')
        
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            flash('User does not exist', 'error')
            return render_template('signinpage.html')
        
        if not check_password_hash(existing_user.password, password):
            flash('Incorrect password', 'error')
            return render_template('signinpage.html')

        session['user_id'] = existing_user.user_id
        session['user_name'] = existing_user.first_name
        session['user_role'] = existing_user.role

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

        if not first_name or not last_name or not email or not password:
            flash('Please fill in all the fields.', 'error')
            return render_template('signuppage.html')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with that email already exists.', 'error')
            return render_template('signuppage.html')
        
        hashed_password = generate_password_hash(password)

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            role='normal',
            is_report=False
        )

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.user_id
        session['user_name'] = new_user.first_name
        session['user_role'] = new_user.role

        flash('Account created successfully.', 'success')
        return redirect(url_for('main.home_page'))
    
    return render_template('signuppage.html')

@main.route('/personalprofile')
def personal_profile_page():
    return render_template('personalprofile.html')

@main.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.home_page'))


