
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.graph import (
    build_dependency_graph,
    create_node_id,
    get_installation_order,
    load_test_graph,
)
from src.visualization import (
    create_mermaid,
    save_mermaid,
)


PROJECT_DIR = Path(__file__).resolve().parent.parent
TEST_GRAPH_PATH = PROJECT_DIR / "tests" / "test_graph.json"


class GraphTests(unittest.TestCase):
    """Тесты построения графа зависимостей."""

    def test_create_node_id(self):
        node_id = create_node_id("Newtonsoft.Json", "13.0.3")

        self.assertEqual(node_id, "newtonsoft.json@13.0.3")

    def test_load_test_graph(self):
        graph = load_test_graph(TEST_GRAPH_PATH)

        self.assertIn("NEWTONSOFT.JSON", graph)
        self.assertIn("MICROSOFT.CSHARP", graph)

    def test_build_test_graph(self):
        graph = build_dependency_graph(
            TEST_GRAPH_PATH,
            "NEWTONSOFT.JSON",
            "1.0.0",
            3,
            test_mode=True,
        )

        root_id = "newtonsoft.json@1.0.0"

        self.assertIn(root_id, graph)

        self.assertEqual(
            graph[root_id]["dependencies"],
            [
                "microsoft.csharp@4.3.0",
                "netstandard.library@1.6.1",
            ],
        )

    def test_max_depth(self):
        graph = build_dependency_graph(
            TEST_GRAPH_PATH,
            "NEWTONSOFT.JSON",
            "1.0.0",
            1,
            test_mode=True,
        )

        root_id = "newtonsoft.json@1.0.0"
        dependency_id = "microsoft.csharp@4.3.0"

        self.assertIn(root_id, graph)
        self.assertIn(dependency_id, graph)

        self.assertEqual(
            graph[dependency_id]["dependencies"],
            [],
        )

    def test_cycle_protection(self):
        graph_data = {
            "A": [
                {"name": "B", "version": "1.0"},
            ],
            "B": [
                {"name": "A", "version": "1.0"},
            ],
        }

        with patch(
            "src.graph.load_test_graph",
            return_value=graph_data,
        ):
            graph = build_dependency_graph(
                "unused.json",
                "A",
                "1.0",
                10,
                test_mode=True,
            )

        self.assertEqual(len(graph), 2)
        self.assertIn("a@1.0", graph)
        self.assertIn("b@1.0", graph)

    @patch("src.graph.fetch_direct_dependencies")
    def test_build_real_graph(self, mock_fetch):
        mock_fetch.side_effect = [
            [
                {
                    "name": "Serilog",
                    "version": "2.12.0",
                },
            ],
            [],
        ]

        graph = build_dependency_graph(
            "https://example.com/",
            "Example.Package",
            "1.0.0",
            3,
        )

        self.assertIn("example.package@1.0.0", graph)
        self.assertIn("serilog@2.12.0", graph)

        self.assertEqual(mock_fetch.call_count, 2)

    def test_invalid_max_depth(self):
        with self.assertRaises(ValueError):
            build_dependency_graph(
                TEST_GRAPH_PATH,
                "NEWTONSOFT.JSON",
                "1.0.0",
                0,
                test_mode=True,
            )

    def test_installation_order(self):
        graph = {
            "a@1.0": {
                "name": "A",
                "version": "1.0",
                "dependencies": ["b@1.0", "c@1.0"],
            },
            "b@1.0": {
                "name": "B",
                "version": "1.0",
                "dependencies": ["d@1.0"],
            },
            "c@1.0": {
                "name": "C",
                "version": "1.0",
                "dependencies": ["d@1.0"],
            },
            "d@1.0": {
                "name": "D",
                "version": "1.0",
                "dependencies": [],
            },
        }

        order = get_installation_order(graph, "a@1.0")

        self.assertEqual(
            order,
            ["d@1.0", "b@1.0", "c@1.0", "a@1.0"],
        )

    def test_installation_order_chain(self):
        graph = {
            "a@1.0": {
                "name": "A",
                "version": "1.0",
                "dependencies": ["b@1.0"],
            },
            "b@1.0": {
                "name": "B",
                "version": "1.0",
                "dependencies": ["c@1.0"],
            },
            "c@1.0": {
                "name": "C",
                "version": "1.0",
                "dependencies": [],
            },
        }

        order = get_installation_order(graph, "a@1.0")

        self.assertEqual(
            order,
            ["c@1.0", "b@1.0", "a@1.0"],
        )

    def test_installation_order_independent_dependencies(self):
        graph = {
            "a@1.0": {
                "name": "A",
                "version": "1.0",
                "dependencies": ["b@1.0", "c@1.0"],
            },
            "b@1.0": {
                "name": "B",
                "version": "1.0",
                "dependencies": [],
            },
            "c@1.0": {
                "name": "C",
                "version": "1.0",
                "dependencies": [],
            },
        }

        order = get_installation_order(graph, "a@1.0")

        self.assertEqual(
            order,
            ["b@1.0", "c@1.0", "a@1.0"],
        )

    def test_installation_order_cycle(self):
        graph = {
            "a@1.0": {
                "name": "A",
                "version": "1.0",
                "dependencies": ["b@1.0"],
            },
            "b@1.0": {
                "name": "B",
                "version": "1.0",
                "dependencies": ["a@1.0"],
            },
        }

        with self.assertRaisesRegex(ValueError, "цикл"):
            get_installation_order(graph, "a@1.0")

    def test_installation_order_missing_node(self):
        graph = {
            "a@1.0": {
                "name": "A",
                "version": "1.0",
                "dependencies": ["missing@1.0"],
            },
        }

        with self.assertRaisesRegex(ValueError, "отсутствует"):
            get_installation_order(graph, "a@1.0")

    def test_create_mermaid(self):
        graph = {
            "a@1.0": {
                "name": "A",
                "version": "1.0",
                "dependencies": ["b@1.0"],
            },
            "b@1.0": {
                "name": "B",
                "version": "2.0",
                "dependencies": [],
            },
        }

        mermaid = create_mermaid(graph, "a@1.0")

        self.assertIn("flowchart TD", mermaid)
        self.assertIn('package_0["A<br/>1.0"]', mermaid)
        self.assertIn('package_1["B<br/>2.0"]', mermaid)
        self.assertIn("package_0 --> package_1", mermaid)

    def test_save_mermaid(self):
        mermaid = "flowchart TD\n    A --> B\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.mmd"

            saved_file = save_mermaid(
                mermaid,
                output_file,
            )

            self.assertTrue(saved_file.exists())
            self.assertEqual(
                saved_file.read_text(encoding="utf-8"),
                mermaid,
            )

    def test_create_mermaid_missing_root(self):
        graph = {
            "a@1.0": {
                "name": "A",
                "version": "1.0",
                "dependencies": [],
            },
        }

        with self.assertRaisesRegex(ValueError, "Корневой пакет"):
            create_mermaid(graph, "missing@1.0")


if __name__ == "__main__":
    unittest.main()
