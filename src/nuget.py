
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET


DOWNLOAD_TIMEOUT = 30


def build_package_url(repository, package_name, version):
    """Формирует URL для скачивания NuGet-пакета."""
    base_url = repository.rstrip("/")
    package_id = package_name.lower()
    package_version = version.lower()

    return (
        f"{base_url}/{package_id}/{package_version}/"
        f"{package_id}.{package_version}.nupkg"
    )


def download_package(package_url):
    """Скачивает NuGet-пакет по указанному URL."""
    try:
        with urlopen(package_url, timeout=DOWNLOAD_TIMEOUT) as response:
            return response.read()
    except HTTPError as error:
        raise ValueError(
            f"Ошибка HTTP при скачивании пакета: {error.code}"
        ) from error
    except URLError as error:
        raise ValueError(
            f"Не удалось подключиться к NuGet: {error.reason}"
        ) from error


def extract_nuspec(package_data):
    """Извлекает XML-файл nuspec из архива NuGet."""
    try:
        with ZipFile(BytesIO(package_data)) as archive:
            nuspec_files = [
                name for name in archive.namelist()
                if name.lower().endswith(".nuspec")
            ]

            if not nuspec_files:
                raise ValueError("В пакете отсутствует файл nuspec")

            return archive.read(nuspec_files[0])

    except BadZipFile as error:
        raise ValueError("Полученный файл не является архивом NuGet") from error


def parse_dependencies(nuspec_data):
    """Извлекает прямые зависимости из XML-файла nuspec."""
    try:
        root = ET.fromstring(nuspec_data)
    except ET.ParseError as error:
        raise ValueError("Некорректный XML-файл nuspec") from error

    dependencies = []
    seen_dependencies = set()

    for element in root.findall(".//{*}dependency"):
        package_id = element.get("id")
        package_version = element.get("version", "не указана")

        if not package_id:
            continue

        dependency = (package_id, package_version)

        if dependency not in seen_dependencies:
            dependencies.append({
                "name": package_id,
                "version": package_version,
            })
            seen_dependencies.add(dependency)

    return dependencies


def fetch_direct_dependencies(repository, package_name, version):
    """Получает прямые зависимости указанной версии пакета."""
    package_url = build_package_url(
        repository,
        package_name,
        version,
    )

    package_data = download_package(package_url)
    nuspec_data = extract_nuspec(package_data)

    return parse_dependencies(nuspec_data)
