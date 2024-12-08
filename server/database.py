# Логика работы с данными
import json
# Класс для отображения заллов
class Hall:
    def __init__(self, hall_id, name, tables):
        self.id = hall_id
        self.name = name
        self.tables = tables  # Список объектов Table
    #Найти столик по ID
    def get_table(self, table_id):
        
        return next((table for table in self.tables if table.id == table_id), None)

# класс для отображения столов    
class Table:
    def __init__(self, id, status):
        self.id = id
        self.status = status
    def set_status(self, status):
        self.status = status

#Класс для ингридиентов
class Ingredient:
    def __init__(self, id, name, unit):
        self.id = id
        self.name = name
        self.unit = unit

# Класс для представления рецепта
class Recipe:
    def __init__(self, id, name, ingredients, complexity, prise):
        self.id = id
        self.name = name
        self.ingredients = ingredients  # Список (ingredient_id, amount)
        self.complexity = complexity
        self.prise = prise

# Класс для представления склада
class Warehouse:
    def __init__(self, id, name, ingredients):
        self.id = id
        self.name = name
        self.ingredients = ingredients  # Список (ingredient_id, amount)

# клсасс персонала
class Employee:
    def __init__(self, id, name, role, performance):
        self.id = id
        self.name = name
        self.role = role
        self.performance = performance
        self.orders = []  # Стек заказов

    def assign_order(self, order):
        """Добавить заказ в стек."""
        self.orders.append(order)

    def complete_order(self):
        """Удалить выполненный заказ из стека."""
        if self.orders:
            return self.orders.pop(0)
        return None

    def get_load(self):
        """Вернуть количество заказов в стеке."""
        return len(self.orders)

