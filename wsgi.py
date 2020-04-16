from web.app import create_app

app = create_app(config="Heroku")

if __name__ == "__main__":
    app.run()
