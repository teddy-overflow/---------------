
from pathlib import Path

from src.config import load_config
from src.nuget import fetch_direct_dependencies


def main():
    """Запускает программу и выводит прямые зависимости пакета."""
    project_dir = Path(__file__).resolve().parent.parent
    config_path = project_dir / "config.xml"

    try:
        config = load_config(config_path)

        print(
            f"Пакет: {config['package_name']}"
        )
        print(f"Версия: {config['version']}")
        print("\nПолучение прямых зависимостей...")

        dependencies = fetch_direct_dependencies(
            config["repository"],
            config["package_name"],
            config["version"],
        )

    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    if not dependencies:
        print("Прямые зависимости отсутствуют.")
        return

    print("\nПрямые зависимости:")

    for dependency in dependencies:
        print(
            f"- {dependency['name']}: "
            f"{dependency['version']}"
        )

    print(f"\nВсего зависимостей: {len(dependencies)}")


if __name__ == "__main__":
    main()
