from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL
from json import JSONEncoder
from datetime import datetime
import numpy, hashlib, os, logging, json, base64



app = Flask(
    __name__,
    static_url_path='',
    static_folder='./', ## 정적 폴더 위치, default로 index.html을 불러옴
)


#이미지 저장경로
UPLOAD_FOLDER = '/res/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

## DB기능 - 로그인
def encrypt_password(password):
    # 비밀번호를 SHA-256 해시 함수를 사용하여 암호화
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


@app.route('/signUp', methods=['POST'])
def registerUser():
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
def loginUser():
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


#------------------------------------
## DB기능 - 메뉴 추가
@app.route('/addMenu', methods = ['POST'])
def addManu():
    MENU = ['Caffeine', 'NonCaffeine', 'Desert']

    try:
        data = request.json
        kind = int(data['kind'])
        title = data['title']
        price = int(data['price'])
        caffeine = int(data['caffeine'])
        protein = int(data['protein'])
        carbo = int(data['carbohydrates'])
        fat = int(data['fat'])
        kal = int(data['calories'])
        imageCount = 0
        fileName = None
        

        if 'imgFile' in data:
            imgData = data['imgFile']
            imgByte = base64.b64decode(imgData)
            imageDirectory = f'./res/{MENU[kind]}'  # 이미지가 있는 디렉토리 경로
            imageFiles = [f for f in os.listdir(imageDirectory) if os.path.isfile(os.path.join(imageDirectory, f))]
            imageCount = len(imageFiles) + 1
            
            fileName = f'drink{imageCount}.jpg'
            filePath = os.path.join(imageDirectory, fileName)

            with open(filePath, 'wb') as file:
                file.write(imgByte)
        else:
            print('이미지 파일 낫 파운드')
            


        # Print request data to the terminal
        #print(f"Received Data: {data}")
        print("imageCount", imageCount)

        # menus 테이블에 추가
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO menus (kind, title, img, price, caffeine, protein, carbo, fat, kal) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
            (kind, title, imageCount, price, caffeine, protein, carbo, fat, kal)
        )
        mysql.connection.commit()
        cur.close()



        return jsonify({'success': True, 'message': 'Menu added successfully'}), 201

    except Exception as e:
        print('경고 경고')
        if fileName and os.path.exists(filePath):
            os.remove(filePath)
        return jsonify({'success': False, 'message': 'Failed to add menu', 'error': str(e)}), 500
    
#--------------------------------------------------
#메뉴 수정하기 기능
# 메뉴 목록 API
@app.route('/get_menus')
def get_menus():
    try:
        cur = mysql.connection.cursor()
        sql = "SELECT * FROM menus"
        cur.execute(sql)
        menus = cur.fetchall()
        cur.close()
        return jsonify(menus)
    
    except Exception as e:
        return f'메뉴 불러오기 중 오류가 발생했습니다: {str(e)}'



@app.route('/delete/<int:menu_id>/<int:kind>/<int:img>', methods=['DELETE'])
def delete_menu(menu_id, kind, img):
    MENU = ['Caffeine', 'NonCaffeine', 'Desert']
    imageDirectory = f'./res/{MENU[kind]}' 
    fileName = f'drink{img}.jpg'

    try:
        # 데이터베이스 트랜잭션 시작
        cur = mysql.connection.cursor()

        # 메뉴 데이터 삭제
        sql_delete_menu = "DELETE FROM menus WHERE id = %s"
        cur.execute(sql_delete_menu, (menu_id,))
        
        # 이미지 파일 삭제
        file_path = os.path.join(imageDirectory, fileName)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f'{fileName} 파일이 성공적으로 삭제되었습니다.')
        else:
            print(f'{fileName} 파일이 존재하지 않습니다.')

        # 데이터베이스 트랜잭션 커밋
        mysql.connection.commit()

        # 데이터베이스 커서 닫기
        cur.close()

        return '메뉴가 성공적으로 삭제되었습니다.'
    except Exception as e:
        # 트랜잭션 롤백
        mysql.connection.rollback()
        return f'메뉴 삭제 중 오류가 발생했습니다: {str(e)}'

#-----------------------------------
#메뉴 수정
@app.route('/update/<int:menu_id>', methods=['PUT'])
def update_menu(menu_id):
    try:
        # 클라이언트로부터 전송된 데이터 가져오기
        menu_data = request.form
        name = menu_data.get("name")
        price = int(menu_data.get("price"))
        caffeine = int(menu_data.get("caffeine"))
        protein = int(menu_data.get("protein"))
        carbo = int(menu_data.get("carbo"))
        fat = int(menu_data.get("fat"))
        kal = int(menu_data.get("calories"))

        # 메뉴 데이터베이스 업데이트
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE menus
            SET title = %s, price = %s, caffeine = %s, protein = %s, carbo = %s, fat = %s, kal = %s
            WHERE id = %s
        """, (name, price, caffeine, protein, carbo, fat, kal, menu_id))
        mysql.connection.commit()
        cur.close()

        # 업데이트된 메뉴 데이터를 클라이언트에 응답
        return jsonify({"message": "메뉴가 성공적으로 수정되었습니다."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




###########################################################
## 주문
@app.route('/kiosk_page/order', methods=['POST'])
def order():

    try:
        data = request.json

        for item in data:
            menuId = item['menuId']
            quan = item['quan']
            content = {menuId : quan}
            fileSave(content)


            # 로그 데이터베이스 입력
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO sales (menuId, quan) VALUES (%s, %s)", (menuId, quan))
            mysql.connection.commit()
            cur.close()


        return jsonify({"message": "주문이 성공적으로 되었습니다."}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500




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
    if not os.path.exists(path):
        os.makedirs(path)

    # 현재 시간 가져오기
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    menu_id, quan = list(content.items())[0]

    # 안전한 파일 이름 생성
    file_name = f'{current_time}_{menu_id}_{quan}.txt'
    file_path = os.path.join(path, file_name)

    with open(file_path, 'w') as f:
        f.write(f'{file_name}')

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