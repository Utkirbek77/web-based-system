from flask import Flask, render_template

app = Flask(__name__)


# 1. Home Page: Displays Name and Student ID
@app.route("/")
def home():
  student_name = "Utkirbek"  # Replace with your actual name
  student_id = "23012866"  # Replace with your actual student ID
  return render_template(
      "index.html", student_name=student_name, student_id=student_id
  )


# 2. Profile Page: Passes a Python list of 3 hobbies to Jinja2 template
@app.route("/profile")
def profile():
  hobbies = [
      "Coding & Microcontrollers",
      "Playing Football",
      "Watching Movies",
  ]
  return render_template("profile.html", hobbies=hobbies)


# 3. Dynamic Greeting Page: Uses dynamic URL parameter <name>
@app.route("/greet/<name>")
def greet(name):
  return render_template("greet.html", name=name)


if __name__ == "__main__":
  app.run(debug=True)