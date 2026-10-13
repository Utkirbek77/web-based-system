
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

os.makedirs(app.instance_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    note = db.Column(db.String(200), default='')
    done = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('todo', '').strip()
        note = request.form.get('note', '').strip()

        if text:
            todo = Todo(text=text, note=note)
            db.session.add(todo)
            db.session.commit()

        return redirect(url_for('index'))

    todos = Todo.query.order_by(Todo.id).all()
    return render_template('index.html', todos=todos)


@app.route('/delete/<int:id>')
def delete(id):
    todo = db.session.get(Todo, id)

    if todo:
        db.session.delete(todo)
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/toggle/<int:id>')
def toggle(id):
    todo = db.session.get(Todo, id)

    if todo:
        todo.done = not todo.done
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    todo = db.get_or_404(Todo, id)

    if request.method == 'POST':
        text = request.form.get('todo', '').strip()

        if text:
            todo.text = text
            todo.note = request.form.get('note', '').strip()
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('edit.html', todo=todo)


if __name__ == '__main__':
    app.run(debug=True)
