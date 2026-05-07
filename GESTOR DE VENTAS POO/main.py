from interface.main import App
from config.database import DatabaseConnection

def main():
    try:
        # Conexión BD
        db = DatabaseConnection()
        db.connect()

        # Ejecutar app
        app = App()
        app.mainloop()

    except Exception as e:
        print(f"Error del sistema: {e}")

    finally:
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    main()