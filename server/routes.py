from flask import Blueprint, request, jsonify

# Инициализация Blueprint
api_blueprint = Blueprint('api', __name__)
def create_process_manager():
    from server.process_manager import ProcessManager
    return ProcessManager

def get_db():
    from database import RestaurantDatabase  # Отложенный импорт, чтобы избежать кругового импорта
    return RestaurantDatabase("server/config.json")
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

# ==== СОТРУДНИКИ ====

@api_blueprint.route("/employees", methods=["GET"])
def get_employees():
    db = get_db()
    """Получить список всех сотрудников."""
    employees = db.get_employee_loads()
    return jsonify(employees)

@api_blueprint.route("/employees/<int:employee_id>/complete_order", methods=["POST"])
def complete_order(employee_id):
    db = get_db()
    """Завершить заказ для сотрудника."""
    result = db.complete_order(employee_id)
    if "error" in result:
        return jsonify(result), 400
    db.save_changes()
    return jsonify(result)

# ==== ЗАКАЗЫ ====

@api_blueprint.route("/orders", methods=["POST"])
def process_order():
    db = get_db()
    """Создать заказ."""
    data = request.get_json()
    recipe_name = data.get("recipe_name")
    quantity = data.get("quantity")

    if not recipe_name or not quantity:
        return jsonify({"error": "Missing recipe_name or quantity"}), 400

    result = db.process_order(recipe_name, quantity)
    if "error" in result:
        return jsonify(result), 400
    
    # Добавление заказа в очередь на обработку
    ProcessManager= create_process_manager()
    process_manager = ProcessManager(db)
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
        "ingredients": [{"ingredient_id": ing_id, "amount": amount} for ing_id, amount in recipe.ingredients]
    })

# ==== СКЛАДЫ ====

@api_blueprint.route("/warehouses/<int:warehouse_id>", methods=["GET"])
def get_warehouse(warehouse_id):
    db = get_db()
    """Получить информацию о складе по ID."""
    warehouse = db.get_warehouse_by_id(warehouse_id)
    if not warehouse:
        return jsonify({"error": "Warehouse not found"}), 404
    return jsonify({
        "id": warehouse.id,
        "name": warehouse.name,
        "ingredients": [{"ingredient_id": ing_id, "amount": amount} for ing_id, amount in warehouse.ingredients]
    })

# ==== ВСПОМОГАТЕЛЬНЫЕ ====

@api_blueprint.route("/save", methods=["POST"])
def save_changes():
    db = get_db()
    """Сохранить изменения в конфигурационный файл."""
    db.save_changes()
    return jsonify({"status": "Changes saved successfully"}), 200
