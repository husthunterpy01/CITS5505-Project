from flask_wtf import FlaskForm
import re
from flask_wtf.file import MultipleFileField
from wtforms import (
    BooleanField,
    DecimalField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError


class CreateProductForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    price = DecimalField('Price', places=2, validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    location_name = StringField('Suburb', validators=[DataRequired(), Length(max=200)])
    latitude = StringField('Latitude', validators=[Optional()])
    longitude = StringField('Longitude', validators=[Optional()])
    images = MultipleFileField('Product Images')
    submit = SubmitField('Create Listing')

    def validate_images(self, field):
        uploaded_images = [file for file in (field.data or []) if file and file.filename]

        if len(uploaded_images) > 10:
            raise ValidationError('You can upload a maximum of 10 images per product.')

        allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
        max_size = 5 * 1024 * 1024

        for image in uploaded_images:
            extension = image.filename.rsplit('.', 1)[-1].lower() if '.' in image.filename else ''
            if extension not in allowed_extensions:
                raise ValidationError('Only JPG, PNG, and WEBP images are allowed.')

            image.seek(0, 2)
            size = image.tell()
            image.seek(0)

            if size > max_size:
                raise ValidationError('Each image must be 5MB or smaller.')


class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')


class SignUpForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    terms_accepted = BooleanField(
        'I agree to the Terms of Service and Privacy Policy',
        validators=[DataRequired(message='Please agree to the Terms of Service and Privacy Policy before signing up.')],
    )
    submit = SubmitField('Sign up')
    _student_email_pattern = re.compile(r'^\d{8}@student\.uwa\.edu\.au$')

    def validate_email(self, field):
        normalized = (field.data or '').strip().lower()
        if not self._student_email_pattern.fullmatch(normalized):
            raise ValidationError('Use UWA student email format: 8digits@student.uwa.edu.au.')

