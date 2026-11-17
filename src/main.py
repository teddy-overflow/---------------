
from pathlib import Path

from src.config import load_config
from src.graph import build_dependency_graph, create_node_id


def print_graph(graph, root_id, ascii_tree=True):
    """Выводит граф зависимостей в виде дерева."""
    if root_id not in graph:
        print("Граф зависимостей пуст.")
        return

    root = graph[root_id]

    print(f"{root['name']} ({root['version']})")

    if not ascii_tree:
        for node in graph.values():
            print(f"- {node['name']} ({node['version']})")

            for dependency_id in node["dependencies"]:
                dependency = graph.get(dependency_id)

                if dependency is not None:
                    print(
                        f"  -> {dependency['name']} "
                        f"({dependency['version']})"
                    )
        return

    stack = []
    root_dependencies = root["dependencies"]

    for index in range(len(root_dependencies) - 1, -1, -1):
        stack.append((
            root_dependencies[index],
            "",
            index == len(root_dependencies) - 1,
            frozenset({root_id}),
        ))

    while stack:
        node_id, prefix, is_last, ancestors = stack.pop()

        node = graph.get(node_id)

        if node is None:
            continue

        branch = "└── " if is_last else "├── "

        print(
            f"{prefix}{branch}"
            f"{node['name']} ({node['version']})"
        )

        if node_id in ancestors:
            print(f"{prefix}    [цикл]")
            continue

        new_ancestors = ancestors | {node_id}
        children = node["dependencies"]

        for index in range(len(children) - 1, -1, -1):
            stack.append((
                children[index],
                prefix + ("    " if is_last else "│   "),
                index == len(children) - 1,
                new_ancestors,
            ))


def main():
    """Запускает программу и строит граф зависимостей."""
    project_dir = Path(__file__).resolve().parent.parent
    config_path = project_dir / "config.xml"

    try:
        config = load_config(config_path)

        repository = config["repository"]

        if config["test_mode"]:
            repository_path = Path(repository)

            if not repository_path.is_absolute():
                repository_path = project_dir / repository_path

            repository = str(repository_path)

        print(f"Пакет: {config['package_name']}")
        print(f"Версия: {config['version']}")
        print(f"Максимальная глубина: {config['max_depth']}")

        if config["test_mode"]:
            print("\nРежим: тестовый")
        else:
            print("\nРежим: NuGet")

        print("\nПостроение графа зависимостей...")

        graph = build_dependency_graph(
            repository,
            config["package_name"],
            config["version"],
            config["max_depth"],
            config["test_mode"],
        )

    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    root_id = create_node_id(
        config["package_name"],
        config["version"],
    )

    print("\nГраф зависимостей:\n")

    print_graph(
        graph,
        root_id,
        config["ascii_tree"],
    )

    print(f"\nВсего узлов в графе: {len(graph)}")


if __name__ == "__main__":
    main()
