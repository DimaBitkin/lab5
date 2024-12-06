from flask import Flask


# Инициализация Flask
app = Flask(__name__)

# Настройка менеджера процессов
def create_app():
    from routes import api_blueprint  # Импортируем после создания приложения, чтобы избежать кругового импорта
    from database import RestaurantDatabase
    from process_manager import ProcessManager
    # Настройки базы данных
    db = RestaurantDatabase("server/config.json")

    # Настройка менеджера процессов
    process_manager = ProcessManager(db)
    process_manager.start()

    # Подключение маршрутов
    app.register_blueprint(api_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
