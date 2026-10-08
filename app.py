from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
  return render_template("index.html", user_name="Utkirbek", name1="Utkirbek")

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/hi/<name1>")
def hi(name1):
  return render_template("hi.html", name1="Utkirbek")

if __name__ == "__main__":
  app.run(debug=True)