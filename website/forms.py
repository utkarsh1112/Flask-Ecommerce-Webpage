from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, FloatField, PasswordField, 
    EmailField, BooleanField, SubmitField, SelectField
)
from wtforms.validators import DataRequired, length, NumberRange
from flask_wtf.file import FileField


class SignUpForm(FlaskForm):
    """
    Form for user registration.
    Fields:
        - Email: User's email address (required).
        - Username: Unique username for the user (minimum 2 characters).
        - Password1: Primary password (minimum 6 characters).
        - Password2: Confirmation of the primary password.
    """
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), length(min=2)])
    password1 = PasswordField('Enter Your Password', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Confirm Your Password', validators=[DataRequired(), length(min=6)])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    """
    Form for user login.
    Fields:
        - Email: User's email address (required).
        - Password: User's account password.
    """
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Enter Your Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class PasswordChangeForm(FlaskForm):
    """
    Form for changing a user's password.
    Fields:
        - Current Password: Verify the user's existing password.
        - New Password: Input for the new password.
        - Confirm New Password: Confirmation of the new password.
    """
    current_password = PasswordField('Current Password', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Change Password')


class ShopItemsForm(FlaskForm):
    """
    Form for adding or updating shop items.
    Fields:
        - Product Name: Name of the product (required).
        - Current Price: Current selling price of the product.
        - Previous Price: Previous price of the product for reference.
        - In Stock: Quantity of the product available.
        - Product Picture: Image file for the product (required).
        - Flash Sale: Boolean indicating if the product is on a flash sale.
    """
    product_name = StringField('Name of Product', validators=[DataRequired()])
    current_price = FloatField('Current Price', validators=[DataRequired()])
    previous_price = FloatField('Previous Price', validators=[DataRequired()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    product_picture = FileField('Product Picture', validators=[DataRequired()])
    flash_sale = BooleanField('Flash Sale')
    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')


class OrderForm(FlaskForm):
    """
    Form for updating the status of an order.
    Fields:
        - Order Status: Dropdown menu to select the current status of an order.
    """
    order_status = SelectField(
        'Order Status', 
        choices=[
            ('Pending', 'Pending'), 
            ('Accepted', 'Accepted'),
            ('Out for delivery', 'Out for delivery'),
            ('Delivered', 'Delivered'), 
            ('Canceled', 'Canceled')
        ]
    )
    update = SubmitField('Update Status')
