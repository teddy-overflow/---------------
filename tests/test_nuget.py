
import unittest
from io import BytesIO
from unittest.mock import patch
from zipfile import ZipFile

from src.nuget import (
    build_package_url,
    extract_nuspec,
    fetch_direct_dependencies,
    parse_dependencies,
)


NUSPEC_XML = """\
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
    <metadata>
        <id>Example.Package</id>
        <version>1.0.0</version>
        <dependencies>
            <group targetFramework=".NETStandard2.0">
                <dependency id="Newtonsoft.Json" version="13.0.3" />
                <dependency id="Serilog" version="2.12.0" />
            </group>
        </dependencies>
    </metadata>
</package>
"""


def create_package():
    """Создаёт тестовый архив NuGet в памяти."""
    package_buffer = BytesIO()

    with ZipFile(package_buffer, "w") as archive:
        archive.writestr("Example.Package.nuspec", NUSPEC_XML)

    return package_buffer.getvalue()


class NugetTests(unittest.TestCase):
    """Тесты получения зависимостей NuGet."""

    def test_build_package_url(self):
        url = build_package_url(
            "https://api.nuget.org/v3-flatcontainer/",
            "Newtonsoft.Json",
            "13.0.3",
        )

        expected = (
            "https://api.nuget.org/v3-flatcontainer/"
            "newtonsoft.json/13.0.3/"
            "newtonsoft.json.13.0.3.nupkg"
        )

        self.assertEqual(url, expected)

    def test_extract_nuspec(self):
        package_data = create_package()
        nuspec_data = extract_nuspec(package_data)

        self.assertIn(b"Example.Package", nuspec_data)

    def test_extract_missing_nuspec(self):
        package_buffer = BytesIO()

        with ZipFile(package_buffer, "w") as archive:
            archive.writestr("readme.txt", "Test package")

        with self.assertRaises(ValueError):
            extract_nuspec(package_buffer.getvalue())

    def test_extract_invalid_archive(self):
        with self.assertRaises(ValueError):
            extract_nuspec(b"not a zip archive")

    def test_parse_dependencies(self):
        dependencies = parse_dependencies(
            NUSPEC_XML.encode("utf-8")
        )

        expected = [
            {
                "name": "Newtonsoft.Json",
                "version": "13.0.3",
            },
            {
                "name": "Serilog",
                "version": "2.12.0",
            },
        ]

        self.assertEqual(dependencies, expected)

    def test_parse_empty_dependencies(self):
        xml_data = b"<package><metadata><dependencies /></metadata></package>"

        self.assertEqual(parse_dependencies(xml_data), [])

    def test_parse_invalid_xml(self):
        with self.assertRaises(ValueError):
            parse_dependencies(b"<package>")

    @patch("src.nuget.download_package")
    def test_fetch_direct_dependencies(self, mock_download):
        mock_download.return_value = create_package()

        dependencies = fetch_direct_dependencies(
            "https://api.nuget.org/v3-flatcontainer/",
            "Example.Package",
            "1.0.0",
        )

        self.assertEqual(len(dependencies), 2)
        self.assertEqual(
            dependencies[0]["name"],
            "Newtonsoft.Json",
        )
        mock_download.assert_called_once()

    @patch("src.nuget.download_package")
    def test_fetch_download_error(self, mock_download):
        mock_download.side_effect = ValueError("Download failed")

        with self.assertRaises(ValueError):
            fetch_direct_dependencies(
                "https://api.nuget.org/v3-flatcontainer/",
                "Example.Package",
                "1.0.0",
            )


if __name__ == "__main__":
    unittest.main()
