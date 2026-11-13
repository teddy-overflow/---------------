import tempfile
import unittest
from pathlib import Path

from src.config import load_config


VALID_XML = """\
<configuration>
    <package_name>Newtonsoft.Json</package_name>
    <repository>https://api.nuget.org/v3-flatcontainer/</repository>
    <test_mode>false</test_mode>
    <version>13.0.3</version>
    <output_file>dependencies.svg</output_file>
    <ascii_tree>true</ascii_tree>
    <max_depth>3</max_depth>
</configuration>
"""


class ConfigTests(unittest.TestCase):
    """Тесты загрузки и проверки конфигурации."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.xml"
        self.config_path.write_text(VALID_XML, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_config(self, old, new):
        content = self.config_path.read_text(encoding="utf-8")
        content = content.replace(old, new)
        self.config_path.write_text(content, encoding="utf-8")

    def test_valid_config(self):
        config = load_config(self.config_path)
        self.assertEqual(config["package_name"], "Newtonsoft.Json")
        self.assertEqual(config["max_depth"], 3)

    def test_empty_package_name(self):
        self.write_config(
            "<package_name>Newtonsoft.Json</package_name>",
            "<package_name> </package_name>",
        )
        with self.assertRaises(ValueError):
            load_config(self.config_path)

    def test_invalid_repository(self):
        self.write_config(
            "https://api.nuget.org/v3-flatcontainer/",
            "not-a-url",
        )
        with self.assertRaises(ValueError):
            load_config(self.config_path)

    def test_invalid_test_mode(self):
        self.write_config(
            "<test_mode>false</test_mode>",
            "<test_mode>maybe</test_mode>",
        )
        with self.assertRaises(ValueError):
            load_config(self.config_path)

    def test_empty_version(self):
        self.write_config(
            "<version>13.0.3</version>",
            "<version> </version>",
        )
        with self.assertRaises(ValueError):
            load_config(self.config_path)

    def test_invalid_output_file(self):
        self.write_config(
            "dependencies.svg",
            "folder/dependencies.png",
        )
        with self.assertRaises(ValueError):
            load_config(self.config_path)

    def test_invalid_ascii_tree(self):
        self.write_config(
            "<ascii_tree>true</ascii_tree>",
            "<ascii_tree>yes</ascii_tree>",
        )
        with self.assertRaises(ValueError):
            load_config(self.config_path)

    def test_invalid_max_depth(self):
        self.write_config(
            "<max_depth>3</max_depth>",
            "<max_depth>abc</max_depth>",
        )
        with self.assertRaises(ValueError):
            load_config(self.config_path)

    def test_zero_max_depth(self):
        self.write_config(
            "<max_depth>3</max_depth>",
            "<max_depth>0</max_depth>",
        )
        with self.assertRaises(ValueError):
            load_config(self.config_path)


if __name__ == "__main__":
    unittest.main()