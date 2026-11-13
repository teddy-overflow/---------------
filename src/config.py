from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


def get_value(root, tag):
    """Получает обязательное значение из XML."""
    element = root.find(tag)

    if element is None:
        raise ValueError(f"Отсутствует параметр: {tag}")

    if element.text is None or not element.text.strip():
        raise ValueError(f"Параметр {tag} не может быть пустым")

    return element.text.strip()


def validate_boolean(value, name):
    """Проверяет, что значение является true или false."""
    if value.lower() not in ("true", "false"):
        raise ValueError(
            f"Параметр {name} должен быть true или false"
        )

    return value.lower() == "true"


def load_config(file_path):
    """Загружает и проверяет настройки из XML."""
    try:
        tree = ET.parse(file_path)
    except ET.ParseError as error:
        raise ValueError(f"Ошибка XML: {error}") from error
    except OSError as error:
        raise ValueError(f"Не удалось открыть файл: {error}") from error

    root = tree.getroot()

    if root.tag != "configuration":
        raise ValueError("Корневой тег должен быть configuration")

    package_name = get_value(root, "package_name")
    repository = get_value(root, "repository")
    test_mode = validate_boolean(
        get_value(root, "test_mode"), "test_mode"
    )
    version = get_value(root, "version")
    output_file = get_value(root, "output_file")
    ascii_tree = validate_boolean(
        get_value(root, "ascii_tree"), "ascii_tree"
    )
    max_depth_text = get_value(root, "max_depth")

    if test_mode:
        if not Path(repository).is_file():
            raise ValueError(
                "В тестовом режиме repository должен быть "
                "путём к существующему файлу"
            )
    else:
        parsed_url = urlparse(repository)

        if parsed_url.scheme not in ("http", "https"):
            raise ValueError(
                "Repository должен быть URL с http или https"
            )

        if not parsed_url.netloc:
            raise ValueError("Некорректный URL репозитория")

    output_path = Path(output_file)

    if output_path.name != output_file:
        raise ValueError(
            "output_file должен содержать только имя файла"
        )

    if output_path.suffix.lower() != ".svg":
        raise ValueError("output_file должен иметь расширение .svg")

    try:
        max_depth = int(max_depth_text)
    except ValueError as error:
        raise ValueError(
            "max_depth должен быть целым числом"
        ) from error

    if max_depth < 1:
        raise ValueError("max_depth должен быть не меньше 1")

    return {
        "package_name": package_name,
        "repository": repository,
        "test_mode": test_mode,
        "version": version,
        "output_file": output_file,
        "ascii_tree": ascii_tree,
        "max_depth": max_depth,
    }