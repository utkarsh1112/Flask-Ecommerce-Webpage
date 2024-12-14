from flask import Blueprint, render_template, flash, redirect
from .forms import LoginForm, SignUpForm, PasswordChangeForm
from .models import Customer
from . import db
from flask_login import login_user, login_required, logout_user

# Create a Blueprint for authentication-related routes
auth = Blueprint('auth', __name__)

# Route for sign-up functionality
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """
    Allows users to create a new account.
    Validates input, checks for matching passwords, and adds the user to the database.
    """
    form = SignUpForm()
    if form.validate_on_submit():  
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        if password1 == password2:  
            new_customer = Customer()
            new_customer.email = email
            new_customer.username = username
            new_customer.password = password2  

            try:
                db.session.add(new_customer)  
                db.session.commit()
                flash('Account Created Successfully, You can now Login')
                return redirect('/login')  # Redirect to login page
            except Exception as e:
                print(e)  # Log the exception for debugging
                flash('Account Not Created!!, Email already exists')

            # Clear form fields in case of an error
            form.email.data = ''
            form.username.data = ''
            form.password1.data = ''
            form.password2.data = ''

    return render_template('signup.html', form=form)  # Render the sign-up page with the form

# Route: Login functionality
@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Allows users to log into their accounts.
    Verifies the email and password, and logs in the user if valid.
    """
    form = LoginForm()
    if form.validate_on_submit():  # Check if the form inputs are valid
        email = form.email.data
        password = form.password.data

        # Query the database for a customer with the given email
        customer = Customer.query.filter_by(email=email).first()

        if customer:
            if customer.verify_password(password=password):  # Verify the entered password
                login_user(customer)  # Log in the user
                return redirect('/')  # Redirect to the home page
            else:
                flash('Incorrect Email or Password')  
        else:
            flash('Account does not exist please Sign Up') 

    return render_template('login.html', form=form)  # Render the login page with the form

# Route: Log out functionality
@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    """
    Logs out the currently logged-in user.
    """
    logout_user()  
    return redirect('/')  

# Route: Profile page
@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    """
    Displays the profile page of the specified customer.
    """
    customer = Customer.query.get(customer_id)  # Fetch the customer by ID
    return render_template('profile.html', customer=customer)  # Render the profile page

# Route to change password functionality
@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    """
    Allows the logged-in user to change their password.
    Verifies the current password and ensures the new passwords match.
    """
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)  # Fetch the customer by ID

    if form.validate_on_submit():  # Check if the form inputs are valid
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):  
            if new_password == confirm_new_password:  
                customer.password = confirm_new_password  # Update the password 
                db.session.commit()
                flash('Password Updated Successfully') 
                return redirect(f'/profile/{customer.id}')  # Redirect to profile page
            else:
                flash('New Passwords do not match!!')  
        else:
            flash('Current Password is Incorrect') 

    return render_template('change_password.html', form=form)  # Render the change password page
