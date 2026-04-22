from flask import Blueprint, jsonify, render_template

main = Blueprint('main', __name__)


@main.route('/')
def home_page():
    return render_template('index.html')


@main.route('/about')
def about_page():
    return render_template('about_page.html')


@main.route('/signin')
def signin_page():
    return render_template('signinpage.html')


@main.route('/signup')
def signup_page():
    return render_template('signuppage.html')


