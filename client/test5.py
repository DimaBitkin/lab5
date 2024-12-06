import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_BASE_URL = "http://127.0.0.1:5000"  # URL сервера


class RestaurantClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.geometry("500x400")

        # Инициализация переменных
        self.halls = []
        self.tables = []
        self.selected_hall = None
        self.selected_table = None

        # Начальный экран с кнопкой "Войти"
        self.login_screen()

    def login_screen(self):
        """Начальный экран с кнопкой Войти"""
        self.clear_window()

        self.title_label = ttk.Label(self.root, text="Welcome to Restaurant Management System", font=("Arial", 18))
        self.title_label.pack(pady=30)

        self.login_button = ttk.Button(self.root, text="Login", command=self.select_hall_screen)
        self.login_button.pack(pady=20)

    def clear_window(self):
        """Очистка окна перед открытием нового"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def select_hall_screen(self):
        """Экран выбора зала и столика"""
        self.clear_window()

        # Загружаем залы с сервера
        try:
            self.halls = requests.get(f"{API_BASE_URL}/halls").json()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load halls: {e}")
            return

        # Заголовок
        self.title_label = ttk.Label(self.root, text="Select Hall and Table", font=("Arial", 18))
        self.title_label.pack(pady=20)

        # Выпадающий список выбора зала
        self.hall_combo = ttk.Combobox(self.root, state="readonly")
        self.hall_combo["values"] = [f"{hall['id']} - {hall['name']}" for hall in self.halls]
        self.hall_combo.pack(pady=10)

        # Выпадающий список выбора столика
        self.table_combo = ttk.Combobox(self.root, state="readonly")
        self.table_combo.pack(pady=10)

        def load_tables(event):
            hall_id = int(self.hall_combo.get().split(" - ")[0])
            self.selected_hall = next((hall for hall in self.halls if hall['id'] == hall_id), None)

            if self.selected_hall:
                self.tables = self.selected_hall["tables"]
                self.table_combo["values"] = [f"Table {table['id']} ({table['status']})" for table in self.tables]
                self.table_combo.set('')

        self.hall_combo.bind("<<ComboboxSelected>>", load_tables)

        # Кнопка "Сесть"
        self.sit_button = ttk.Button(self.root, text="Sit Down", command=self.sit_down)
        self.sit_button.pack(pady=20)

        # Кнопка "Создать заказ"
        self.create_order_button = ttk.Button(self.root, text="Create Order", command=self.create_order_window)
        self.create_order_button.pack(pady=10)

    def sit_down(self):
        """Функция для бронирования столика"""
        try:
            table_id = int(self.table_combo.get().split(" ")[1])  # Получаем номер столика из выпадающего меню
            if not self.selected_hall or not table_id:
                raise ValueError("Please select a table and hall.")
            
            # Отправляем запрос на сервер для бронирования
            response = requests.post(f"{API_BASE_URL}/halls/{self.selected_hall['id']}/tables/{table_id}/reserve")

            if response.status_code == 200:
                messagebox.showinfo("Success", "You have reserved the table!")
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to reserve the table."))
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def create_order_window(self):
        """Окно для создания заказа"""
        self.clear_window()

        # Заголовок
        self.title_label = ttk.Label(self.root, text="Create Order", font=("Arial", 18))
        self.title_label.pack(pady=20)

        # Загружаем меню с сервера
        try:
            recipes = requests.get(f"{API_BASE_URL}/recipes").json()
            recipe_names = [recipe['name'] for recipe in recipes]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recipes: {e}")
            return

        # Выпадающий список для выбора блюда
        self.recipe_combo = ttk.Combobox(self.root, state="readonly", values=recipe_names)
        self.recipe_combo.pack(pady=10)

        # Поле для выбора количества
        self.quantity_label = ttk.Label(self.root, text="Quantity:")
        self.quantity_label.pack(pady=5)
        self.quantity_entry = ttk.Entry(self.root)
        self.quantity_entry.pack(pady=5)

        # Кнопка для оформления заказа
        self.order_button = ttk.Button(self.root, text="Place Order", command=self.place_order)
        self.order_button.pack(pady=20)

    def place_order(self):
        """Функция для размещения заказа"""
        table_id = int(self.table_combo.get().split(" ")[1])
        recipe_name = self.recipe_combo.get()
        quantity = self.quantity_entry.get()

        if not table_id or not recipe_name or not quantity:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        try:
            response = requests.post(f"{API_BASE_URL}/orders", json={
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

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantClientApp(root)
    root.mainloop()
