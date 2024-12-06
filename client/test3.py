import tkinter as tk
from tkinter import ttk, messagebox
import requests
from concurrent.futures import ThreadPoolExecutor

API_BASE_URL = "http://127.0.0.1:5000"  # URL сервера


class RestaurantClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.geometry("900x600")

        # === Главное окно ===
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = ttk.Label(self.main_frame, text="Restaurant Management", font=("Arial", 24))
        self.title_label.pack(pady=10)

        self.info_frame = ttk.LabelFrame(self.main_frame, text="Current Statistics", padding="10")
        self.info_frame.pack(fill=tk.X, pady=10)

        self.hall_load_label = ttk.Label(self.info_frame, text="Hall Load: Loading...")
        self.hall_load_label.grid(row=0, column=0, padx=10, sticky="w")

        self.revenue_label = ttk.Label(self.info_frame, text="Total Revenue: Loading...")
        self.revenue_label.grid(row=1, column=0, padx=10, sticky="w")

        self.employee_load_label = ttk.Label(self.info_frame, text="Employee Load: Loading...")
        self.employee_load_label.grid(row=2, column=0, padx=10, sticky="w")

        # Кнопки действий
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=20)

        self.manage_table_button = ttk.Button(self.button_frame, text="Manage Table", command=self.manage_table_window)
        self.manage_table_button.grid(row=0, column=0, padx=10)

        self.create_order_button = ttk.Button(self.button_frame, text="Create Order", command=self.create_order_window)
        self.create_order_button.grid(row=0, column=1, padx=10)

        self.view_details_button = ttk.Button(self.button_frame, text="View Details", command=self.view_details_window)
        self.view_details_button.grid(row=0, column=2, padx=10)

        # Поле для отображения данных
        self.data_text = tk.Text(self.main_frame, wrap=tk.WORD, height=15)
        self.data_text.pack(fill=tk.BOTH, expand=True)

        # Запуск обновления данных через ThreadPoolExecutor
        self.executor = ThreadPoolExecutor(max_workers=5)  # Максимум 5 потоков
        self.start_update_task()

    # === Обновление данных ===
    def start_update_task(self):
        self.executor.submit(self.update_data_periodically)

    def update_data_periodically(self):
        while True:
            try:
                halls = self.get_data(f"{API_BASE_URL}/halls")
                employees = self.get_data(f"{API_BASE_URL}/employees")
                revenue = sum([hall.get("revenue", 0) for hall in halls])

                hall_load = ", ".join(
                    [f"{hall['name']}: {len([t for t in hall['tables'] if t['status'] == 'reserved'])}/{len(hall['tables'])}" for hall in halls]
                )
                employee_load = ", ".join(
                    [f"{emp['name']} ({emp['role']}): {emp['orders_in_queue']} orders" for emp in employees]
                )

                self.update_labels(hall_load, revenue, employee_load)
            except Exception as e:
                self.update_labels("Error", "Error", f"Error: {e}")

    def update_labels(self, hall_load, revenue, employee_load):
        self.hall_load_label.config(text=f"Hall Load: {hall_load}")
        self.revenue_label.config(text=f"Total Revenue: ${revenue}")
        self.employee_load_label.config(text=f"Employee Load: {employee_load}")

    def get_data(self, url):
        response = requests.get(url)
        response.raise_for_status()  # Поднимет исключение, если запрос завершился ошибкой
        return response.json()

    # === Управление столиком ===
    def manage_table_window(self):
        # Аналогично вашему коду, создание окна управления столиками
        pass

    # === Создание заказа ===
    def create_order_window(self):
        # Аналогично вашему коду, создание окна для заказов
        pass

    # === Детали состояния ===
    def view_details_window(self):
        messagebox.showinfo("Details", "Feature coming soon!")

    def close_executor(self):
        """Закрыть ThreadPoolExecutor при выходе."""
        self.executor.shutdown(wait=True)


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantClientApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_executor)  # Закрытие приложения корректно завершает потоки
    root.mainloop()
