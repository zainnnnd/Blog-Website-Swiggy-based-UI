import os  # Importing the os module for generating a random secret key
from flask import Flask, render_template, request, redirect, url_for, flash, session  # Importing necessary Flask modules
import mysql.connector  # Importing mysql.connector to interact with the MySQL database
from werkzeug.security import generate_password_hash, check_password_hash  # Importing Werkzeug security functions

app = Flask(__name__)  # Initializing the Flask application
app.secret_key = os.urandom(24)  # Securely generating a random secret key for session management

# Function to establish a connection to the MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',  # Database host
        user='omar',  # Database user
        password='omar',  # Database user's password
        database='BlogTodo'  # Database name
    )

@app.route("/")
@app.route("/home")  # Setting up route for the home page
def home():
    return render_template('home.html')  # Rendering the home.html template

@app.route("/about")  # Setting up route for the about page
def about():
    return render_template('about.html')  # Rendering the about.html template

@app.route("/register", methods=['GET', 'POST'])  # Setting up route for the registration page
def register():
    if request.method == 'POST':  # If the form is submitted via POST method
        first_name = request.form['first_name']  # Getting the first name from the form
        last_name = request.form['last_name']  # Getting the last name from the form
        email = request.form['email']  # Getting the email from the form
        password = request.form['password']  # Getting the password from the form
        confirm_password = request.form['confirm_password']  # Getting the confirmed password from the form
        contact_number = request.form['contact_number']  # Getting the contact number from the form

        if password != confirm_password:  # Checking if passwords match
            flash('Passwords do not match!', 'danger')  # Flashing an error message
            return redirect(url_for('register'))  # Redirecting back to the registration page

        conn = get_db_connection()  # Establishing a database connection
        cursor = conn.cursor()  # Creating a cursor object

        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))  # Checking if the email already exists
        if cursor.fetchone():  # If the email exists
            flash('Email address already exists!', 'danger')  # Flashing an error message
            cursor.close()  # Closing the cursor
            conn.close()  # Closing the connection
            return redirect(url_for('register'))  # Redirecting back to the registration page

        hashed_password = generate_password_hash(password)  # Hashing the password
        cursor.execute('INSERT INTO users (first_name, last_name, email, password, contact_number) VALUES (%s, %s, %s, %s, %s)',
                       (first_name, last_name, email, hashed_password, contact_number))  # Inserting the new user into the database
        conn.commit()  # Committing the transaction

        cursor.close()  # Closing the cursor
        conn.close()  # Closing the connection

        flash('You have successfully registered!', 'success')  # Flashing a success message
        return redirect(url_for('login'))  # Redirecting to the login page

    return render_template('register.html')  # Rendering the register.html template

@app.route('/login', methods=['GET', 'POST'])  # Setting up route for the login page
def login():
    if request.method == 'POST':  # If the form is submitted via POST method
        email = request.form['email']  # Getting the email from the form
        password = request.form['password']  # Getting the password from the form

        conn = get_db_connection()  # Establishing a database connection
        cursor = conn.cursor(dictionary=True)  # Creating a cursor object that returns results as dictionaries
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))  # Checking if the email exists
        user = cursor.fetchone()  # Fetching the user

        cursor.close()  # Closing the cursor
        conn.close()  # Closing the connection

        if user and check_password_hash(user['password'], password):  # If the user exists and the password matches
            session['user_id'] = user['id']  # Storing the user's id in the session
            session['user_first_name'] = user['first_name']  # Storing the user's first name in the session
            flash('Login successful!', 'success')  # Flashing a success message
            return redirect(url_for('account'))  # Redirecting to the account page
        else:
            flash('Invalid email or password!', 'danger')  # Flashing an error message
            return redirect(url_for('login'))  # Redirecting back to the login page

    return render_template('login.html')  # Rendering the login.html template

@app.route('/logout')  # Setting up route for the logout
def logout():
    session.clear()  # Clearing the session
    flash('You have successfully logged out!', 'success')  # Flashing a success message
    return redirect(url_for('login'))  # Redirecting to the login page

@app.route('/account')  # Setting up route for the account page
def account():
    user_id = session.get('user_id')  # Getting the user_id from the session
    if not user_id:  # If no user is logged in
        flash('Please log in to access your account.', 'danger')  # Flashing an error message
        return redirect(url_for('login'))  # Redirecting to the login page

    conn = get_db_connection()  # Establishing a database connection
    cursor = conn.cursor(dictionary=True)  # Creating a cursor object that returns results as dictionaries
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))  # Fetching the user's details
    user = cursor.fetchone()  # Fetching the user

    cursor.close()  # Closing the cursor
    conn.close()  # Closing the connection

    return render_template('account.html', user=user)  # Rendering the account.html template with the user's details

@app.route('/update', methods=['GET', 'POST'])  # Setting up route for updating user details
def update_details():
    user_id = session.get('user_id')  # Getting the user_id from the session
    if not user_id:  # If no user is logged in
        flash('Please log in to update your details.', 'danger')  # Flashing an error message
        return redirect(url_for('login'))  # Redirecting to the login page

    if request.method == 'POST':  # If the form is submitted via POST method
        first_name = request.form['first_name']  # Getting the first name from the form
        last_name = request.form['last_name']  # Getting the last name from the form
        email = request.form['email']  # Getting the email from the form
        password = request.form['password']  # Getting the password from the form
        confirm_password = request.form['confirm_password']  # Getting the confirmed password from the form
        contact_number = request.form['contact_number']  # Getting the contact number from the form

        if password != confirm_password:  # Checking if passwords match
            flash('Passwords do not match!', 'danger')  # Flashing an error message
            return redirect(url_for('update_details'))

        conn = get_db_connection()  # Establishing a database connection
        cursor = conn.cursor()  # Creating a cursor object

        hashed_password = generate_password_hash(password)  # Hashing the new password

        # Updating the user details in the database
        cursor.execute('UPDATE users SET first_name = %s, last_name = %s, email = %s, password = %s, contact_number = %s WHERE id = %s',
                       (first_name, last_name, email, hashed_password, contact_number, user_id))
        conn.commit()  # Committing the transaction

        cursor.close()  # Closing the cursor
        conn.close()  # Closing the connection

        flash('Your details have been updated!', 'success')  # Flashing a success message
        return redirect(url_for('account'))  # Redirecting to the account page

    conn = get_db_connection()  # Establishing a database connection
    cursor = conn.cursor(dictionary=True)  # Creating a cursor object that returns results as dictionaries
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()  # Fetching the user

    cursor.close()  # Closing the cursor
    conn.close()  # Closing the connection

    return render_template('update.html', user=user)  # Rendering the update.html template with the user's details

if __name__ == '__main__':
    app.run(debug=True)  # Running the Flask application in debug mode
