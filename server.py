import random
import time
from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from threading import Thread
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модели базы данных
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    revenue = db.Column(db.Float, default=0.0)

class Hall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    capacity = db.Column(db.Integer, default=20)

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hall_id = db.Column(db.Integer, db.ForeignKey('hall.id'), nullable=False)
    is_reserved = db.Column(db.Boolean, default=False)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)  # chef или waiter
    performance = db.Column(db.Float, default=1.0)  # производительность
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=100)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

# Функция для обработки заказов в параллельных потоках
def process_order(order_id, restaurant_id):
    time.sleep(random.uniform(1, 5))  # имитация времени на выполнение заказа
    print(f"Order {order_id} processed in restaurant {restaurant_id}")

def create_order(restaurant_id):
    order_id = random.randint(1000, 9999)
    thread = Thread(target=process_order, args=(order_id, restaurant_id))
    thread.start()

# Функция для корректных JSON-ответов
def json_response(data, status=200):
    return Response(
        response=json.dumps(data, ensure_ascii=False),
        status=status,
        mimetype="application/json"
    )

# Загрузка данных из config.json
def populate_data():
    if not Restaurant.query.first():
        with open('config.json', encoding='utf-8') as f:
            config = json.load(f)

        for restaurant_data in config["restaurants"]:
            restaurant = Restaurant(
                name=restaurant_data["name"],
                location=restaurant_data["location"]
            )
            db.session.add(restaurant)
            db.session.commit()

            for hall_data in restaurant_data["halls"]:
                hall = Hall(
                    name=hall_data["name"],
                    restaurant_id=restaurant.id
                )
                db.session.add(hall)
                db.session.commit()

                for table_data in hall_data["tables"]:
                    table = Table(
                        hall_id=hall.id,
                        is_reserved=table_data["is_reserved"]
                    )
                    db.session.add(table)

            for menu_item_data in restaurant_data["menu"]:
                menu_item = MenuItem(
                    name=menu_item_data["name"],
                    price=menu_item_data["price"],
                    restaurant_id=restaurant.id
                )
                db.session.add(menu_item)

            for employee_data in restaurant_data["employees"]:
                employee = Employee(
                    name=employee_data["name"],
                    role=employee_data["role"],
                    performance=employee_data["performance"],
                    restaurant_id=restaurant.id
                )
                db.session.add(employee)

            for warehouse_data in restaurant_data["warehouses"]:
                warehouse = Warehouse(
                    product_name=warehouse_data["product_name"],
                    quantity=warehouse_data["quantity"],
                    restaurant_id=restaurant.id
                )
                db.session.add(warehouse)

        db.session.commit()

# Эндпоинты
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    data = [{"id": r.id, "name": r.name, "location": r.location, "revenue": r.revenue} for r in restaurants]
    return json_response(data)

@app.route('/restaurant/<int:restaurant_id>', methods=['GET'])
def get_restaurant_info(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    halls = Hall.query.filter_by(restaurant_id=restaurant_id).all()
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    employees = Employee.query.filter_by(restaurant_id=restaurant_id).all()
    warehouses = Warehouse.query.filter_by(restaurant_id=restaurant_id).all()

    data = {
        "restaurant": {
            "name": restaurant.name,
            "location": restaurant.location,
            "revenue": restaurant.revenue
        },
        "halls": [{"id": hall.id, "name": hall.name, "capacity": hall.capacity} for hall in halls],
        "menu": [{"id": m.id, "name": m.name, "price": m.price} for m in menu_items],
        "employees": [{"id": e.id, "name": e.name, "role": e.role, "performance": e.performance} for e in employees],
        "warehouses": [{"id": w.id, "product_name": w.product_name, "quantity": w.quantity} for w in warehouses]
    }

    return json_response(data)

@app.route('/reserve_table', methods=['POST'])
def reserve_table():
    table_id = request.json.get('table_id')
    table = Table.query.get(table_id)
    if table and not table.is_reserved:
        table.is_reserved = True
        db.session.commit()
        create_order(table.hall_id)
        return json_response({"status": "success", "message": "Table reserved successfully"})
    return json_response({"status": "error", "message": "Table is already reserved"}, status=400)

# Запуск сервера
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        populate_data()
    app.run(debug=True)
