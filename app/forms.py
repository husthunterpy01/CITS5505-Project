from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL

class CreateProductForm(FlaskForm):
  product_name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
  description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
  price = DecimalField('Price', places=2, validators=[DataRequired(), NumberRange(min=0)])
  category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
  location_id = SelectField('Location',coerce=int, validators=[DataRequired()])
  image_url = StringField('Image URL', validators=[Optional(), URL()])

  submit = SubmitField('Create Listing')