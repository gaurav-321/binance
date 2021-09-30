import os
import MySQLdb.cursors
from flask import Flask, render_template, redirect, flash, url_for, session, request, json
from flask_ipban import IpBan
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from temp.main import account, tickers
from collections import OrderedDict

initial_total = account.TOTAL


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    fName = StringField('fName',
                        validators=[DataRequired(), Length(min=2, max=40)])
    lName = StringField('lName',
                        validators=[DataRequired(), Length(min=2, max=40)])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember')
    submit = SubmitField('Login')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'flask'
app.config['MYSQL_PASSWORD'] = 'rooted123#'
app.config['MYSQL_DB'] = 'flaskApi'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

mysql = MySQL(app)
ip_ban = IpBan(ban_seconds=200, ban_count=200)
ip_ban.init_app(app)


@app.route("/")
@app.route("/home")
def home():
    labels = list(OrderedDict.fromkeys([x['date'] for x in account.trades]))[::-1]
    values = []
    for date in labels:
        temp = []
        for x in account.trades:
            if x['date'] == date:
                temp.append(x['profit'])
        values.append(sum(temp))
    if len(values) == 0:
        values = [10]
    total_sell = len([x for x in account.trades if x['action'] == "SELL"])
    data = {"total Sell": total_sell,
            "positive trades": len([x for x in account.trades if x['profit'] > 0]),
            "negative trades": len([x for x in account.trades if x['profit'] < 0]),
            "Win Rate": (len([x for x in account.trades if x['profit'] > 0])/total_sell)*100 if total_sell > 0 else 1,
            "Average Profit": sum([x['profit'] for x in account.trades]) / total_sell if total_sell > 0 else 1,
            "Average Profit Per": sum([x['profit_per'] for x in account.trades]) / total_sell if total_sell > 0 else 1,
            }
    return render_template('home.html', tickers=tickers, assets=account.assets,
                           initial_total=initial_total, total=account.TOTAL,
                           profit=sum([x['profit'] for x in account.trades]), values=values, labels=labels,
                           title_chart='Profit Loss Day Vise', max=max(values) * 2, data=data)


@app.route("/current")
def current():
    if 'username' in session.keys():
        return render_template('current.html', tickers=tickers, assets=account.assets,
                               initial_total=initial_total, total=account.TOTAL,
                               profit=sum([x['profit'] for x in account.trades]))
    else:
        flash(f'Please Login to access the crypto trader', 'danger')
        return redirect("login")


@app.route("/trade")
def trade():
    if 'username' in session.keys():
        return render_template('trade.html', tickers=tickers, assets=account.assets,
                               initial_total=initial_total, total=account.TOTAL,
                               profit=sum([x['profit'] for x in account.trades]))
    else:
        flash(f'Please Login to access the crypto trader', 'danger')
        return redirect("login")


@app.route("/registers", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if 'username' in session.keys():
        return redirect("home")

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        fName = form.fName.data
        lName = form.lName.data
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM accounts WHERE username = '{username}' ")
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
            flash(f'{msg}', 'failed')
            return redirect(url_for('register'))
        else:
            cursor.execute("INSERT INTO accounts VALUES (% s, % s, % s, % s, % s)",
                           (fName, lName, username, email, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
        flash(f'{msg}', 'success')
        return redirect(url_for('login'))

    return render_template('new_register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if 'username' in session.keys():
        return redirect("home")
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
       # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute(f"SELECT * FROM accounts WHERE username = '{username}' AND password = '{password}' ")
       # account_found = cursor.fetchone()
        if username=="admin" and password=="gag1234":
            session["username"] = username
            flash(f'You have been logged in! as {session["username"]}', 'success')
            return redirect(url_for('home'))
        else:
            ip_ban.add()
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('new_login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route("/update.json", methods=['GET'])
def update():
    temp = []

    for x in tickers:
        temp.append(
            {'index': tickers.index(x), 'name': x.name, 'current': x.current, 'bought': x.bought_value,
             'quantity': x.bought_quantity,'rsi':x.rsi_val, 'profit': x.profit, 'profit_per': x.profit_per, 'link': x.link})

    if 'username' in session.keys():
        return json.dumps({"data": temp})
    else:
        ip_ban.add()
        return json.dumps([])


@app.route("/update_trade.json", methods=['GET'])
def update_trade():
    temp = []
    filter_request = request.args.get('filter')
    if len(account.trades) > 0:
        if filter_request:
            for x in account.trades:
                x['index'] = len(temp)
                if x['action'].lower() == filter_request:
                    temp.append(x)
        else:
            for x in account.trades:
                x['index'] = len(temp)
                temp.append(x)
    if 'username' in session.keys():
        return json.dumps({"data": temp}) if len(temp) > 0 else json.dumps(
            {"data": [{'index': "", 'name': "", 'current': "", 'bought': "", 'bought_busd': "",
                       'quantity': "", 'rsi': "", 'macd': "", 'profit': "", 'profit_per': "", 'action': '',
                       'link': ""}]})
    else:
        ip_ban.add()
        return json.dumps([])


if __name__ == '__main__':
    app.run("0.0.0.0", 8080, threaded=True)
