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

        # Запуск потока обновления данных
        self.executor = ThreadPoolExecutor(max_workers=5)  # Максимум 5 потоков
        self.halls = []
        self.employees = []
        self.revenue = 0

    # === Обновление данных по событию ===
    def update_data(self):
        """Обновить данные о залах, сотрудниках и выручке"""
        self.executor.submit(self.fetch_data)

    def fetch_data(self):
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
        window = tk.Toplevel(self.root)
        window.title("Manage Table")
        window.geometry("400x200")

        ttk.Label(window, text="Select Hall:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        hall_combo = ttk.Combobox(window, state="readonly")
        hall_combo.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(window, text="Select Table:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        table_combo = ttk.Combobox(window, state="readonly")
        table_combo.grid(row=1, column=1, padx=10, pady=5)

        def load_halls():
            try:
                halls = self.get_data(f"{API_BASE_URL}/halls")
                hall_combo["values"] = [f"{hall['id']} - {hall['name']}" for hall in halls]

                def load_tables(event):
                    hall_id = hall_combo.get().split(" - ")[0]
                    hall = next((h for h in halls if h["id"] == int(hall_id)), None)
                    if hall:
                        table_combo["values"] = [f"{t['id']} ({t['status']})" for t in hall["tables"]]

                hall_combo.bind("<<ComboboxSelected>>", load_tables)
            except Exception:
                messagebox.showerror("Error", "Failed to load halls or tables.")

        load_halls()

        def sit_down():
            hall_id = int(hall_combo.get().split(" - ")[0])
            table_id = int(table_combo.get().split(" ")[0])
            try:
                response = requests.post(f"{API_BASE_URL}/halls/{hall_id}/tables/{table_id}/reserve")
                if response.status_code == 200:
                    messagebox.showinfo("Success", "You have reserved the table!")
                    self.update_data()  # Обновляем данные после изменения
                else:
                    messagebox.showerror("Error", response.json().get("error", "Failed to reserve the table."))
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        def stand_up():
            hall_id = int(hall_combo.get().split(" - ")[0])
            table_id = int(table_combo.get().split(" ")[0])
            try:
                response = requests.post(f"{API_BASE_URL}/halls/{hall_id}/tables/{table_id}/release")
                if response.status_code == 200:
                    messagebox.showinfo("Success", "You have released the table!")
                    self.update_data()  # Обновляем данные после изменения
                else:
                    messagebox.showerror("Error", response.json().get("error", "Failed to release the table."))
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        ttk.Button(window, text="Sit Down", command=sit_down).grid(row=2, column=0, padx=10, pady=20)
        ttk.Button(window, text="Stand Up", command=stand_up).grid(row=2, column=1, padx=10, pady=20)

    # === Создание заказа ===
    def create_order_window(self):
        window = tk.Toplevel(self.root)
        window.title("Create Order")
        window.geometry("400x300")

        ttk.Label(window, text="Select Table:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        table_entry = ttk.Entry(window)
        table_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(window, text="Recipe Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        recipe_entry = ttk.Entry(window)
        recipe_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(window, text="Quantity:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        quantity_entry = ttk.Entry(window)
        quantity_entry.grid(row=2, column=1, padx=10, pady=5)

        def place_order():
            table_id = table_entry.get()
            recipe_name = recipe_entry.get()
            quantity = quantity_entry.get()
            try:
                response = requests.post(f"{API_BASE_URL}/orders", json={
                    "table_id": int(table_id),
                    "recipe_name": recipe_name,
                    "quantity": int(quantity)
                })
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Order placed successfully!")
                    self.update_data()  # Обновляем данные после изменения
                else:
                    messagebox.showerror("Error", response.json().get("error", "Failed to place the order."))
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        ttk.Button(window, text="Place Order", command=place_order).grid(row=3, columnspan=2, pady=20)

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
