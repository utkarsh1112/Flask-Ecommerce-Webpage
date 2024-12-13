from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model, UserMixin):
    """
    Represents a customer in the system.
    Attributes:
        - email: Unique email address of the customer.
        - username: Customer's username.
        - password_hash: Hashed version of the customer's password.
        - date_joined: Timestamp when the customer joined.
    Relationships:
        - cart_items: Items in the customer's cart.
        - orders: Orders placed by the customer.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(150))
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))

    @property
    def password(self):
        """
        Prevents access to the password attribute.
        """
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        """
        Hashes the password before storing it.
        """
        # Add password complexity checks here if needed
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        """
        Verifies the provided password against the stored hash.
        """
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        """
        Returns a string representation of the customer.
        """
        return f'<Customer {self.id}>'


class Product(db.Model):
    """
    Represents a product in the inventory.
    Attributes:
        - product_name: Name of the product.
        - current_price: Current selling price of the product.
        - previous_price: Previous price of the product for reference.
        - in_stock: Quantity available in stock.
        - product_picture: URL or path to the product's image.
        - flash_sale: Indicates if the product is part of a flash sale.
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
        """
        Returns a string representation of the product.
        """
        return f'<Product {self.product_name}>'


class Cart(db.Model):
    """
    Represents a customer's shopping cart.
    Attributes:
        - quantity: Quantity of the product in the cart.
        - customer_link: Foreign key to the customer.
        - product_link: Foreign key to the product.
    """
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        """
        Returns a string representation of the cart item.
        """
        return f'<Cart {self.id}>'


class Order(db.Model):
    """
    Represents an order placed by a customer.
    Attributes:
        - quantity: Quantity of the product ordered.
        - price: Total price of the order.
        - status: Status of the order (e.g., Pending, Delivered).
        - payment_id: Payment identifier for the transaction.
    """
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)
    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        """
        Returns a string representation of the order.
        """
        return f'<Order {self.id}>'
