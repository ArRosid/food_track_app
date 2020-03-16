from flask import Flask, render_template, g, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/view')
def view():
    return render_template("day.html")

@app.route("/food", methods=["GET","POST"])
def food():
    if request.method == "POST":
        food_name = request.form.get("food-name")
        protein = request.form.get("protein")
        carbohydrates = request.form.get("carbohydrates")
        fat = request.form.get("fat")

        return f"<h1>{food_name} {protein} {carbohydrates} {fat}</h1>"

    return render_template("add_food.html")


if __name__ == "__main__":
    app.run(debug=True)