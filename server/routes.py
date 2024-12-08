from flask import Blueprint, request, jsonify
import logging
import random

# Инициализация Blueprint
api_blueprint = Blueprint('api', __name__)

def create_process_manager():
    from server.process_manager import ProcessManager
    return ProcessManager

def get_db():
    from database import RestaurantDatabase  # Отложенный импорт, чтобы избежать кругового импорта
    return RestaurantDatabase("server/config.json")

# ==== ДИНАМИЧЕСКОЕ ОБНОВЛЕНИЕ СТАТУСОВ (WebSocket) ====
# Для интеграции WebSocket потребуется отдельный сервер или использование Flask-SocketIO.

# ==== ЗАЛЫ ====

@api_blueprint.route("/halls", methods=["GET"])
def get_halls():
    db = get_db()
    """Получить список всех залов."""
    halls = db.get_halls()
    return jsonify(halls)

@api_blueprint.route("/halls/<int:hall_id>", methods=["GET"])
def get_hall(hall_id):
    db = get_db()
    """Получить зал по ID."""
    hall = db.get_hall(hall_id)
    if not hall:
        return jsonify({"error": "Hall not found"}), 404
    return jsonify({"id": hall.id, "name": hall.name, "tables": [{"id": table.id, "status": table.status} for table in hall.tables]})

@api_blueprint.route("/halls/<int:hall_id>/tables/<int:table_id>/reserve", methods=["POST"])
def reserve_table(hall_id, table_id):
    db = get_db()
    """Забронировать столик."""
    if db.reserve_table(hall_id, table_id):
        db.save_changes()
        return jsonify({"status": "Table reserved successfully"}), 200
    return jsonify({"error": "Table is not available"}), 400

@api_blueprint.route("/halls/<int:hall_id>/tables/<int:table_id>/release", methods=["POST"])
def release_table(hall_id, table_id):
    db = get_db()
    """Освободить столик."""
    if db.release_table(hall_id, table_id):
        db.save_changes()
        return jsonify({"status": "Table released successfully"}), 200
    return jsonify({"error": "Table is not reserved"}), 400

@api_blueprint.route("/halls/statistics", methods=["GET"])
def get_hall_statistics():
    db = get_db()
    """Получить статистику по залам."""
    stats = db.get_hall_statistics()
    return jsonify(stats)

# ==== СОТРУДНИКИ ====

@api_blueprint.route("/employees", methods=["GET"])
def get_employees():
    db = get_db()
    """Получить список всех сотрудников."""
    employees = db.get_employee_loads()
    return jsonify(employees)

@api_blueprint.route("/employees/<int:employee_id>/tasks", methods=["GET"])
def get_employee_tasks(employee_id):
    db = get_db()
    """Получить текущие задачи сотрудника."""
    tasks = db.get_employee_tasks(employee_id)
    if "error" in tasks:
        return jsonify(tasks), 404
    return jsonify(tasks)

# ==== ЗАКАЗЫ ====

@api_blueprint.route("/orders", methods=["GET"])
def get_orders():
    db = get_db()
    """Получить список текущих заказов."""
    orders = db.get_current_orders()
    return jsonify(orders)

@api_blueprint.route("/orders/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    process_manager = create_process_manager()
    result = process_manager.cancel_order(order_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"status": "Order canceled successfully"}), 200

@api_blueprint.route("/orders", methods=["POST"])
def process_order():
    db = get_db()
    """Создать заказ."""
    data = request.get_json()
    recipe_name = data.get("recipe_name")
    quantity = data.get("quantity")

    if not recipe_name or not quantity:
        return jsonify({"error": "Missing recipe_name or quantity"}), 400

    # Обработка шумовой величины
    noise = random.uniform(-0.1, 0.1)  # Шум в пределах -10% до +10%
    result = db.process_order(recipe_name, quantity, noise)
    if "error" in result:
        return jsonify(result), 400

    process_manager = create_process_manager()
    process_manager.add_order(recipe_name, quantity)

    db.save_changes()
    return jsonify(result)

# ==== ИНГРЕДИЕНТЫ ====

@api_blueprint.route("/ingredients/<int:ingredient_id>", methods=["GET"])
def get_ingredient(ingredient_id):
    db = get_db()
    """Получить информацию об ингредиенте по ID."""
    ingredient = db.get_ingredient_by_id(ingredient_id)
    if not ingredient:
        return jsonify({"error": "Ingredient not found"}), 404
    return jsonify({"id": ingredient.id, "name": ingredient.name, "unit": ingredient.unit})

# ==== РЕЦЕПТЫ ====

@api_blueprint.route("/recipes/<string:recipe_name>", methods=["GET"])
def get_recipe(recipe_name):
    db = get_db()
    """Получить информацию о рецепте по имени."""
    recipe = db.get_recipe_by_name(recipe_name)
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    return jsonify({
        "id": recipe.id,
        "name": recipe.name,
        "complexity": recipe.complexity,
        "price": recipe.price,
        "ingredients": [{"ingredient_id": ing_id, "amount": amount} for ing_id, amount in recipe.ingredients]
    })

# ==== ВЫРУЧКА ====

@api_blueprint.route("/revenue", methods=["GET"])
def get_revenue():
    db = get_db()
    """Получить общую выручку."""
    revenue = db.get_total_revenue()
    return jsonify({"revenue": revenue}), 200

# ==== ЛОГИ ====

@api_blueprint.route("/logs", methods=["GET"])
def get_logs():
    """Получить последние записи логов."""
    with open("server.log", "r") as log_file:
        logs = log_file.readlines()
    return jsonify({"logs": logs[-50:]})  # Последние 50 записей

# ==== ТЕСТОВЫЕ ЭНДПОИНТЫ ====

@api_blueprint.route("/healthcheck", methods=["GET"])
def healthcheck():
    """Проверка статуса сервера."""
    return jsonify({"status": "OK", "message": "Server is running"}), 200

# ==== УНИФИЦИРОВАННАЯ ОБРАБОТКА ОШИБОК ====

@api_blueprint.errorhandler(400)
def handle_bad_request(e):
    return jsonify({"error": "Bad Request", "message": str(e)}), 400

@api_blueprint.errorhandler(404)
def handle_not_found(e):
    return jsonify({"error": "Not Found", "message": str(e)}), 404

# ==== ВСПОМОГАТЕЛЬНЫЕ ====

@api_blueprint.route("/save", methods=["POST"])
def save_changes():
    db = get_db()
    """Сохранить изменения в конфигурационный файл."""
    db.save_changes()
    return jsonify({"status": "Changes saved successfully"}), 200
