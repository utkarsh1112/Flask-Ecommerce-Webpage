import os
import logging
from flask import Blueprint, render_template, flash, send_from_directory, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .forms import ShopItemsForm, OrderForm
from .models import Product, Order, Customer
from . import db

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the Blueprint for admin routes
admin = Blueprint('admin', __name__)

# Utility: Create a decorator to restrict access to admin users only
def admin_required(f):
    """Decorator to ensure the user is an admin."""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:  # Check if the user is admin
            logging.warning("Unauthorized access attempt by user ID: %s", current_user.id)
            return render_template('404.html')  # Show 404 for unauthorized users
        return f(*args, **kwargs)

    return decorated_function

# Utility: Centralize file-saving logic
def save_file(file, folder='media'):
    """
    Saves the uploaded file securely to the specified folder.
    Creates the folder if it doesn't exist.
    """
    os.makedirs(folder, exist_ok=True)  # Ensure the folder exists
    file_name = secure_filename(file.filename)  # Sanitize the filename
    file_path = os.path.join(folder, file_name)
    file.save(file_path)  # Save the file
    return file_path

# Route: Serve images from the media folder
@admin.route('/media/<path:filename>')
def get_image(filename):
    """
    Serve media files from the media folder.
    """
    return send_from_directory('../media', filename)

# Route: Add shop items (only admin)
@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
@admin_required
def add_shop_items():
    """
    Add new items to the shop. Admin access required.
    """
    form = ShopItemsForm()

    if form.validate_on_submit():
        try:
            # Extract form data
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            # Save the product picture
            file_path = save_file(form.product_picture.data)

            # Create a new Product instance
            new_shop_item = Product(
                product_name=product_name,
                current_price=current_price,
                previous_price=previous_price,
                in_stock=in_stock,
                flash_sale=flash_sale,
                product_picture=file_path
            )

            # Add and commit to the database
            db.session.add(new_shop_item)
            db.session.commit()
            flash(f'{product_name} added successfully!', 'success')
            logging.info("Product %s added by admin.", product_name)

        except Exception as e:
            logging.error("Failed to add product: %s", e)
            flash('An error occurred while adding the product!', 'danger')

    return render_template('add_shop_items.html', form=form)

# Route: Display all shop items (only admin)
@admin.route('/shop-items', methods=['GET'])
@login_required
@admin_required
def shop_items():
    """
    View all shop items. Admin access required.
    """
    items = Product.query.order_by(Product.date_added).all()  # Query all items
    return render_template('shop_items.html', items=items)

# Route: Update an existing shop item (only admin)
@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_item(item_id):
    """
    Update details of an existing shop item. Admin access required.
    """
    form = ShopItemsForm()
    item_to_update = Product.query.get_or_404(item_id)  # Get the item or 404 if not found

    # Pre-fill placeholders with current data
    form.product_name.render_kw = {'placeholder': item_to_update.product_name}
    form.previous_price.render_kw = {'placeholder': item_to_update.previous_price}
    form.current_price.render_kw = {'placeholder': item_to_update.current_price}
    form.in_stock.render_kw = {'placeholder': item_to_update.in_stock}
    form.flash_sale.render_kw = {'placeholder': item_to_update.flash_sale}

    if form.validate_on_submit():
        try:
            # Update the item's attributes
            item_to_update.product_name = form.product_name.data
            item_to_update.current_price = form.current_price.data
            item_to_update.previous_price = form.previous_price.data
            item_to_update.in_stock = form.in_stock.data
            item_to_update.flash_sale = form.flash_sale.data

            # Save the new product picture
            if form.product_picture.data:
                item_to_update.product_picture = save_file(form.product_picture.data)

            db.session.commit()
            flash(f'{item_to_update.product_name} updated successfully!', 'success')
            logging.info("Product %s updated by admin.", item_to_update.product_name)
            return redirect(url_for('admin.shop_items'))

        except Exception as e:
            logging.error("Failed to update product: %s", e)
            flash('An error occurred while updating the item!', 'danger')

    return render_template('update_item.html', form=form)

# Route: Delete a shop item (only admin)
@admin.route('/delete-item/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_item(item_id):
    """
    Delete a shop item. Admin access required.
    """
    try:
        item_to_delete = Product.query.get_or_404(item_id)  # Get the item or 404
        db.session.delete(item_to_delete)
        db.session.commit()
        flash('Item deleted successfully!', 'success')
        logging.info("Product ID %s deleted by admin.", item_id)

    except Exception as e:
        logging.error("Failed to delete product: %s", e)
        flash('An error occurred while deleting the item!', 'danger')

    return redirect(url_for('admin.shop_items'))

# Route: View customer orders (only admin)
@admin.route('/view-orders', methods=['GET'])
@login_required
@admin_required
def order_view():
    """
    View all customer orders. Admin access required.
    """
    orders = Order.query.all()  # Query all orders
    return render_template('view_orders.html', orders=orders)

# Route: Update an order's status (only admin)
@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_order(order_id):
    """
    Update the status of an order. Admin access required.
    """
    form = OrderForm()
    order_to_update = Order.query.get_or_404(order_id)  # Get the order or 404 if not found

    if form.validate_on_submit():
        try:
            # Update order status
            order_to_update.status = form.order_status.data
            db.session.commit()
            flash(f'Order {order_id} updated successfully!', 'success')
            logging.info("Order ID %s updated by admin.", order_id)
            return redirect(url_for('admin.order_view'))

        except Exception as e:
            logging.error("Failed to update order: %s", e)
            flash('An error occurred while updating the order!', 'danger')

    return render_template('order_update.html', form=form)

# Route: Display all customers (only admin)
@admin.route('/customers', methods=['GET'])
@login_required
@admin_required
def display_customers():
    """
    Display all registered customers. Admin access required.
    """
    customers = Customer.query.all()  # Query all customers
    return render_template('customers.html', customers=customers)

# Route: Admin dashboard (only admin)
@admin.route('/admin-page', methods=['GET'])
@login_required
@admin_required
def admin_page():
    """
    Display the admin dashboard. Admin access required.
    """
    return render_template('admin.html')
