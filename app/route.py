from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from app.extensions import db
from app.models import User, Product
from app.service.auth import AuthService
from app.utils import user_roles

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


@main.route('/personalprofile', methods=['POST','GET'])
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
            # Handle update info
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            # Update info into database
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
            # Handle update password
            # Check old password
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

@main.route('/browse', methods=['POST', 'GET'])
def browse_page():
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    
    products = []

    for product in all_products:
        primary_image = None

        for image in product.images:
            if image.is_primary:
                primary_image = image.image_url
                break

        if not primary_image:
            primary_image = 'assets/logo/UWA_logo.webp'

        products.append({
            'product_id': product.product_id,
            'title': product.product_name,
            'description': product.description,
            'price': product.price,
            'location': product.location,
            'status': product.status,
            'seller_name': f'{product.seller.first_name} {product.seller.last_name}',
            'image': primary_image
        })
    
    return render_template('browse.html', products=products);
