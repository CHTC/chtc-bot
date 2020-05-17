from web.app import create_app

app = create_app(config="testing")

if __name__ == "__main__":
    app.run()
