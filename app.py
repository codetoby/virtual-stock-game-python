from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from handlers import buy, sell, get_data, userportfolio
from cs50 import SQL

db = SQL("sqlite:///users.db")

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
PORT = 5000


def login_required(func):
    def wrapper(*args, **kwargs):
        if "id" not in session:
            return redirect("/login")
        else:
            return func(*args, **kwargs)
    wrapper.__name__ = func.__name__        
    return wrapper

def admin_required(func):
    def wrapper():
        id = session["id"]
        user = db.execute("SELECT admin from users where id=?", id)
        if user[0]["admin"] == True:
            return func()
        return redirect("/")
    wrapper.__name__ = func.__name__
    return wrapper

def checkInput(email) -> bool:
    
    if '@' in email or '.' in email:
        return True
    else:
        return False

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":
        
        email = request.form.get("email")
        password = request.form.get("password")
        admin = False
        
        if email is None or password is None:
            return render_template("failure.html")
        
        valid = checkInput(email)
        
        if valid == False:
            return render_template("register.html")
    
        user = db.execute("INSERT INTO users (email, password, admin) VALUES(?, ?, ?)", email, password, admin)
        id = user
        db.execute("insert into portfolio (id) VALUES(?)", id)
        
        return redirect("/login")
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    
    if request.method == "POST":
        
        email = request.form.get("email")
        password = request.form.get("password")
        
        if email is None or password is None:
            return render_template("failure.html")
        
        valid = checkInput(email)
        
        if valid == False:
            return render_template("failure.html")
        
        user = db.execute("select id, password from users where email = ?", email)
        
        if user:
            db_password = user[0]["password"]
            if password == db_password:
                session["id"] = user[0]["id"]
                return redirect("/")
        
        return render_template("failure.html")
    
    return render_template("login.html")

@app.route("/users")
@login_required
@admin_required
def users():
    users = db.execute("SELECT * FROM users")
    return jsonify(users)

@app.route("/")   
def index():
    return render_template("index.html")

@app.route("/portfolio")
@login_required
def portfolio():
    id = session["id"]
    stocks = userportfolio(id)#
    return render_template("portfolio.html", stocks=stocks)

@app.route("/order", methods=["GET", "POST"])
@login_required
def order():
    
    if request.method == "POST":
        id = session["id"]
        ticker = request.form.get("ticker")
        try:
            shares = int(request.form.get("shares"))
        except:
            return render_template("failure.html")
        orderTpye = request.form.get("orderType")
        
        if ticker is None or shares is None or orderTpye is None:
            return render_template("failure.html")
        
        if orderTpye == "buy":
            order = buy(ticker, shares, id)
        elif orderTpye == "sell":
            order = sell(ticker, shares, id)
    
        if order["success"] == False:
            return render_template("failure.html")     
    return render_template("order.html")

@app.route("/history")
@login_required
def history():
       
    id = session["id"]
    history = db.execute("select * from history where id = ?", id)   
    return render_template("history.html", history=history)

@app.route("/quote")
@login_required
def quote():

    id = session["id"]
    
    ticker = request.args.get("ticker")
    if ticker is None:
        return render_template("failure.html")
    
    data = get_data(ticker)
    
    history = db.execute("select * from history where id = ? and ticker = ?", id, ticker)
    return render_template("index.html", history=history, data=data)

if __name__ == "__main__":
    app.run(debug=True, port=PORT)