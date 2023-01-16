import jwt, datetime, hashlib, certifi

from flask import Flask, render_template, request, jsonify, url_for, redirect

app = Flask(__name__)

from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb+srv://yunseo:sparta@cluster0.6bemlvq.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

##### 로그인
SECRET_KEY = 'HoneyHobby'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload['id']})
        return render_template('login.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for('login', msg='로그인 시간이 만료되었습니다.'))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('login', msg='로그인 정보가 존재하지 않습니다.'))

@app.route('/login')
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)

# 로그인 기능
# id,pw를 클라이언트에게 받아와 pw를 해쉬인코딩 하여 암호화한다.
# id와 암호화한 pw를 mongoDB에 있는지 확인하고, 없을시에는 result = None
# 클라이언트에게 받은 id와 pw가 mongoDB와 일치할 시 token을 생성한다.
# 클라이언트에게 토큰을 전송한다.

@app.route("/api/sign_in", methods=['POST'])
def signin():
    id_receive = request.form['id_give']
    password_receive = request.form['pw_give']
    # pw를 암호화합니다.
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # 해당 유저를 찾습니다.
    result = db.users.find_one({'id': id_receive, 'password': pw_hash})
    # 찾으면 토큰을 만들어 발급합니다.
    if result is not None:
        payload = {'id': id_receive, 'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)}
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token, 'msg': '로그인 성공!'})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})

##### 회원가입
ca = certifi.where()

client = MongoClient('mongodb+srv://yunseo:sparta@cluster0.6bemlvq.mongodb.net/?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

@app.route('/signup')
def sign_up():
    return render_template('register.html')

#로그인 완료 시 메인 페이지로 이동
@app.route('/main')
def page_main():
    return render_template('main.html')

@app.route("/api/signup", methods=["POST"])
def web_signup_post():
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {'id': id_receive, 'password': pw_hash}
    db.users.insert_one(doc)

    return jsonify({'msg': '가입 완료'})

@app.route("/signin", methods=["GET"])
def web_signup_get():
    user_list = list(db.users.find({}, {'_id': False}))
    return jsonify({'users': user_list})


@app.route('/main')
def main():
    return render_template('main.html')
@app.route("/main_list", methods=["GET"])
def main_list():
    main_list = list(db.hobby.find({}, {'_id': False}))
    # print(main_list)
    return jsonify({'hobby':main_list})

@app.route('/mypage')
def mypage():
   return render_template('upload.html')

# @app.route("/connect")
# def connect():
#     # return jsonify({'msg':'연결완료!'})
#     return redirect(url_for('mypage'))

ca = certifi.where()
client = MongoClient('mongodb+srv://eastjin:1q2w3e4r@cluster0.nb3pybc.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

# 등록 화면
@app.route('/upload', methods=['GET','POST'])
def newHome():
    # if request.method =='POST':
        # return redirect(url_for('upload_post'))
    return render_template('upload.html')

# 등록 동작
@app.route("/main", methods=["POST"])
def bucket_post():
    # title_receive = request.form['title_give']
    # url_receive = request.form['url_give']
    # contents_receive = request.form['contents_give']

    title_receive = request.form['title']
    url_receive = request.form['url']
    contents_receive = request.form['contents']

    print(title_receive)

    hobby_list = list(db.hobby.find({}, {'_id': False}))
    count = len(hobby_list) + 1

    doc = {
        'num': count,
        'title': title_receive,
        'url': url_receive,
        'contents': contents_receive
        # 'delete':0
    }
    db.hobby.insert_one(doc)
    # return jsonify({'msg': 'save'})
    return render_template('main.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)