# Класс для работы с базой данных
class RestaurantDatabase:
    def __init__(self, config_file):
        self.config_file = config_file
        self.halls = []
        self.ingredients = []
        self.recipes = []
        self.warehouses = []
        self.employees = []  # Добавляем сотрудников
        self.load_data(config_file)

    def load_data(self, config_file):
        with open(config_file, 'r') as file:
            data = json.load(file)
        
       
        # Загрузка залов
        self.halls = []
        for hall_data in data.get("halls", []):
            try:
                hall_id = hall_data["id"]  # Проверяем, что есть id для зала
                name = hall_data["name"]   # Проверяем, что есть имя зала
                tables_data = hall_data.get("tables", [])  # Получаем таблицы (или пустой список, если нет)

                # Загружаем таблицы
                tables = []
                for table_data in tables_data:
                    try:
                        table_id = table_data["id"]  # Проверяем наличие id стола
                        status = table_data["status"]  # Проверяем статус стола
                        tables.append(Table(id=table_id, status=status))
                    except KeyError as e:
                        print(f"Warning: Missing key {e} in table data: {table_data}")

                # Создаем объект зала
                hall = Hall(hall_id=hall_id, name=name, tables=tables)
                self.halls.append(hall)

            except KeyError as e:
                print(f"Warning: Missing key {e} in hall data: {hall_data}")


            
        # Загрузка сотрудников
        for employee_data in data["employees"]:
            employee = Employee(
                employee_data["id"],
                employee_data["name"],
                employee_data["role"],
                employee_data["performance"]
            )
            self.employees.append(employee)

        # Загружаем ингредиенты
        for ingredient_data in data["ingredients"]:
            ingredient = Ingredient(
                ingredient_data["id"],
                ingredient_data["name"],
                ingredient_data["unit"]
            )
            self.ingredients.append(ingredient)

        # Загружаем рецепты
        for recipe_data in data["recipes"]:
            ingredients = []
            for ingredient_data in recipe_data["ingredients"]:
                ingredients.append((ingredient_data["ingredient_id"], ingredient_data["amount"]))
            recipe = Recipe(
                recipe_data["id"],
                recipe_data["name"],
                ingredients,
                recipe_data["complexity"],
                recipe_data["price"]
                
            )
            self.recipes.append(recipe)

        # Загружаем склады
        for warehouse_data in data["warehouses"]:
            ingredients = []
            for ingredient_data in warehouse_data["ingredients"]:
                ingredients.append((ingredient_data["ingredient_id"], ingredient_data["amount"]))
            warehouse = Warehouse(
                warehouse_data["id"],
                warehouse_data["name"],
                ingredients
            )
            self.warehouses.append(warehouse)

    #вернуть все залы
    def get_halls(self):
        return [{"id": hall.id, "name": hall.name, "tables": [{"id": table.id, "status": table.status} for table in hall.tables]} for hall in self.halls]

    #вернуть зал по ID
    def get_hall(self, hall_id):
        return next((hall for hall in self.halls if hall.id == hall_id), None)
    
    #вернуть зал по имени
    def get_hall_by_name(self, name):
        # Находит и возвращает зал по имени
        for hall in self.halls:
            if hall.name == name:
                return hall
        return None  # Если зал с таким именем не найден

    #вернуть стол в определенном зале с определеннымм индексом
    def get_table(self, hall_id, table_id):
        hall = self.get_hall(hall_id)
        return hall.get_table(table_id)
    
    #резервируем стол
    def reserve_table(self, hall_id, table_id):
        hall = self.get_hall(hall_id)
        if hall:
            table = hall.get_table(table_id)
            if table and table.status == "free":
                table.set_status("reserved")
                return True
        return False

    def release_table(self, hall_id, table_id):
        hall = self.get_hall(hall_id)
        if hall:
            table = hall.get_table(table_id)
            if table and table.status == "reserved":
                table.set_status("free")
                return True
        return False
    

    # Получить ингредиент по ID
    def get_ingredient_by_id(self, ingredient_id):
        for ingredient in self.ingredients:
            if ingredient.id == ingredient_id:
                return ingredient
        return None

    # Получить рецепт по имени
    def get_recipe_by_name(self, recipe_name):
        for recipe in self.recipes:
            if recipe.name == recipe_name:
                return recipe
        return None

    # Получить склад по ID
    def get_warehouse_by_id(self, warehouse_id):
        for warehouse in self.warehouses:
            if warehouse.id == warehouse_id:
                return warehouse
        return None

    # Проверить, достаточно ли ингредиентов для рецепта
    def check_ingredients_for_recipe(self, recipe_name, quantity):
        recipe = self.get_recipe_by_name(recipe_name)
        if recipe:
            for ingredient_id, amount_needed in recipe.ingredients:
                ingredient = self.get_ingredient_by_id(ingredient_id)
                if ingredient:
                    total_needed = amount_needed * quantity
                    # Проверяем, есть ли нужное количество ингредиентов на складе
                    for warehouse in self.warehouses:
                        for warehouse_ingredient_id, warehouse_amount in warehouse.ingredients:
                            if warehouse_ingredient_id == ingredient.id:
                                if warehouse_amount < total_needed:
                                    return False  # Не хватает ингредиентов
        return True

    # Обработать заказ
    def process_order(self, recipe_name, quantity):
        recipe = self.get_recipe_by_name(recipe_name)
        if not recipe:
            return {"error": "Recipe not found"}

        # Проверяем наличие ингредиентов
        if not self.check_ingredients_for_recipe(recipe_name, quantity):
            return {"error": "Not enough ingredients"}

        # Ищем наименее загруженного повара
        chef = self.get_least_loaded_employee("chef")
        if not chef:
            return {"error": "No available chefs"}

        # Рассчитываем время выполнения
        base_time = recipe.complexity * 10  # 10 минут на единицу сложности
        time_to_complete = base_time / chef.performance

        # Вычисляем стоимость заказа
        total_cost = recipe.price * quantity

        # Создаём заказ
        order = {
            "recipe_name": recipe_name,
            "quantity": quantity,
            "time_to_complete": time_to_complete,
            "total_cost": total_cost
        }

        # Добавляем заказ в стек повара
        chef.assign_order(order)

        # Списываем ингредиенты
        self.deduct_ingredients(recipe_name, quantity)
        return {"status": "success", "time_to_complete": time_to_complete, "chef_id": chef.id, "total_cost": total_cost}


    # Списать ингредиенты с запасов
    def deduct_ingredients(self, recipe_name, quantity):
        recipe = self.get_recipe_by_name(recipe_name)
        if recipe:
            for ingredient_id, amount_needed in recipe.ingredients:
                ingredient = self.get_ingredient_by_id(ingredient_id)
                if ingredient:
                    total_needed = amount_needed * quantity
                    # Списываем ингредиенты с соответствующих складов
                    for warehouse in self.warehouses:
                        for index, (warehouse_ingredient_id, warehouse_amount) in enumerate(warehouse.ingredients):
                            if warehouse_ingredient_id == ingredient.id:
                                new_amount = warehouse_amount - total_needed
                                warehouse.ingredients[index] = (warehouse_ingredient_id, new_amount)
        return True
    # Расчет выручки
    def get_total_revenue(self):
        return sum(recipe.price * order["quantity"] for recipe in self.recipes for order in recipe.orders)
    

    #Получить информацию о загруженности сотрудников.
    def get_employee_loads(self):
        return [
            {"id": emp.id, "name": emp.name, "role": emp.role, "orders_in_queue": emp.get_load()}
             for emp in self.employees
    ]
    #Найти наименее загруженного сотрудника по роли.
    def get_least_loaded_employee(self, role):
        employees = [emp for emp in self.employees if emp.role == role]
        if not employees:
            return None
        return min(employees, key=lambda emp: emp.get_load())


    #Завершить заказ для указанного сотрудника
    def complete_order(self, employee_id):
        employee = next((emp for emp in self.employees if emp.id == employee_id), None)
        if not employee:
            return {"error": "Employee not found"}

        completed_order = employee.complete_order()
        if not completed_order:
            return {"error": "No orders to complete"}
    
        return {"status": "Order completed", "order": completed_order}

    #Сохраняет изменения в файл конфигурации.
    def save_changes(self):
        data = {
            "halls": [
                {
                    "id": hall.id,
                    "name": hall.name,
                    "tables": [
                        {"id": table.id, "status": table.status}
                        for table in hall.tables
                    ]
                }
                for hall in self.halls
            ],
            "ingredients": [
                {"id": ing.id, "name": ing.name, "unit": ing.unit} for ing in self.ingredients
            ],
            "recipes": [
                {
                    "id": recipe.id,
                    "name": recipe.name,
                    "complexity": recipe.complexity,
                    "price": recipe.price,
                    "ingredients": [
                        {"ingredient_id": ing_id, "amount": amount}
                        for ing_id, amount in recipe.ingredients
                    ]
                } for recipe in self.recipes
            ],
            "warehouses": [
                {
                    "id": warehouse.id,
                    "name": warehouse.name,
                    "ingredients": [
                        {"ingredient_id": ing_id, "amount": amount}
                        for ing_id, amount in warehouse.ingredients
                    ]
                } for warehouse in self.warehouses
            ],
            "employees": [
            {"id": emp.id, "name": emp.name, "role": emp.role, "performance": emp.performance}
            for emp in self.employees
        ]
        }
        with open(self.config_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


'''
# Использование класса
if __name__ == "__main__":
    db = Database("config_halls.json")
    a = RestaurantDatabase("config_menu.json")
    # Пример: Обновить статус стола
    hall_id = 1
    table_id = 2
    new_status = "occupied"
    
    if db.reserve_table(hall_id, table_id):
        print(f"Статус стола {table_id} в зале {hall_id} обновлен на '{new_status}'!")
        db.save_changes()  # Сохраняем изменения в файл
        a.save_changes()
        print(db.get_table(hall_id, table_id))
    else:
        print(f"Не удалось обновить статус стола {table_id} в зале {hall_id}.")
'''