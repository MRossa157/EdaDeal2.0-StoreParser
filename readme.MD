# Sbermarket Store Parser for Edadeal2.0
This parser is part of [Edadeal2.0/Parser](https://github.com/Alotgrey/EdaDeal2.0/tree/Parser)

## Requirements
- Python >=3.12.2
- Poetry
- Chrome browser

## How to use
1) Connect to your PostgreSQL via ```.env``` file (see ```.env.example```)
2) Install all requirements:
    - ```pip install poetry```
    - ```poetry install```
3) Launch app/main.py: ```python app/main.py```

## Why no docker?
Because I am using ```no_driver``` without **headless mode**, and in that format it is impossible to run container in Docker
