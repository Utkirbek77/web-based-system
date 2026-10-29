
import os
from flask import Flask, Blueprint, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields

app = Flask(__name__)
os.makedirs(app.instance_path, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("TODO_DATABASE_URI", "sqlite:///todo.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ERROR_404_HELP"] = False
app.config["RESTX_JSON"] = {"ensure_ascii": False}

db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    note = db.Column(db.String(200), default="")
    done = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form.get("todo", "").strip()
        note = request.form.get("note", "").strip()

        if text:
            todo = Todo(text=text, note=note)
            db.session.add(todo)
            db.session.commit()

        return redirect(url_for("index"))

    todos = Todo.query.order_by(Todo.id).all()
    return render_template("index.html", todos=todos)


@app.route("/delete/<int:id>")
def delete(id):
    todo = db.session.get(Todo, id)

    if todo:
        db.session.delete(todo)
        db.session.commit()

    return redirect(url_for("index"))


@app.route("/toggle/<int:id>")
def toggle(id):
    todo = db.session.get(Todo, id)

    if todo:
        todo.done = not todo.done
        db.session.commit()

    return redirect(url_for("index"))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    todo = db.get_or_404(Todo, id)

    if request.method == "POST":
        text = request.form.get("todo", "").strip()

        if text:
            todo.text = text
            todo.note = request.form.get("note", "").strip()
            db.session.commit()
            return redirect(url_for("index"))

    return render_template("edit.html", todo=todo)


api_bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    api_bp,
    version="1.0",
    title="Todo API",
    description="RESTful API for the Todo application",
    doc="/docs"
)

ns = api.namespace("todos", description="Todo operations")


todo_model = api.model("Todo", {
    "id": fields.Integer(readonly=True),
    "text": fields.String(required=True, example="우유 사기"),
    "note": fields.String(description="설명", example="2리터짜리로"),
    "done": fields.Boolean
})

todo_input = api.model("TodoInput", {
    "text": fields.String(required=True, example="우유 사기"),
    "note": fields.String(description="설명", example="2리터짜리로"),
    "done": fields.Boolean
})


@ns.route("/")
class TodoList(Resource):

    @ns.doc("Get all todos")
    @ns.param("done", "true for completed, false for incomplete")
    @ns.marshal_list_with(todo_model)
    def get(self):
        q = Todo.query
        done = request.args.get("done")

        if done is not None:
            q = q.filter_by(done=(done.lower() == "true"))

        return q.order_by(Todo.id).all()

    @ns.doc("Create a new todo")
    @ns.expect(todo_input, validate=True)
    @ns.marshal_with(todo_model, code=201)
    def post(self):
        data = api.payload
        todo = Todo(
            text=data["text"],
            note=data.get("note", ""),
            done=data.get("done", False)
        )

        db.session.add(todo)
        db.session.commit()

        return todo, 201, {"Location": f"/api/todos/{todo.id}"}


@ns.route("/<int:id>")
@ns.param("id", "Todo ID")
@ns.response(404, "Todo not found")
class TodoItem(Resource):

    @ns.doc("Get a single todo")
    @ns.marshal_with(todo_model)
    def get(self, id):
        return get_or_abort(id)

    @ns.doc("Replace a todo")
    @ns.expect(todo_input, validate=True)
    @ns.marshal_with(todo_model)
    def put(self, id):
        todo = get_or_abort(id)
        data = api.payload
        todo.text = data["text"]
        todo.note = data.get("note", "")
        todo.done = data.get("done", False)
        db.session.commit()
        return todo

    @ns.doc("Partially update a todo")
    @ns.expect(todo_input)
    @ns.marshal_with(todo_model)
    def patch(self, id):
        todo = get_or_abort(id)
        data = api.payload

        if "text" in data:
            todo.text = data["text"]

        if "note" in data:
            todo.note = data["note"]

        if "done" in data:
            todo.done = data["done"]

        db.session.commit()
        return todo

    @ns.doc("Delete a todo")
    @ns.response(204, "Todo deleted")
    def delete(self, id):
        todo = get_or_abort(id)
        db.session.delete(todo)
        db.session.commit()
        return "", 204


def get_or_abort(id):
    todo = db.session.get(Todo, id)
    if todo is None:
        ns.abort(404, f"{id} 번 할 일이 없습니다")
    return todo


app.register_blueprint(api_bp)


if __name__ == "__main__":
    app.run(debug=True)
