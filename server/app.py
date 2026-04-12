import importlib

create_app = importlib.import_module("app").create_app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)