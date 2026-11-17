import json
import subprocess
import tempfile
from pathlib import Path


def create_mermaid(graph, root_id):
    """Создаёт текст диаграммы Mermaid из графа зависимостей."""
    if root_id not in graph:
        raise ValueError("Корневой пакет отсутствует в графе")

    lines = ["flowchart TD"]

    node_ids = {}
    for index, node_id in enumerate(graph):
        node_ids[node_id] = f"package_{index}"

    for node_id, node in graph.items():
        mermaid_id = node_ids[node_id]

        name = str(node["name"]).replace('"', "&quot;")
        version = str(node["version"]).replace('"', "&quot;")

        label = f"{name}<br/>{version}"

        lines.append(
            f'    {mermaid_id}["{label}"]'
        )

    for node_id, node in graph.items():
        source_id = node_ids[node_id]

        for dependency_id in node["dependencies"]:
            if dependency_id not in node_ids:
                continue

            target_id = node_ids[dependency_id]

            lines.append(
                f"    {source_id} --> {target_id}"
            )

    return "\n".join(lines) + "\n"


def save_mermaid(mermaid_text, output_file):
    """Сохраняет текст диаграммы Mermaid."""
    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        mermaid_text,
        encoding="utf-8",
    )

    return output_path


def render_mermaid(mermaid_file, output_file):
    """Преобразует Mermaid-файл в SVG с помощью Mermaid CLI."""
    mermaid_path = Path(mermaid_file).resolve()
    output_path = Path(output_file).resolve()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    edge_paths = [
        Path(
            r"C:\Program Files (x86)\Microsoft\Edge"
            r"\Application\msedge.exe"
        ),
        Path(
            r"C:\Program Files\Microsoft\Edge"
            r"\Application\msedge.exe"
        ),
    ]

    edge_path = next(
        (path for path in edge_paths if path.exists()),
        None,
    )

    if edge_path is None:
        raise ValueError(
            "Не удалось найти Microsoft Edge"
        )

    puppeteer_config = {
        "executablePath": str(edge_path),
        "args": ["--no-sandbox"],
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "puppeteer.json"

        config_path.write_text(
            json.dumps(puppeteer_config),
            encoding="utf-8",
        )

        command = [
            "cmd",
            "/c",
            "mmdc.cmd",
            "-i",
            str(mermaid_path),
            "-o",
            str(output_path),
            "-p",
            str(config_path),
        ]

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

        except FileNotFoundError as error:
            raise ValueError(
                "Mermaid CLI не найден. "
                "Проверьте установку Mermaid CLI"
            ) from error

        except subprocess.CalledProcessError as error:
            message = error.stderr or error.stdout

            raise ValueError(
                f"Ошибка создания SVG: {message}"
            ) from error

    if not output_path.exists():
        raise ValueError(
            "Mermaid CLI не создал SVG-файл"
        )

    return output_path
