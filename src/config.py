
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


MIN_MAX_DEPTH = 1


def get_value(root, tag):
    """Получает обязательное значение из XML."""
    element = root.find(tag)

    if element is None or element.text is None:
        raise ValueError(f"Отсутствует параметр: {tag}")

    value = element.text.strip()

    if not value:
        raise ValueError(f"Параметр {tag} не может быть пустым")

    return value


def validate_boolean(value, name):
    """Проверяет, что значение является true или false."""
    normalized_value = value.lower()

    if normalized_value not in ("true", "false"):
        raise ValueError(
            f"Параметр {name} должен быть true или false"
        )

    return normalized_value == "true"


def validate_repository(repository, test_mode):
    """Проверяет путь к тестовому файлу или URL репозитория."""
    if test_mode:
        if not Path(repository).is_file():
            raise ValueError(
                "В тестовом режиме repository должен быть "
                "путём к существующему файлу"
            )
        return

    parsed_url = urlparse(repository)

    if parsed_url.scheme not in ("http", "https"):
        raise ValueError(
            "Repository должен быть URL с http или https"
        )

    if not parsed_url.netloc:
        raise ValueError("Некорректный URL репозитория")


def validate_output_file(output_file):
    """Проверяет имя и расширение выходного файла."""
    output_path = Path(output_file)

    if output_path.name != output_file:
        raise ValueError(
            "output_file должен содержать только имя файла"
        )

    if output_path.suffix.lower() != ".svg":
        raise ValueError("output_file должен иметь расширение .svg")


def validate_max_depth(value):
    """Проверяет и преобразует максимальную глубину анализа."""
    try:
        max_depth = int(value)
    except ValueError as error:
        raise ValueError(
            "max_depth должен быть целым числом"
        ) from error

    if max_depth < MIN_MAX_DEPTH:
        raise ValueError("max_depth должен быть не меньше 1")

    return max_depth


def load_config(file_path):
    """Загружает и проверяет настройки из XML."""
    try:
        tree = ET.parse(file_path)
    except ET.ParseError as error:
        raise ValueError(f"Ошибка XML: {error}") from error
    except OSError as error:
        raise ValueError(
            f"Не удалось открыть файл: {error}"
        ) from error

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
    max_depth = validate_max_depth(get_value(root, "max_depth"))

    validate_repository(repository, test_mode)
    validate_output_file(output_file)

    return {
        "package_name": package_name,
        "repository": repository,
        "test_mode": test_mode,
        "version": version,
        "output_file": output_file,
        "ascii_tree": ascii_tree,
        "max_depth": max_depth,
    }
