from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_cursor_connection
import pymysql
from ml.predict_model import predict_matchup
from ml.predict_model import predict_matchup_2

app = Flask(__name__)
app.secret_key = 'your_secret_key_low_key'

@app.route('/')
def home():
    return redirect(url_for('login'))

# 1. 회원가입 페이지 로직
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        try:
            conn = get_cursor_connection()
            cursor = conn.cursor()
            # MySQL은 플레이스홀더로 ? 대신 %s를 사용합니다
            sql = "INSERT INTO users (username, password, name, email) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, hashed_password, name, email))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
        except pymysql.err.IntegrityError:
            flash('이미 존재하는 아이디 또는 이메일입니다.')
            return redirect(url_for('register'))
            
    return render_template('register.html')

# 2. 로그인 페이지 로직
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_cursor_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone() # DictCursor 사용으로 결과가 딕셔너리로 반환됨
        cursor.close()
        conn.close()
        
        # 딕셔너리 키값으로 데이터 검증 ('password', 'user_id' 등)
        # if user : 사용자가 데이터베이스에 존재하는가?
        # check_password_hash 함수 : 입력한 비밀번호가 저장된 암호화 비밀번호와 일치하는지 검사
        # 사용자가 존재하고 비밀번호도 맞으면
        if user and check_password_hash(user['password'], password):
            # 로그인 상태를 유지하기 위해 session에 저장
            # 세션은 로그인한 사용자의 정보를 서버가 기억하는 공간 입니다.
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['name'] = user['name']
            return redirect(url_for('predict_2'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

@app.route("/events")
def events():

    conn = get_cursor_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM schedule
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    data = []

    for row in rows:

        data.append({

            "title": f"{row['away_team']} vs {row['home_team']} {row['result']}",

            "start": row['game_date'].strftime("%Y-%m-%d"),
            
            # FullCalendar에서 기본적으로 제공하는 정보는 title, start, end 등입니다. 그 외에 사용자가 
            # 직접 추가한 데이터는 extendedProps 안에 저장됩니다.
            "away_team": row['away_team'],
            
            "home_team": row['home_team'],
            
            "result": row['result']
        })

    return jsonify(data)

@app.route("/predict")
def predict():

    away = request.args.get("away")
    home = request.args.get("home")

    result = predict_matchup(
        away,
        home,
        team_A_is_home=False
    )

    return render_template(
        "predict.html",

        away=away,
        home=home,

        away_prob=result["away_prob"],
        home_prob=result["home_prob"],

        statA=result["statA"],
        statB=result["statB"],

        h2h=result["h2h"],

        winner=result["winner"],

        confidence=result["confidence"],
        confidence_level=result["confidence_level"]
    )

@app.route('/predict_2', methods=['GET', 'POST'])

def predict_2():
    if 'username' not in session: return redirect(url_for('login'))
    
    teams = ['KIA', '삼성', 'LG', '두산', 'KT', 'SSG', '롯데', '한화', 'NC', '키움']
    result = None
    
    team_A = ""
    team_B = ""

    if request.method=="POST":

        team_A=request.form.get("team_A")
        team_B=request.form.get("team_B")

        is_home=request.form.get("is_home")

        result = predict_matchup_2(
            team_A,
            team_B,
            team_A_is_home=(is_home == "A_home")
        )

    return render_template(

          "predict_2.html",

          team_A=team_A,
          team_B=team_B,
          teams=teams,
          result=result,
          name=session['name'],

          selected_A=team_A,
          selected_B=team_B

      )
    
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)