from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import get_db_connection

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        user = cursor.fetchone()
        db.close()

        if user and user['password_hash'] == password:
            session['admin_id'] = user['id']
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('auth.login'))
