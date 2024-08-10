import boto3
import json
from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

def get_db_credentials(secret_name, region_name):
    # AWS Secrets Manager'dan kimlik bilgilerini al
    client = boto3.client('secretsmanager', region_name=region_name)
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

# Secrets Manager icin kullanilan kimlik bilgilerini tanimla
secret_name = "mailDB-sec-manager" #Kendi olusturdugunuz Secret manager in adini giriniz !!!
region_name = "us-east-1"          # Region name giriniz !!!
db_credentials = get_db_credentials(secret_name, region_name)

# MySQL bağlantı ayarları
db_config = {
    'user': db_credentials['username'],
    'password': db_credentials['password'],
    'host': db_credentials['host'],
    'database': db_credentials['dbname']
}

def execute_query(query, params=None):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
    finally:
        cursor.close()
        connection.close()

# Veritabanını oluşturma ve başlatma
with app.app_context():
    drop_table = "DROP TABLE IF EXISTS users;"
    users_table = """
    CREATE TABLE users (
        username VARCHAR(255) NOT NULL PRIMARY KEY,
        email VARCHAR(255)
    );
    """
    data = """
    INSERT INTO users (username, email) VALUES
        ('dora', 'dora@amazon.com'),
        ('cansın', 'cansın@google.com'),
        ('sencer', 'sencer@bmw.com'),
        ('uras', 'uras@mercedes.com'),
        ('ares', 'ares@porche.com');
    """
    execute_query(drop_table)
    execute_query(users_table)
    execute_query(data)

def find_emails(keyword):
    query = "SELECT * FROM users WHERE username LIKE %s;"
    result = execute_query(query, (f"%{keyword}%",))
    user_emails = [(row[0], row[1]) for row in result]
    if not user_emails:
        user_emails = [("Not Found", "Not Found")]
    return user_emails

def insert_email(name, email):
    query = "SELECT * FROM users WHERE username = %s;"
    result = execute_query(query, (name,))
    if len(name) == 0 or len(email) == 0:
        return 'Username or email cannot be empty!'
    elif not result:
        insert = "INSERT INTO users (username, email) VALUES (%s, %s);"
        execute_query(insert, (name, email))
        return f"User {name} and {email} have been added successfully"
    else:
        return f"User {name} already exists"

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
    app.run(host='0.0.0.0', port=8081)