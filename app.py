from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модели
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Формы
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class TaskForm(FlaskForm):
    task = StringField('Task', validators=[InputRequired()])
    submit = SubmitField('Add Task')

# Роуты
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # сохраняем user_id в сессии
            request.environ['user_id'] = user.id
            return redirect(url_for('index', user_id=user.id))
        else:
            flash('Invalid credentials')
    return render_template('login.html', form=form)

@app.route('/index/<int:user_id>', methods=['GET', 'POST'])
def index(user_id):
    form = TaskForm()
    todos = Todo.query.filter_by(user_id=user_id).all()
    if form.validate_on_submit():
        new_task = Todo(task=form.task.data, user_id=user_id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index', user_id=user_id))
    return render_template('index.html', form=form, todos=todos)

@app.route('/toggle/<int:todo_id>')
def toggle(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for('index', user_id=todo.user_id))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    user_id = todo.user_id
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index', user_id=user_id))

# Создание базы при первом запуске
with app.app_context():
    db.create_all()
    # создаём тестового пользователя, если нет
    if not User.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('1234')
        user = User(username='admin', password=hashed_pw)
        db.session.add(user)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
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
