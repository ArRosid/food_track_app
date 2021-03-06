from flask import Flask, render_template, g, request
from datetime import datetime
import dbcon

app = Flask(__name__)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'postgres_db_conn'):
        g.postgres_db_conn.close()
    if hasattr(g, 'postgres_db_cur'):
        g.postgres_db_cur.close()

@app.route('/', methods=["GET","POST"])
def index():
    db = dbcon.get_db()

    if request.method == "POST":
        date = request.form["date"] # the format will be yyyy-mm-dd
        
        dt = datetime.strptime(date, "%Y-%m-%d")
        database_date = datetime.strftime(dt, "%Y%m%d")
        
        db.execute("insert into log_date (entry_date) values (%s)",
                    (database_date,))

    db.execute('''select log_date.entry_date, sum(food.protein) as protein, 
                        sum(food.carbohydrates) as carbohydrates , 
                        sum(food.fat) as fat, sum(food.calories) as calories
                    from log_date
                    left join food_date on food_date.log_date_id = log_date.id
                    left join food on food.id = food_date.food_id
                    group by log_date.id order by log_date.entry_date desc''')

    results = db.fetchall()

    date_result = []

    for r in results:
        single_date = {}

        single_date["entry_date"] = r["entry_date"]
        single_date["protein"] = r["protein"]
        single_date["carbohydrates"] = r["carbohydrates"]
        single_date["fat"] = r["fat"]
        single_date["calories"] = r["calories"]

        d = datetime.strptime(str(r["entry_date"]), '%Y-%m-%d')
        single_date["pretty_date"] = datetime.strftime(d, "%B %d, %Y") #%B for month in word
        date_result.append(single_date)

    return render_template('home.html', results=date_result)

@app.route('/view/<date>/', methods=["GET","POST"])
def view(date):
    db = dbcon.get_db()

    # get the id of date
    db.execute("select * from log_date where entry_date=%s", (date,))
    date_result = db.fetchone()

    if request.method == "POST":
        food_id = request.form.get("food-select")
        db.execute("insert into food_date (food_id, log_date_id) values (%s,%s)",
                    (food_id, date_result["id"],))
    
    db.execute("select * from log_date where entry_date=%s", (date,))
    result = db.fetchone()

    d = datetime.strptime(str(result["entry_date"]), "%Y-%m-%d")
    pretty_date = datetime.strftime(d, "%B %d, %Y")

    db.execute("select id, name from food")
    food_results = db.fetchall()

    db.execute('''select food.name, food.protein, food.carbohydrates, food.fat, food.calories
                            from log_date
                            join food_date on food_date.log_date_id = log_date.id 
                            join food on food.id = food_date.food_id 
                            where log_date.entry_date = %s ''', (date,))
    log_results = db.fetchall()

    totals = {}
    totals['protein'] = 0
    totals["carbohydrates"] = 0
    totals["fat"] = 0
    totals["calories"] = 0

    for food in log_results:
        totals["protein"] += food["protein"]
        totals["carbohydrates"] += food["carbohydrates"]
        totals["fat"] += food["fat"]
        totals["calories"] += food["calories"]

    return render_template("day.html", entry_date=result["entry_date"],
                            pretty_date=pretty_date, food_results=food_results,
                            log_results=log_results, totals=totals)

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
                    values (%s,%s,%s,%s,%s)",
                    (food_name, protein, carbohydrates, fat, calories,))

    db.execute("select * from food")
    results = db.fetchall()

    return render_template("add_food.html", results=results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001", debug=True)