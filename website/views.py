from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Order
from flask_login import login_required, current_user
from . import db
from intasend import APIService


views = Blueprint('views', __name__)

# Define constants for clarity
SHIPPING_FEE = 200
API_PUBLISHABLE_KEY = os.getenv('API_PUBLISHABLE_KEY', 'YOUR_PUBLISHABLE_KEY')
API_TOKEN = os.getenv('API_TOKEN', 'YOUR_API_TOKEN')



@views.route('/')
def home():

    items = Product.query.filter_by(flash_sale=True)

    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    """
    Adds a product to the user's cart or updates the quantity if it already exists.
    """
    try:
        item_to_add = Product.query.get(item_id)
        if not item_to_add:
            flash('Item not found')
            return redirect(request.referrer)

        # Check if the item already exists in the cart
        item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()

        if item_exists:
            item_exists.quantity += 1
            flash(f'Quantity of {item_exists.product.product_name} has been updated.')
        else:
            new_cart_item = Cart(
                quantity=1,
                product_link=item_to_add.id,
                customer_link=current_user.id
            )
            db.session.add(new_cart_item)
            flash(f'{item_to_add.product_name} added to cart.')

        db.session.commit()
    except Exception as e:
        print('Error adding item to cart:', e)
        flash('An error occurred while adding the item to the cart.')

    return redirect(request.referrer)



@views.route('/cart')
@login_required
def show_cart():
    """
    Displays the user's cart with calculated total and shipping cost.
    """
    try:
        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        # Calculate subtotal and total
        amount = sum(item.product.current_price * item.quantity for item in cart)
        total = amount + SHIPPING_FEE

        return render_template('cart.html', cart=cart, amount=amount, total=total)
    except Exception as e:
        print('Error retrieving cart:', e)
        flash('An error occurred while retrieving your cart.')
        return redirect('/')


@views.route('/minuscart')
@login_required
def minus_cart():
    """
    Decreases the quantity of a cart item by one. Ensures the quantity does not go below 1.
    """
    if request.method == 'GET':
        try:
            cart_id = request.args.get('cart_id')
            cart_item = Cart.query.get(cart_id)

            if not cart_item or cart_item.customer_link != current_user.id:
                return jsonify({'error': 'Invalid cart item.'}), 400

            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                db.session.commit()
            else:
                return jsonify({'error': 'Quantity cannot be less than 1.'}), 400

            # Recalculate totals
            cart = Cart.query.filter_by(customer_link=current_user.id).all()
            amount = sum(item.product.current_price * item.quantity for item in cart)

            return jsonify({
                'quantity': cart_item.quantity,
                'amount': amount,
                'total': amount + SHIPPING_FEE
            })
        except Exception as e:
            print('Error decreasing cart quantity:', e)
            return jsonify({'error': 'An error occurred.'}), 500



@views.route('removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('/place-order')
@login_required
def place_order():
    """
    Places an order for all items in the user's cart.
    Processes payment and updates stock quantities.
    """
    try:
        customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()

        if not customer_cart:
            flash('Your cart is empty.')
            return redirect('/cart')

        # Calculate the total cost
        total = sum(item.product.current_price * item.quantity for item in customer_cart) + SHIPPING_FEE

        # Process payment
        service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
        create_order_response = service.collect.mpesa_stk_push(
            phone_number='YOUR_NUMBER',
            email=current_user.email,
            amount=total,
            narrative='Purchase of goods'
        )

        # Validate payment response
        if create_order_response.get('status') != 'SUCCESS':
            flash('Payment failed. Please try again.')
            return redirect('/cart')

        # Place orders and update stock
        for item in customer_cart:
            new_order = Order(
                quantity=item.quantity,
                price=item.product.current_price,
                status=create_order_response['invoice']['state'].capitalize(),
                payment_id=create_order_response['id'],
                product_link=item.product_link,
                customer_link=item.customer_link
            )

            product = Product.query.get(item.product_link)
            if product.in_stock < item.quantity:
                raise ValueError(f"Insufficient stock for {product.product_name}.")

            product.in_stock -= item.quantity
            db.session.add(new_order)
            db.session.delete(item)

        db.session.commit()

        flash('Order placed successfully!')
        return redirect('/orders')

    except ValueError as ve:
        db.session.rollback()
        flash(str(ve))
        return redirect('/cart')
    except Exception as e:
        db.session.rollback()
        print('Error placing order:', e)
        flash('An error occurred while placing your order.')
        return redirect('/cart')



@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)


@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')














