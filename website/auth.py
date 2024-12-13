from flask import Blueprint, render_template, flash, redirect, url_for
from .forms import LoginForm, SignUpForm, PasswordChangeForm
from .models import Customer
from . import db
from flask_login import login_user, login_required, logout_user

# Define a Blueprint for authentication-related routes
auth = Blueprint('auth', __name__)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """
    Handles user sign-up.
    Validates the form data and creates a new user if successful.
    """
    form = SignUpForm()
    
    # Process the form submission
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        # Check if passwords match
        if password1 == password2:
            # Create a new Customer object
            new_customer = Customer(email=email, username=username, password=password2)

            try:
                # Save the new customer to the database
                db.session.add(new_customer)
                db.session.commit()
                flash('Account created successfully! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                # Handle database errors, such as duplicate emails
                flash('Account creation failed. The email might already exist.', 'danger')
                print(f"Error creating account: {e}")
        else:
            flash('Passwords do not match. Please try again.', 'danger')

    return render_template('signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    Validates user credentials and logs in the user if successful.
    """
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Query the database for the customer
        customer = Customer.query.filter_by(email=email).first()

        if customer:
            # Verify the provided password
            if customer.verify_password(password=password):
                login_user(customer)
                flash('Login successful!', 'success')
                return redirect(url_for('main.index'))  # Redirect to the main index page
            else:
                flash('Incorrect email or password.', 'danger')
        else:
            flash('Account does not exist. Please sign up.', 'warning')

    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def log_out():
    """
    Logs out the currently logged-in user.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    """
    Displays the profile of a specific customer.
    """
    # Use get_or_404 to handle invalid customer IDs gracefully
    customer = Customer.query.get_or_404(customer_id)
    return render_template('profile.html', customer=customer)

@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    """
    Allows users to change their password.
    Validates the current password and ensures the new passwords match.
    """
    form = PasswordChangeForm()

    # Retrieve the current customer from the database
    customer = Customer.query.get_or_404(customer_id)

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        # Check if the current password is correct
        if customer.verify_password(current_password):
            # Ensure the new password and confirmation match
            if new_password == confirm_new_password:
                customer.password = new_password  # Assuming the model handles password hashing
                db.session.commit()
                flash('Password updated successfully!', 'success')
                return redirect(url_for('auth.profile', customer_id=customer.id))
            else:
                flash('New passwords do not match.', 'danger')
        else:
            flash('Current password is incorrect.', 'danger')

    return render_template('change_password.html', form=form)
