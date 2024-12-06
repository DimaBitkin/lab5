import threading
import time
from queue import PriorityQueue
from database import RestaurantDatabase


class Order:
    def __init__(self, order_id, recipe_name, quantity, time_to_complete):
        self.order_id = order_id
        self.recipe_name = recipe_name
        self.quantity = quantity
        self.time_to_complete = time_to_complete

    def __lt__(self, other):
        """Для приоритезации заказов по времени выполнения."""
        return self.time_to_complete < other.time_to_complete


class ProcessManager:
    def __init__(self, database: RestaurantDatabase):
        self.database = database
        self.lock = threading.Lock()
        self.orders_queue = PriorityQueue()  # Очередь заказов по приоритету (время выполнения)
        self.active_threads = []

    def add_order(self, recipe_name, quantity):
        """Добавить заказ в очередь."""
        with self.lock:
            result = self.database.process_order(recipe_name, quantity)
            if "error" in result:
                return result

            order = Order(
                order_id=len(self.active_threads) + 1,  # Уникальный ID заказа
                recipe_name=recipe_name,
                quantity=quantity,
                time_to_complete=result["time_to_complete"]
            )
            self.orders_queue.put(order)
            print(f"Заказ {order.order_id} добавлен в очередь.")
            return {"status": "Order added to the queue", "order_id": order.order_id}

    def process_orders(self):
        """Обработать заказы из очереди."""
        while True:
            if not self.orders_queue.empty():
                with self.lock:
                    order = self.orders_queue.get()
                self.assign_order_to_employee(order)

    def assign_order_to_employee(self, order):
        """Назначить заказ на наименее загруженного сотрудника."""
        chef = self.database.get_least_loaded_employee("chef")
        if not chef:
            print("Нет доступных поваров.")
            return

        print(f"Назначаем заказ {order.order_id} повару {chef.name}.")
        chef.assign_order(order)

        thread = threading.Thread(target=self.complete_order, args=(chef, order))
        thread.start()
        self.active_threads.append(thread)

    def complete_order(self, employee, order):
        """Завершить выполнение заказа."""
        print(f"Повар {employee.name} начал выполнение заказа {order.order_id}.")
        time.sleep(order.time_to_complete)  # Симуляция времени выполнения

        # После выполнения заказа передаем его официанту
        if order.recipe_name in ["Burger", "Fries"]:  # Пример фильтрации по блюдам
            self.pass_to_waiter(order)
        else:
            with self.lock:
                completed_order = employee.complete_order()
                if completed_order:
                    print(f"Заказ {order.order_id} выполнен поваром {employee.name}.")
                else:
                    print(f"Ошибка: Заказ {order.order_id} не найден в стеке повара.")

    def pass_to_waiter(self, order):
        """Передаем заказ официанту."""
        waiter = self.database.get_least_loaded_employee("waiter")
        if waiter:
            print(f"Заказ {order.order_id} передан официанту {waiter.name}.")
            waiter.assign_order(order)
            self.notify_order_completed(order)

    def notify_order_completed(self, order):
        """Уведомление о завершении заказа."""
        print(f"Заказ {order.order_id} завершен и передан клиенту.")

    def monitor_threads(self):
        """Мониторинг выполнения потоков."""
        while True:
            with self.lock:
                self.active_threads = [t for t in self.active_threads if t.is_alive()]
            time.sleep(1)

    def start(self):
        """Запустить обработку заказов."""
        threading.Thread(target=self.process_orders, daemon=True).start()
        threading.Thread(target=self.monitor_threads, daemon=True).start()
