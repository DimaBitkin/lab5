import requests

SERVER_URL = "http://localhost:5000"  # Укажите адрес сервера

def get_restaurants():
    response = requests.get(f"{SERVER_URL}/halls")
    return response.json()

def get_hall_by_id(hall_id):
    response = requests.get(f"{SERVER_URL}/halls/{hall_id}")
    return response.json()

def reserve_table(hall_id, table_id):
    response = requests.post(f"{SERVER_URL}/halls/{hall_id}/tables/{table_id}/reserve")
    return response.json()

def get_menu(restaurant_id):
    response = requests.get(f"{SERVER_URL}/restaurants/{restaurant_id}/menu")
    return response.json()

def create_order(order_data):
    response = requests.post(f"{SERVER_URL}/orders", json=order_data)
    return response.json()
