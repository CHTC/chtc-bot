import os

from web.app import create_app

app = create_app(config=os.environ["CONFIG"])

if __name__ == "__main__":
    app.run()
