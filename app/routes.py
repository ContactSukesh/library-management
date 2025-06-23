from flask import session, url_for, Blueprint, render_template, request, redirect
from app.db import get_db_connection
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template("dashboard.html")

@main.route('/books')
def books():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    db.close()
    return render_template("books.html", books=books)

@main.route('/books/add', methods=["POST"])
def add_book():
    title = request.form["title"]
    author = request.form["author"]
    genre = request.form["genre"]
    copies = int(request.form["copies"])

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO books (title, author, genre, total_copies, available_copies) VALUES (%s, %s, %s, %s, %s)",
        (title, author, genre, copies, copies)
    )
    db.commit()
    db.close()
    return redirect("/books")

@main.route('/members')
def members():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    db.close()
    return render_template("members.html", members=members)

@main.route('/members/add', methods=["POST"])
def add_member():
    name = request.form["name"]
    email = request.form["email"]

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO members (name, email) VALUES (%s, %s)",
        (name, email)
    )
    db.commit()
    db.close()
    return redirect("/members")

@main.route('/search', methods=['POST'])
def search_book():
    query = request.form['query']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE %s OR author LIKE %s
    """, (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    db.close()
    return render_template("dashboard.html", results=results)

@main.route('/transactions')
def transactions():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.id, m.name AS member, b.title AS book, t.checkout_date, t.due_date, t.return_date, t.status
        FROM transactions t
        JOIN members m ON t.member_id = m.id
        JOIN books b ON t.book_id = b.id
    """)
    txns = cursor.fetchall()
    db.close()
    return render_template("transactions.html", transactions=txns)

@main.route('/transactions/borrow', methods=["POST"])
def borrow_book():
    member_id = request.form["member_id"]
    book_id = request.form["book_id"]
    checkout_date = datetime.now().date()
    due_date = checkout_date + timedelta(days=14)

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT available_copies FROM books WHERE id = %s", (book_id,))
    available = cursor.fetchone()[0]
    if available < 1:
        db.close()
        return "Book not available", 400

    cursor.execute("""
        INSERT INTO transactions (member_id, book_id, checkout_date, due_date)
        VALUES (%s, %s, %s, %s)
    """, (member_id, book_id, checkout_date, due_date))
    cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = %s", (book_id,))
    db.commit()
    db.close()
    return redirect("/transactions")

@main.route('/transactions/return/<int:id>')
def return_book(id):
    return_date = datetime.now().date()

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT book_id FROM transactions WHERE id = %s", (id,))
    book_id = cursor.fetchone()[0]

    cursor.execute("UPDATE transactions SET return_date = %s, status = 'returned' WHERE id = %s", (return_date, id))
    cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE id = %s", (book_id,))
    db.commit()
    db.close()
    return redirect("/transactions")

@main.route('/reports')
def reports():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM transactions WHERE status='borrowed'")
    borrowed = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM members WHERE membership_status='active'")
    members = cursor.fetchone()[0]

    db.close()
    return render_template("reports.html", total_books=total_books, borrowed=borrowed, members=members)
