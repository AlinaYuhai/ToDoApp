from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Todo
from forms import RegistrationForm, LoginForm, TodoForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret123"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

db.init_app(app)

# создаём таблицы сразу
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = TodoForm()
    if form.validate_on_submit():
        todo = Todo(task=form.task.data, owner=current_user)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for("index"))

    filter_option = request.args.get("filter", "all")
    if filter_option == "completed":
        todos = Todo.query.filter_by(owner=current_user, completed=True).all()
    elif filter_option == "active":
        todos = Todo.query.filter_by(owner=current_user, completed=False).all()
    else:
        todos = Todo.query.filter_by(owner=current_user).all()

    return render_template("index.html", todos=todos, form=form)

@app.route("/toggle/<int:todo_id>")
@login_required
def toggle(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.owner != current_user:
        flash("Not authorized!", "danger")
        return redirect(url_for("index"))
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>")
@login_required
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.owner != current_user:
        flash("Not authorized!", "danger")
        return redirect(url_for("index"))
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
