import requests

BASE_URL = "http://127.0.0.1:5000"

def list_restaurants():
    response = requests.get(f"{BASE_URL}/restaurants")
    response.encoding = 'utf-8'
    restaurants = response.json()
    print("\nList of restaurants:")
    for r in restaurants:
        print(f"ID: {r['id']}, Name: {r['name']}, Location: {r['location']}, Revenue: {r['revenue']}")
    return restaurants

def view_restaurant(restaurant_id):
    response = requests.get(f"{BASE_URL}/restaurant/{restaurant_id}")
    response.encoding = 'utf-8'
    restaurant = response.json()

    print(f"\nRestaurant: {restaurant['restaurant']['name']}")
    print(f"Location: {restaurant['restaurant']['location']}")
    print(f"Revenue: {restaurant['restaurant']['revenue']}")

    print("\nHalls:")
    for hall in restaurant["halls"]:
        print(f"  {hall['name']} (Capacity: {hall['capacity']})")

    print("\nMenu:")
    for item in restaurant["menu"]:
        print(f"  {item['name']} - ${item['price']}")

    print("\nEmployees:")
    for employee in restaurant["employees"]:
        print(f"  {employee['name']} ({employee['role']}, Performance: {employee['performance']})")

    print("\nWarehouse:")
    for product in restaurant["warehouses"]:
        print(f"  {product['product_name']} - {product['quantity']} units")

def reserve_table():
    table_id = int(input("\nEnter Table ID to reserve: "))
    response = requests.post(f"{BASE_URL}/reserve_table", json={"table_id": table_id})
    response.encoding = 'utf-8'
    result = response.json()
    if result["status"] == "success":
        print("Table successfully reserved!")
    else:
        print("Error:", result["message"])

def main():
    while True:
        print("\nMenu:")
        print("1. View list of restaurants")
        print("2. Select a restaurant")
        print("3. Reserve a table")
        print("4. Exit")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            list_restaurants()
        elif choice == "2":
            restaurant_id = int(input("Enter Restaurant ID: "))
            view_restaurant(restaurant_id)
        elif choice == "3":
            reserve_table()
        elif choice == "4":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
