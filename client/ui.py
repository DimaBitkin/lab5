import tkinter as tk
from api import get_restaurants, reserve_table

def show_restaurants():
    restaurants = get_restaurants()
    for restaurant in restaurants:
        print(f"{restaurant['id']}. {restaurant['name']} - {restaurant['location']}")

def reserve_table_ui():
    hall_id = int(input("Enter hall id: "))
    table_id = int(input("Enter table id: "))
    result = reserve_table(hall_id, table_id)
    print(result["status"])

# Основное окно
root = tk.Tk()
root.title("Restaurant Booking System")

btn_show_restaurants = tk.Button(root, text="Show Restaurants", command=show_restaurants)
btn_show_restaurants.pack()

btn_reserve_table = tk.Button(root, text="Reserve Table", command=reserve_table_ui)
btn_reserve_table.pack()

root.mainloop()
