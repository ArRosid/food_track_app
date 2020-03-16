from flask import Flask, render_template, g, request
from datetime import datetime
import dbcon

app = Flask(__name__)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/', methods=["GET","POST"])
def index():
    db = dbcon.get_db()

    if request.method == "POST":
        date = request.form["date"] # the format will be yyyy-mm-dd
        
        dt = datetime.strptime(date, "%Y-%m-%d")
        database_date = datetime.strftime(dt, "%Y%m%d")
        
        db.execute("insert into log_date (entry_date) values (?)",
                    [database_date])
        db.commit()

    cur = db.execute("select * from log_date order by entry_date desc")
    results = cur.fetchall()

    date_result = []

    for r in results:
        single_date = {}
        d = datetime.strptime(str(r["entry_date"]), '%Y%m%d')
        single_date["pretty_date"] = datetime.strftime(d, "%B %d, %Y") #%B for month in word
        date_result.append(single_date)

    return render_template('home.html', results=date_result)

@app.route('/view/<date>/')
def view(date):
    db = dbcon.get_db()

    cur = db.execute("select * from log_date where entry_date=?", [date])
    result = cur.fetchone()
    d = datetime.strptime(str(result["entry_date"]), "%Y%m%d")
    pretty_date = datetime.strftime(d, "%B %d, %Y")

    food_cur = db.execute("select id, name from food")
    food_results = food_cur.fetchall()

    return render_template("day.html", pretty_date=pretty_date,
                            food_results=food_results)

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