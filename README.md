# NuGet Dependency Graph Visualizer

## Описание проекта

Проект представляет собой инструмент для получения и визуализации графа зависимостей пакетов NuGet.

Программа загружает настройки из XML-файла, получает информацию о NuGet-пакетах, извлекает их зависимости и в дальнейшем строит граф зависимостей.

## Параметры конфигурации

Настройки задаются в файле `config.xml`.

| Параметр       | Описание                                   |
| -------------- | ------------------------------------------ |
| `package_name` | Имя анализируемого пакета                  |
| `repository`   | URL репозитория или путь к тестовому файлу |
| `test_mode`    | Режим использования тестового репозитория  |
| `version`      | Версия пакета                              |
| `output_file`  | Имя выходного SVG-файла                    |
| `ascii_tree`   | Включение вывода ASCII-дерева              |
| `max_depth`    | Максимальная глубина анализа               |

## Структура проекта

```text
.
├── .gitignore
├── README.md
├── config.xml
├── run.bat
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── nuget.py
└── tests/
    ├── __init__.py
    ├── test_config.py
    └── test_nuget.py
```

## Основные функции

### Модуль `config.py`

- `get_value()` — получает обязательное значение из XML.
- `validate_boolean()` — проверяет логические параметры.
- `validate_repository()` — проверяет URL или путь к тестовому файлу.
- `validate_output_file()` — проверяет имя и расширение выходного файла.
- `validate_max_depth()` — проверяет глубину анализа.
- `load_config()` — загружает и проверяет конфигурацию.

### Модуль `nuget.py`

- `build_package_url()` — формирует URL NuGet-пакета.
- `download_package()` — скачивает пакет из репозитория.
- `extract_nuspec()` — извлекает файл `.nuspec` из архива `.nupkg`.
- `parse_dependencies()` — извлекает прямые зависимости из XML.
- `fetch_direct_dependencies()` — выполняет получение прямых зависимостей пакета.

### Модуль `main.py`

Запускает программу, загружает конфигурацию, получает прямые зависимости и выводит их названия и версии.

## Запуск программы

Для запуска требуется Python 3.

Из корневой папки проекта выполните:

```bash
python -m src.main
```

В Windows также можно запустить программу с помощью файла:

```text
run.bat
```

## Запуск тестов

Для запуска автоматических тестов выполните:

```bash
python -m unittest discover -s tests -v
```

Тесты проверяют загрузку конфигурации, формирование URL, обработку архивов NuGet, разбор XML и получение прямых зависимостей.

## Пример конфигурации

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <package_name>Newtonsoft.Json</package_name>
    <repository>
        https://api.nuget.org/v3-flatcontainer/
    </repository>
    <test_mode>false</test_mode>
    <version>13.0.3</version>
    <output_file>dependencies.svg</output_file>
    <ascii_tree>true</ascii_tree>
    <max_depth>3</max_depth>
</configuration>
```

## Пример результата

Для пакета `Newtonsoft.Json` версии `13.0.3` программа получает следующие прямые зависимости:

```text
Пакет: Newtonsoft.Json
Версия: 13.0.3

Прямые зависимости:
- Microsoft.CSharp: 4.3.0
- NETStandard.Library: 1.6.1
- System.ComponentModel.TypeConverter: 4.3.0
- System.Runtime.Serialization.Primitives: 4.3.0
- System.Runtime.Serialization.Formatters: 4.3.0
- System.Xml.XmlDocument: 4.3.0

Всего зависимостей: 6
```

## Текущий этап разработки

**Этап 1 — завершён:**

- создание CLI-прототипа;
- загрузка XML-конфигурации;
- проверка параметров;
- обработка ошибок;
- автоматические тесты.

**Этап 2 — завершён:**

- получение NuGet-пакета по URL репозитория;
- извлечение файла `.nuspec` из архива `.nupkg`;
- разбор XML-описания пакета;
- получение прямых зависимостей и их версий;
- вывод результатов в консоль;
- автоматические тесты без обращения к сети.
