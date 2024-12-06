import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

# Константы для API
API_BASE_URL = "http://127.0.0.1:5000"

class RestaurantClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.geometry("800x600")

        # Создание основного фрейма
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        self.title_label = ttk.Label(self.main_frame, text="Restaurant Management", font=("Arial", 24))
        self.title_label.pack(pady=10)

        # Кнопки действий
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=20)

        self.halls_button = ttk.Button(self.button_frame, text="View Halls", command=self.view_halls)
        self.halls_button.grid(row=0, column=0, padx=10)

        self.reservation_button = ttk.Button(self.button_frame, text="Reserve Table", command=self.reserve_table_window)
        self.reservation_button.grid(row=0, column=1, padx=10)

        self.orders_button = ttk.Button(self.button_frame, text="Create Order", command=self.create_order_window)
        self.orders_button.grid(row=0, column=2, padx=10)

        self.warehouse_button = ttk.Button(self.button_frame, text="View Warehouse", command=self.view_warehouse_window)
        self.warehouse_button.grid(row=0, column=3, padx=10)

        # Поле для отображения данных
        self.data_text = tk.Text(self.main_frame, wrap=tk.WORD, height=20)
        self.data_text.pack(fill=tk.BOTH, expand=True)

        # Запуск потока для обновления данных
        self.start_update_thread()

    def clear_data_text(self):
        """Очистить текстовое поле."""
        self.data_text.delete(1.0, tk.END)

    def display_data(self, data):
        """Отобразить данные в текстовом поле."""
        self.clear_data_text()
        self.data_text.insert(tk.END, data)

    # ==== Обновление данных ====
    def start_update_thread(self):
        """Запустить поток для периодического обновления данных."""
        threading.Thread(target=self.update_data_periodically, daemon=True).start()

    def update_data_periodically(self):
        """Периодически обновлять данные о загруженности залов, сотрудников и складов."""
        while True:
            try:
                response = requests.get(f"{API_BASE_URL}/employees")
                response.raise_for_status()
                employees = response.json()
                formatted_data = "\n".join([f"{emp['name']} ({emp['role']}): {emp['orders_in_queue']} orders in queue" for emp in employees])
                self.display_data(formatted_data)
            except requests.RequestException:
                self.display_data("Error: Unable to fetch updated data.")
            finally:
                self.root.after(5000)  # Обновление каждые 5 секунд

    # ==== API Взаимодействия ====

    def view_halls(self):
        """Получить и отобразить список залов."""
        threading.Thread(target=self.fetch_halls, daemon=True).start()

    def fetch_halls(self):
        try:
            response = requests.get(f"{API_BASE_URL}/halls")
            response.raise_for_status()
            halls = response.json()
            formatted_data = "\n".join([f"ID: {hall['id']}, Name: {hall['name']}" for hall in halls])
            self.display_data(formatted_data)
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch halls: {e}")

    def reserve_table_window(self):
        """Окно для бронирования столика."""
        reservation_window = tk.Toplevel(self.root)
        reservation_window.title("Reserve Table")

        ttk.Label(reservation_window, text="Hall ID:").grid(row=0, column=0, padx=10, pady=5)
        hall_id_entry = ttk.Entry(reservation_window)
        hall_id_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(reservation_window, text="Table ID:").grid(row=1, column=0, padx=10, pady=5)
        table_id_entry = ttk.Entry(reservation_window)
        table_id_entry.grid(row=1, column=1, padx=10, pady=5)

        def reserve_table():
            hall_id = hall_id_entry.get()
            table_id = table_id_entry.get()
            threading.Thread(target=self.reserve_table_api, args=(hall_id, table_id), daemon=True).start()

        reserve_button = ttk.Button(reservation_window, text="Reserve", command=reserve_table)
        reserve_button.grid(row=2, columnspan=2, pady=10)

    def reserve_table_api(self, hall_id, table_id):
        try:
            response = requests.post(f"{API_BASE_URL}/halls/{hall_id}/tables/{table_id}/reserve")
            if response.status_code == 200:
                messagebox.showinfo("Success", "Table reserved successfully!")
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to reserve table"))
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to reserve table: {e}")

    def create_order_window(self):
        """Окно для создания заказа."""
        order_window = tk.Toplevel(self.root)
        order_window.title("Create Order")

        ttk.Label(order_window, text="Recipe Name:").grid(row=0, column=0, padx=10, pady=5)
        recipe_entry = ttk.Entry(order_window)
        recipe_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(order_window, text="Quantity:").grid(row=1, column=0, padx=10, pady=5)
        quantity_entry = ttk.Entry(order_window)
        quantity_entry.grid(row=1, column=1, padx=10, pady=5)

        def create_order():
            recipe_name = recipe_entry.get()
            quantity = quantity_entry.get()
            threading.Thread(target=self.create_order_api, args=(recipe_name, quantity), daemon=True).start()

        order_button = ttk.Button(order_window, text="Create Order", command=create_order)
        order_button.grid(row=2, columnspan=2, pady=10)

    def create_order_api(self, recipe_name, quantity):
        try:
            response = requests.post(f"{API_BASE_URL}/orders", json={"recipe_name": recipe_name, "quantity": int(quantity)})
            if response.status_code == 200:
                result = response.json()
                messagebox.showinfo("Success", f"Order created! Estimated time: {result['time_to_complete']} mins")
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to create order"))
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to create order: {e}")

    def view_warehouse_window(self):
        """Окно для отображения склада."""
        threading.Thread(target=self.fetch_warehouse, daemon=True).start()

    def fetch_warehouse(self):
        try:
            response = requests.get(f"{API_BASE_URL}/warehouses/1")
            response.raise_for_status()
            warehouse = response.json()
            formatted_data = f"Warehouse Name: {warehouse['name']}\n" + "\n".join(
                [f"{ing['ingredient_id']}: {ing['amount']}" for ing in warehouse["ingredients"]]
            )
            self.display_data(formatted_data)
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch warehouse: {e}")


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantClientApp(root)
    root.mainloop()
