import threading
import time
import random
from queue import PriorityQueue
from database import RestaurantDatabase

class Order:
    def __init__(self, order_id, recipe_name, quantity, time_to_complete, stage="chef"):
        self.order_id = order_id
        self.recipe_name = recipe_name
        self.quantity = quantity
        self.time_to_complete = time_to_complete
        self.stage = stage  # chef -> waiter

    def __lt__(self, other):
        return self.time_to_complete < other.time_to_complete


class ProcessManager:
    def __init__(self, database: RestaurantDatabase):
        self.database = database
        self.lock = threading.Lock()
        self.orders_queue = PriorityQueue()
        self.active_threads = []

    def add_order(self, recipe_name, quantity):
        with self.lock:
            result = self.database.process_order(recipe_name, quantity)
            if "error" in result:
                return result

            noise_factor = random.uniform(0.8, 1.2)  # Добавляем шумовую величину
            time_to_complete = result["time_to_complete"] * noise_factor

            order = Order(
                order_id=len(self.active_threads) + 1,
                recipe_name=recipe_name,
                quantity=quantity,
                time_to_complete=time_to_complete,
            )
            self.orders_queue.put(order)
            print(f"Заказ {order.order_id} добавлен в очередь.")
            return {"status": "Order added to the queue", "order_id": order.order_id}

    def process_orders(self):
        while True:
            if not self.orders_queue.empty():
                with self.lock:
                    order = self.orders_queue.get()
                self.assign_order_to_employee(order)

    def assign_order_to_employee(self, order):
        employee_role = "chef" if order.stage == "chef" else "waiter"
        employee = self.database.get_least_loaded_employee(employee_role)
        if not employee:
            print(f"Нет доступных сотрудников с ролью {employee_role}.")
            return

        print(f"Назначаем заказ {order.order_id} сотруднику {employee.name} ({employee.role}).")
        employee.assign_order(order)

        thread = threading.Thread(target=self.complete_order, args=(employee, order))
        thread.start()
        self.active_threads.append(thread)

    def complete_order(self, employee, order):
        print(f"Сотрудник {employee.name} начал выполнение заказа {order.order_id} (этап: {order.stage}).")
        time.sleep(order.time_to_complete)
        with self.lock:
            completed_order = employee.complete_order()
            if completed_order:
                if order.stage == "chef":
                    print(f"Повар {employee.name} завершил заказ {order.order_id}. Передаем официанту.")
                    order.stage = "waiter"
                    self.orders_queue.put(order)
                elif order.stage == "waiter":
                    print(f"Официант {employee.name} завершил заказ {order.order_id}.")
            else:
                print(f"Ошибка: Заказ {order.order_id} не найден в стеке сотрудника {employee.name}.")

    def monitor_threads(self):
        while True:
            with self.lock:
                self.active_threads = [t for t in self.active_threads if t.is_alive()]
            time.sleep(1)

    def start(self):
        threading.Thread(target=self.process_orders, daemon=True).start()
        threading.Thread(target=self.monitor_threads, daemon=True).start()
