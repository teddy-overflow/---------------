from pathlib import Path

from src.config import load_config


def main():
    """Запускает программу и выводит настройки."""
    project_dir = Path(__file__).resolve().parent.parent
    config_path = project_dir / "config.xml"

    try:
        config = load_config(config_path)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    print("Конфигурация программы:")
    print("-----------------------")

    for key, value in config.items():
        print(f"{key} = {value}")


if __name__ == "__main__":
    main()