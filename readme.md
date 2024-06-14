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


SELECT m.title AS menuName, SUM(s.quan) AS totalSales
            FROM sales s
            JOIN menus m ON s.menuId = m.id
            GROUP BY m.title
            ORDER BY totalSales DESC;



select SUM(s.quan), SUM(s.quan * m.price) from sales s join menus m on s.menuId = m.id where date(s.sellTime)BETWEEN '2024-06-13' AND '2024-06-14';


DELETE FROM menus WHERE id = 2;
select * from sales;
select * from menus;
select * from userss where userId = 'admin' and userPwd = '11'; 

INSERT INTO menus (kind, title, img, price, caffeine, protein, carbo, fat, kal) VALUES (0, "카페모카", 2, 5400, 53, 13, 15, 21, 504);