from flask import Flask,render_template,request,session,redirect,url_for,flash
from library import Library
from book import Book
from user import User
import json.......



app = Flask(__name__)
app.secret_key="your_secret_key"      #it is a sceret key

def load_users(library):
    users = {}
    try:
        with open("users_data.json", "r") as f:
            data = json.load(f)

            for item in data:
                user = User(item["name"], item["password"], item.get("role", "user"))

                # ✅ VERY IMPORTANT (restore borrowed books)
                for book_id in item.get("borrowed_books", []):
                    book = library.find_book(book_id)
                    if book:
                        user.borrowed_books.append(book)

                users[item["name"]] = user

    except FileNotFoundError:
        pass

    return users


def save_users(users):
    data = []

    for name, user in users.items():
        data.append({
            "name": name,
            "password": user.password,
            "role": user.role,
            "borrowed_books": [book.book_id for book in user.borrowed_books]
        })

    with open("users_data.json", "w") as f:
        json.dump(data, f)

library = Library()
library.load_books()
users = load_users(library)
# default admin
if "admin" not in users:
     users["admin"] = User("admin", "admin123", "admin")

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # print(username , password)

        if username in users and users[username].password == password:
            session["username"] = username
            session["role"] = users[username].role

            return redirect(url_for("dashboard"))
        else:
              flash("Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/")

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"]
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            flash("User already exists")

        users[username] = User(username, password, "user")
        save_users(users)

        flash("Registered successfully")

    return render_template("register.html")

@app.route("/show_books")
def show_books():
    return render_template("show_books.html", books=library.books)
@app.route("/add_book", methods=["GET","POST"])
def add_book():
     if request.method =="POST":
        book_id =int(request.form["book_id"])
        title = request.form["title"]
        author = request.form["author"]

        if library.find_book(book_id):
             flash("Book with this ID already exists.")
             return redirect(url_for("add_book"))
        
        library.add_book(Book(book_id,title,author))
        library.save_books()
        flash("Book added successfully")
        return redirect(url_for("show_books"))

     return render_template("add_book.html")


@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    if "username" not in session:
        return redirect("/")

    if request.method == "POST":
        username = session["username"]

        book_id = request.form.get("book_id")

        # 🔴 empty check
        if not book_id:
            flash("Please enter Book ID", "danger")
            return redirect(url_for("borrow"))

        # 🔴 number check
        try:
            book_id = int(book_id)
        except ValueError:
            flash("Invalid Book ID", "danger")
            return redirect(url_for("borrow"))

        book = library.find_book(book_id)

        if not book:
            flash("Book not found", "danger")
            return redirect(url_for("borrow"))

        if not book.available:
            flash("Book already borrowed", "warning")
            return redirect(url_for("borrow"))

        users[username].borrow_book(book)

        library.save_books()
        save_users(users)

        flash("Book borrowed successfully", "success")
        return redirect(url_for("show_books"))  # better UX

    return render_template("borrow.html")

@app.route("/my_books")
def my_books():
    if "username" not in session:
        return redirect("/")

    username = session["username"]
    user = users[username]

    return render_template("my_books.html", books=user.borrowed_books)


@app.route("/remove_book", methods=["GET", "POST"])
def remove_book():
    if session.get("role") != "admin":
        flash("Access denied")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        book_id = int(request.form["book_id"])

        if not library.find_book(book_id):
            flash("Book not found")

        library.remove_book(book_id)
        library.save_books()

        flash("Book removed successfully")

    return render_template("remove_book.html")


@app.route("/search", methods=["GET", "POST"])
def search_book():
    result = "not_searched"

    if request.method == "POST":
        title = request.form["title"].lower()
        result = None

        for book in library.books:
            if title in book.title.lower():
                result = book
                break

    return render_template("search.html", result=result)

@app.route("/logout")
def logout():
    session.clear()   # remove user data
    return redirect("/")

@app.route("/available")
def available_books():
    available = [b for b in library.books if b.available]
    return render_template("available.html", books=available)

@app.route("/borrowed")
def borrowed_books():
    borrowed = [b for b in library.books if not b.available]
    return render_template("borrowed.html", books=borrowed)

@app.route("/users")
def show_users():
    if session.get("role") != "admin":
        flash("Access denied")
        return redirect(url_for("dashboard"))

    return render_template("users.html", users=users)


@app.route("/return", methods=["GET", "POST"])
def return_book():
    if "username" not in session:
        return redirect("/")

    if request.method == "POST":
        username = session["username"]

        book_id = request.form.get("book_id")

        # 🔴 Check empty input
        if not book_id:
            flash("Please enter Book ID", "danger")
            return redirect(url_for("return_book"))

        # 🔴 Check valid number
        try:
            book_id = int(book_id)
        except ValueError:
            flash("Invalid Book ID", "danger")
            return redirect(url_for("return_book"))

        book = library.find_book(book_id)

        if not book:
            flash("Book not found", "danger")
            return redirect(url_for("return_book"))

        if book not in users[username].borrowed_books:
            flash("You don't have this book", "danger")
            return redirect(url_for("return_book"))

        users[username].return_book(book)

        library.save_books()
        save_users(users)

        flash("Book returned successfully", "success")
        return redirect(url_for("dashboard"))

    return render_template("return.html")
@app.route("/create_admin", methods=["GET", "POST"])
def create_admin():
    if "role" not in session or session["role"] != "admin":
        flash("Access denied")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            flash("User already exists")
            return redirect(url_for("create_admin"))

        users[username] = User(username, password, "admin")
        save_users(users)

        flash("New admin created")
        return redirect(url_for("dashboard"))

    return render_template("create_admin.html")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
