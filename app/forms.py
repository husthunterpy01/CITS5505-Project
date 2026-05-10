from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from flask_wtf.file import FileAllowed, FileSize, MultipleFileField

class CreateProductForm(FlaskForm):
  product_name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
  description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
  price = DecimalField('Price', places=2, validators=[DataRequired(), NumberRange(min=0)])
  category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
  location_name = StringField('Suburb', validators=[DataRequired(), Length(max=200)])
  latitude = StringField('Latitude', validators=[DataRequired()])
  longitude = StringField('Longitude', validators=[DataRequired()])
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

