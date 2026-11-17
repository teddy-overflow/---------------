import json
import re
from pathlib import Path

from src.nuget import fetch_direct_dependencies


PACKAGE_NAME_PATTERN = re.compile(r"^[A-Z0-9._-]+$")


def load_test_graph(file_path):
    """Загружает и проверяет тестовый граф из JSON."""
    try:
        with Path(file_path).open(
            "r",
            encoding="utf-8",
        ) as file:
            graph_data = json.load(file)

    except OSError as error:
        raise ValueError(
            f"Не удалось открыть тестовый граф: {error}"
        ) from error
    except json.JSONDecodeError as error:
        raise ValueError(
            "Некорректный JSON-файл тестового графа"
        ) from error

    if not isinstance(graph_data, dict):
        raise ValueError(
            "Тестовый граф должен содержать JSON-объект"
        )

    for package_name, dependencies in graph_data.items():
        if (
            not isinstance(package_name, str)
            or not PACKAGE_NAME_PATTERN.fullmatch(package_name)
        ):
            raise ValueError(
                "Названия пакетов должны содержать "
                "заглавные латинские буквы, цифры, "
                "точки, дефисы или подчёркивания"
            )

        if not isinstance(dependencies, list):
            raise ValueError(
                f"Зависимости {package_name} должны быть списком"
            )

        for dependency in dependencies:
            if not isinstance(dependency, dict):
                raise ValueError(
                    f"Некорректная зависимость пакета {package_name}"
                )

            dependency_name = dependency.get("name")
            dependency_version = dependency.get("version")

            if (
                not isinstance(dependency_name, str)
                or not PACKAGE_NAME_PATTERN.fullmatch(
                    dependency_name
                )
            ):
                raise ValueError(
                    "Некорректное название зависимости"
                )

            if (
                not isinstance(dependency_version, str)
                or not dependency_version.strip()
            ):
                raise ValueError(
                    "Некорректная версия зависимости"
                )

    return graph_data


def create_node_id(package_name, version):
    """Создаёт уникальный идентификатор пакета."""
    return f"{package_name.lower()}@{version.lower()}"


def build_dependency_graph(
    repository,
    package_name,
    version,
    max_depth,
    test_mode=False,
):
    """Строит граф зависимостей итеративным алгоритмом DFS."""
    if max_depth < 1:
        raise ValueError("max_depth должен быть не меньше 1")

    test_graph = {}

    if test_mode:
        test_graph = load_test_graph(repository)
        package_name = package_name.upper()

    graph = {}
    visited_depth = {}

    stack = [(package_name, version, 0)]

    while stack:
        current_name, current_version, depth = stack.pop()

        node_id = create_node_id(
            current_name,
            current_version,
        )

        previous_depth = visited_depth.get(node_id)

        if previous_depth is not None and previous_depth <= depth:
            continue

        visited_depth[node_id] = depth

        if depth >= max_depth:
            dependencies = []
        elif test_mode:
            dependencies = test_graph.get(
                current_name.upper(),
                [],
            )
        else:
            dependencies = fetch_direct_dependencies(
                repository,
                current_name,
                current_version,
            )

        dependency_ids = []

        for dependency in dependencies:
            dependency_id = create_node_id(
                dependency["name"],
                dependency["version"],
            )
            dependency_ids.append(dependency_id)

        graph[node_id] = {
            "name": current_name,
            "version": current_version,
            "dependencies": dependency_ids,
        }

        for dependency in reversed(dependencies):
            stack.append((
                dependency["name"],
                dependency["version"],
                depth + 1,
            ))

    return graph


def get_installation_order(graph, root_id):
    """Определяет порядок установки пакетов топологической сортировкой."""
    if root_id not in graph:
        raise ValueError("Корневой пакет отсутствует в графе")

    states = {}
    installation_order = []
    stack = [(root_id, False)]

    while stack:
        node_id, is_finished = stack.pop()

        if node_id not in graph:
            raise ValueError(
                f"В графе отсутствует узел: {node_id}"
            )

        if is_finished:
            states[node_id] = 2
            installation_order.append(node_id)
            continue

        state = states.get(node_id, 0)

        if state == 2:
            continue

        if state == 1:
            raise ValueError(
                f"Обнаружен цикл зависимостей: {node_id}"
            )

        states[node_id] = 1

        stack.append((node_id, True))

        dependencies = graph[node_id]["dependencies"]

        for dependency_id in reversed(dependencies):
            dependency_state = states.get(dependency_id, 0)

            if dependency_state == 1:
                raise ValueError(
                    f"Обнаружен цикл зависимостей: {dependency_id}"
                )

            if dependency_state != 2:
                stack.append((dependency_id, False))

    return installation_order
