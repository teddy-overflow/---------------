
import unittest
from pathlib import Path
from unittest.mock import patch

from src.graph import (
    build_dependency_graph,
    create_node_id,
    load_test_graph,
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


if __name__ == "__main__":
    unittest.main()
