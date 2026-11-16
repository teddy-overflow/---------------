# NuGet Dependency Graph Visualizer

## Описание проекта

Проект представляет собой инструмент для визуализации графа зависимостей пакетов NuGet.

На первом этапе реализован CLI-прототип, который загружает настройки из XML-файла, проверяет их корректность и выводит параметры программы в консоль.

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
├── config.xml
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py
│   └── main.py
└── tests/
    ├── __init__.py
    └── test_config.py
```

## Основные функции

- `get_value()` — получает обязательное значение из XML.
- `validate_boolean()` — проверяет логические параметры.
- `validate_repository()` — проверяет URL или путь к тестовому файлу.
- `validate_output_file()` — проверяет имя и расширение выходного файла.
- `validate_max_depth()` — проверяет глубину анализа.
- `load_config()` — загружает и проверяет конфигурацию.
- `main()` — запускает программу и выводит настройки.

## Запуск программы

Для запуска требуется Python 3.

Из корневой папки проекта выполните:

```bash
python -m src.main
```

## Запуск тестов

Для запуска автоматических тестов выполните:

```bash
python -m unittest discover -s tests -v
```

## Пример конфигурации

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <package_name>Newtonsoft.Json</package_name>
    <repository>https://api.nuget.org/v3-flatcontainer/</repository>
    <test_mode>false</test_mode>
    <version>13.0.3</version>
    <output_file>dependencies.svg</output_file>
    <ascii_tree>true</ascii_tree>
    <max_depth>3</max_depth>
</configuration>
```

## Текущий этап разработки

Реализован первый этап:

- создание CLI-прототипа;
- загрузка XML-конфигурации;
- проверка параметров;
- обработка ошибок;
- автоматические тесты.
