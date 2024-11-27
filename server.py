from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.after_request
def after_request(response):
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# Database models
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)

class Hall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hall_id = db.Column(db.Integer, db.ForeignKey('hall.id'), nullable=False)
    is_reserved = db.Column(db.Boolean, default=False)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

# Utility function for JSON responses with UTF-8
def json_response(data, status=200):
    return Response(
        response=json.dumps(data, ensure_ascii=False),
        status=status,
        mimetype="application/json"
    )

# Populate database from config.json
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
        db.session.commit()

# API endpoints
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    data = [{"id": r.id, "name": r.name, "location": r.location} for r in restaurants]
    return json_response(data)

@app.route('/restaurant/<int:restaurant_id>', methods=['GET'])
def get_halls_and_tables(restaurant_id):
    halls = Hall.query.filter_by(restaurant_id=restaurant_id).all()
    response = []
    for hall in halls:
        tables = Table.query.filter_by(hall_id=hall.id).all()
        response.append({
            "hall_id": hall.id,
            "hall_name": hall.name,
            "tables": [{"id": t.id, "is_reserved": t.is_reserved} for t in tables]
        })
    return json_response(response)

@app.route('/menu/<int:restaurant_id>', methods=['GET'])
def get_menu(restaurant_id):
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    data = [{"id": m.id, "name": m.name, "price": m.price} for m in menu_items]
    return json_response(data)

@app.route('/reserve_table', methods=['POST'])
def reserve_table():
    table_id = request.json.get('table_id')
    table = Table.query.get(table_id)
    if table and not table.is_reserved:
        table.is_reserved = True
        db.session.commit()
        return json_response({"status": "success", "message": "Table reserved successfully"})
    return json_response({"status": "error", "message": "Table is already reserved"}, status=400)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        populate_data()
    app.run(debug=True)
