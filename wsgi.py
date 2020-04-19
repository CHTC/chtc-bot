from web.app import create_app

app = create_app(config="heroku")

if __name__ == "__main__":
    app.run()
