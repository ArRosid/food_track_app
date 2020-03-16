from flask import Flask, render_template, g, request
import dbcon

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/view')
def view():
    return render_template("day.html")

@app.route("/food", methods=["GET","POST"])
def food():

    db = dbcon.get_db()
   
    if request.method == "POST":
        food_name = request.form.get("food-name")
        protein = int(request.form.get("protein"))
        carbohydrates = int(request.form.get("carbohydrates"))
        fat = int(request.form.get("fat"))

        calories = protein * 4 + carbohydrates * 4 + fat * 9
        db.execute("insert into food (name, protein, carbohydrates, fat, calories)\
                    values (?,?,?,?,?)",
                    [food_name, protein, carbohydrates, fat, calories])
        db.commit()

    cur = db.execute("select * from food")
    results = cur.fetchall()

    return render_template("add_food.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)