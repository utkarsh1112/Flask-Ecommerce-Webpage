from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Define the Customer model, representing a user in the application
class Customer(db.Model, UserMixin):
        """
    Model for a customer in the application. Includes login functionality and
    relationships to carts and orders.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(150))
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))    # Link to Cart model
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))       # Link to Order model

    @property
    #Prevent direct access to the password attribute.
    def password(self):
        raise AttributeError('Password is not a readable Attribute')

    @password.setter
    #Automatically hash the password when setting it.
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    #Verify the hashed password against the input password.
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    #String representation of the Customer object.
    def __str__(self):
        return '<Customer %r>' % Customer.id


class Product(db.Model):
    """
    Model for a product in the shop. Tracks product details, pricing, and availability.
    """
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Integer, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))

    def __str__(self):
        return '<Product %r>' % self.product_name


class Cart(db.Model):
    """
    Model for items in a customer's cart. Links customers to products with a quantity.
    """
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # customer product

    def __str__(self):
        return '<Cart %r>' % self.id


class Order(db.Model):
    """
    Model for customer orders. Tracks order details, status, and payment information.
    """
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # customer

    #Function for string representation of the Order object.
    def __str__(self):
        return '<Order %r>' % self.id

