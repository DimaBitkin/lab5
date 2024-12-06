import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_BASE_URL = "http://127.0.0.1:5000"  # URL сервера

class RestaurantClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.geometry("800x600")

        # Инициализация переменных
        self.halls = []
        self.tables = []
        self.selected_hall = None
        self.selected_table = None
        self.menu = []

        # Начальный экран с кнопкой "Войти"
        self.login_screen()

    def login_screen(self):
        """Начальный экран с кнопкой Войти"""
        self.clear_window()

        self.title_label = ttk.Label(self.root, text="Welcome to Restaurant Management System", font=("Arial", 18))
        self.title_label.pack(pady=30)

        self.login_button = ttk.Button(self.root, text="Login", command=self.main_screen)
        self.login_button.pack(pady=20)

    def clear_window(self):
        """Очистка окна перед открытием нового"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_screen(self):
        """Главный экран с кнопками для управления столиками и заказами"""
        self.clear_window()

        # Загружаем данные с сервера
        self.load_data()

        # Заголовок главного экрана
        self.title_label = ttk.Label(self.root, text="Main Menu", font=("Arial", 18))
        self.title_label.pack(pady=30)

        # Кнопки для действий
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=20)

        # Кнопки
        self.manage_table_button = ttk.Button(self.button_frame, text="Manage Table", command=self.manage_table_window)
        self.manage_table_button.grid(row=0, column=0, padx=10)

        self.create_order_button = ttk.Button(self.button_frame, text="Create Order", command=self.create_order_window)
        self.create_order_button.grid(row=0, column=1, padx=10)

        self.view_inventory_button = ttk.Button(self.button_frame, text="View Inventory", command=self.view_inventory_window)
        self.view_inventory_button.grid(row=0, column=2, padx=10)

        # Информация о текущей загрузке
        self.info_frame = ttk.LabelFrame(self.root, text="Current Statistics", padding="10")
        self.info_frame.pack(fill=tk.X, pady=10)

        self.hall_load_label = ttk.Label(self.info_frame, text="Hall Load: Loading...")
        self.hall_load_label.grid(row=0, column=0, padx=10, sticky="w")

        self.employee_load_label = ttk.Label(self.info_frame, text="Employee Load: Loading...")
        self.employee_load_label.grid(row=1, column=0, padx=10, sticky="w")

        self.update_data()

    def load_data(self):
        """Загрузка данных с сервера"""
        try:
            self.halls = requests.get(f"{API_BASE_URL}/halls").json()
            self.menu = requests.get(f"{API_BASE_URL}/recipes").json()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            return

    def update_data(self):
        """Обновление данных о залах и сотрудниках"""
        try:
            halls = requests.get(f"{API_BASE_URL}/halls").json()
            employees = requests.get(f"{API_BASE_URL}/employees").json()

            hall_load = ", ".join([f"{hall['name']}: {len([t for t in hall['tables'] if t['status'] == 'reserved'])}/{len(hall['tables'])}" for hall in halls])
            employee_load = ", ".join([f"{emp['name']} ({emp['role']}): {emp['orders_in_queue']} orders" for emp in employees])

            self.hall_load_label.config(text=f"Hall Load: {hall_load}")
            self.employee_load_label.config(text=f"Employee Load: {employee_load}")
        except Exception as e:
            self.hall_load_label.config(text="Hall Load: Error")
            self.employee_load_label.config(text="Employee Load: Error")

        self.root.after(5000, self.update_data)  # Обновление каждые 5 секунд

    def manage_table_window(self):
        """Окно для управления столиками"""
        window = tk.Toplevel(self.root)
        window.title("Manage Table")
        window.geometry("400x250")

        ttk.Label(window, text="Select Hall:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        hall_combo = ttk.Combobox(window, state="readonly")
        hall_combo.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(window, text="Select Table:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        table_combo = ttk.Combobox(window, state="readonly")
        table_combo.grid(row=1, column=1, padx=10, pady=5)

        def load_halls():
            hall_combo["values"] = [f"{hall['id']} - {hall['name']}" for hall in self.halls]
            hall_combo.set('')

        def load_tables(event):
            hall_id = hall_combo.get().split(" - ")[0]
            hall = next((h for h in self.halls if h["id"] == int(hall_id)), None)
            if hall:
                table_combo["values"] = [f"{t['id']} ({t['status']})" for t in hall["tables"]]
                table_combo.set('')

        hall_combo.bind("<<ComboboxSelected>>", load_tables)
        load_halls()

        def sit_down():
            hall_id = int(hall_combo.get().split(" - ")[0])
            table_id = int(table_combo.get().split(" ")[0])
            try:
                response = requests.post(f"{API_BASE_URL}/halls/{hall_id}/tables/{table_id}/reserve")
                if response.status_code == 200:
                    messagebox.showinfo("Success", "You have reserved the table!")
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
                else:
                    messagebox.showerror("Error", response.json().get("error", "Failed to release the table."))
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        ttk.Button(window, text="Sit Down", command=sit_down).grid(row=2, column=0, padx=10, pady=20)
        ttk.Button(window, text="Stand Up", command=stand_up).grid(row=2, column=1, padx=10, pady=20)

    def create_order_window(self):
        """Окно для создания заказа"""
        window = tk.Toplevel(self.root)
        window.title("Create Order")
        window.geometry("400x300")

        ttk.Label(window, text="Select Hall:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        hall_combo = ttk.Combobox(window, state="readonly")
        hall_combo.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(window, text="Select Table:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        table_combo = ttk.Combobox(window, state="readonly")
        table_combo.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(window, text="Select Recipe:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        recipe_combo = ttk.Combobox(window, state="readonly")
        recipe_combo["values"] = [recipe['name'] for recipe in self.menu]
        recipe_combo.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(window, text="Quantity:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        quantity_entry = ttk.Entry(window)
        quantity_entry.grid(row=3, column=1, padx=10, pady=5)

        def place_order():
            hall_id = int(hall_combo.get().split(" - ")[0])
            table_id = int(table_combo.get().split(" ")[0])
            recipe_name = recipe_combo.get()
            quantity = quantity_entry.get()

            if not hall_id or not table_id or not recipe_name or not quantity:
                messagebox.showerror("Error", "Please fill all fields.")
                return

            try:
                response = requests.post(f"{API_BASE_URL}/orders", json={
                    "hall_id": hall_id,
                    "table_id": table_id,
                    "recipe_name": recipe_name,
                    "quantity": int(quantity)
                })
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Order placed successfully!")
                else:
                    messagebox.showerror("Error", response.json().get("error", "Failed to place the order."))
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        ttk.Button(window, text="Place Order", command=place_order).grid(row=4, columnspan=2, pady=20)

    def view_inventory_window(self):
        """Окно для отображения состояния холодильников"""
        window = tk.Toplevel(self.root)
        window.title("View Inventory")
        window.geometry("400x300")

        try:
            warehouses = requests.get(f"{API_BASE_URL}/warehouses").json()
            for warehouse in warehouses:
                ttk.Label(window, text=f"{warehouse['name']}").pack(pady=10)
                for ingredient in warehouse['ingredients']:
                    ttk.Label(window, text=f"{ingredient['ingredient_id']} - {ingredient['amount']}").pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {e}")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantClientApp(root)
    root.mainloop()
