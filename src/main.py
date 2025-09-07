from app import App


def main():
    model = "qwen3:0.6b"
    db_url = "postgresql://postgres:chinook@localhost:55000/chinook"
    App(model, db_url)


if __name__ == "__main__":
    main()
