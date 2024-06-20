## KIOSK PROJECT

## How to Configuration?

```bash
pip install flask
```

## How to use it?

```bash
python service.py
```

and then connect http://localhost:5000/



## Program initalation
# MySQL configurations  <-- service.py setting
app.config['MYSQL_HOST'] = 'your_local_host'
app.config['MYSQL_USER'] = 'your_id'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'database_name'
mysql = MySQL(app)



## DB SHEMA
CREATE DATABASE mydatabase;
GRANT ALL PRIVILEGES ON mydatabase.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

use mydatabase;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userId VARCHAR(50) NOT NULL,
    userPwd VARCHAR(255) NOT NULL
);

CREATE TABLE menus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kind INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    img INT NOT NULL,
    price INT NOT NULL,
    caffeine INT,
    protein INT,
    carbo INT,
    fat INT,
    kal INT
);


CREATE TABLE sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sellTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    menuId INT,
    quan INT,
    FOREIGN KEY (menuId) REFERENCES menus(id)
);


