from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL
from json import JSONEncoder
import numpy, hashlib, os, logging, json



app = Flask(
    __name__,
    static_url_path='',
    static_folder='./', ## 정적 폴더 위치, default로 index.html을 불러옴
)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tiger'
app.config['MYSQL_DB'] = 'mydatabase'
mysql = MySQL(app)


## 초기 설정
@app.route('/')
@app.route('/home')
def home():
    return app.send_static_file("./index.html")





################################################################################
## 여기에 필요한 기능 코드 작성

## DB기능
def encrypt_password(password):
    # 비밀번호를 SHA-256 해시 함수를 사용하여 암호화
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


@app.route('/signUp', methods=['POST'])
def register_user():
    data = request.json
    user_id = data['userId']
    user_pwd = data['userPwd']
    encrypted_password = encrypt_password(user_pwd)
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (userId, userPwd) VALUES (%s, %s)", (user_id, encrypted_password))
    mysql.connection.commit()
    cur.close()
    
    return 'User registered successfully', 201



@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    user_id = data['userId']
    user_pwd = data['userPwd']

    # 사용자가 제공한 아이디를 가진 사용자가 데이터베이스에 있는지 확인
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE userId = %s and userPwd = %s", (user_id, encrypt_password(user_pwd)))
    user = cur.fetchone()
    cur.close()


    # 사용자가 데이터베이스에 존재하고 비밀번호가 일치하는지 확인
    if user != None:
        return jsonify({'success': True, 'message': '로그인 성공'})
    else:
        return jsonify({'success': False, 'message': '아이디 또는 비밀번호가 잘못되었습니다.'})




###########################################################
## 주문
@app.route('/kiosk_page/order', methods=['POST'])
def order():
    logDisable(False) ## 로그 저장

    order_menu = request.form["order"]
    fileSave(order_menu)
    output = {"output": "none"}
    output = json.dumps(output, cls=NumpyArrayEncoder)
    return outputJSON(json.loads(output), "ok")



## 주문 정보 가지고 오기
@app.route('/kitch_page/getOrder', methods=['POST'])
def getOrder(): 
    logDisable(True) ## 로그 저장 X

    currentOrder = os.listdir('./data')
    output = {"output": currentOrder}
    output = json.dumps(output, cls=NumpyArrayEncoder)
    return outputJSON(json.loads(output), "ok")

################################################################################
## 테스트 코드: 참고용
@app.route('/kiosk_page/test', methods=['POST'])
def test():
    output = request.form["name"]
    output = {"output": output}
    output = json.dumps(output, cls=NumpyArrayEncoder)
    return outputJSON(json.loads(output), "ok")

def fileSave(content):
    path = './data'
    f = open(f'{path}/{content}.txt', 'w')
    f.write(f'{content} + 111')
    f.close()

def logDisable(n):
    log = logging.getLogger('werkzeug')
    log.disabled = n 

def outputJSON(msg, status="error"):
    return {"data": msg, "status": status}


@app.route('/image_count')
def image_count():

    directory_name = request.args.get('name', 'Caffeine') # 기본값 - 카페인
    image_directory = f'./res/{directory_name}'  # 이미지가 있는 디렉토리 경로
    
    if not os.path.exists(image_directory):
        return jsonify({'count': 0, 'error': 'Directory not found'}), 404

    
    image_files = [f for f in os.listdir(image_directory) if os.path.isfile(os.path.join(image_directory, f))]
    image_count = len(image_files)
    return jsonify({'count': image_count})



class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

if __name__ == '__main__':
    app.run(debug=True)