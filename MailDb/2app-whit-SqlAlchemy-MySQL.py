from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# MySQL bağlantı ayarları

# Lokalde calisan MySQL icin ayarlar
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sqluser:Aa123123@localhost/clarusdb'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Kendi RDS MySQL DB endpointinizi giriniz !!!  @.........../clarusway

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Clarusway_1@database-1.c1gusaos8lxd.us-east-1.rds.amazonaws.com/clarus'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    drop_table = text('DROP TABLE IF EXISTS users;')
    users_table = text(""" 
    CREATE TABLE users(username VARCHAR(255) NOT NULL PRIMARY KEY, email VARCHAR(255));
    """)
    data = text("""
    INSERT INTO users
    VALUES
        ("dora", "dora@amazon.com"),
        ("cansın", "cansın@google.com"),
        ("sencer", "sencer@bmw.com"),
        ("uras", "uras@mercedes.com"),
        ("ares", "ares@porche.com");
    """)
    db.session.execute(drop_table)
    db.session.execute(users_table)
    db.session.execute(data)
    db.session.commit()

def find_emails(keyword):
    with app.app_context():
        query = text(f"SELECT * FROM users WHERE username LIKE '%{keyword}%';")
        result = db.session.execute(query)
        user_emails = [(row[0], row[1]) for row in result]
        if not user_emails:
            user_emails = [("Not Found", "Not Found")]
        return user_emails

def insert_email(name, email):
    with app.app_context():
        query = text(f"SELECT * FROM users WHERE username = '{name}';")
        result = db.session.execute(query)
        response = ''
        if len(name) == 0 or len(email) == 0:
            response = 'Username or email cannot be empty!'
        elif not any(result):
            insert = text(f"INSERT INTO users VALUES ('{name}', '{email}');")
            db.session.execute(insert)
            db.session.commit()
            response = f"User {name} and {email} have been added successfully"
        else:
            response = f"User {name} already exists"
        return response

@app.route('/', methods=['GET', 'POST'])
def emails():
    if request.method == 'POST':
        user_app_name = request.form['user_keyword']
        user_emails = find_emails(user_app_name)
        return render_template('emails.html', name_emails=user_emails, keyword=user_app_name, show_result=True)
    else:
        return render_template('emails.html', show_result=False)

@app.route('/add', methods=['GET', 'POST'])
def add_email():
    if request.method == 'POST':
        user_app_name = request.form['username']
        user_app_email = request.form['useremail']
        result_app = insert_email(user_app_name, user_app_email)
        return render_template('add-email.html', result_html=result_app, show_result=True)
    else:
        return render_template('add-email.html', show_result=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
