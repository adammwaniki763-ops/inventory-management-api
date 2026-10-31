# Inventory Management System

This project is a Python Flask REST API for the Moringa School summative lab.
It manages inventory items using CRUD operations and a temporary in-memory list.
It also searches the OpenFoodFacts API and includes a command-line client.

## Features

- Flask REST API
- GET all inventory items
- GET one inventory item
- POST a new inventory item
- PATCH selected item fields
- DELETE an inventory item
- OpenFoodFacts barcode and product-name search
- CLI client that communicates through HTTP
- Unit tests using pytest
- Mocked network calls using unittest.mock
- JSON error responses and input validation

## Important storage note

The assignment asks for simulated array storage, so this version uses a Python
list of dictionaries. Data is reset when the server restarts. A production
system would replace inventory.py storage with SQLite or PostgreSQL.

## Installation

Create and enter a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell use:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the API

Start the development server:

```bash
python app.py
```

The API is available at `http://127.0.0.1:5000`.

## API routes

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/health` | Check service status |
| GET | `/inventory` | List all items |
| GET | `/inventory/<id>` | View one item |
| POST | `/inventory` | Add an item |
| PATCH | `/inventory/<id>` | Update item fields |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/external-products/search?query=milk` | Search OpenFoodFacts |

## Example POST body

```json
{
  "name": "Kenyan Tea",
  "barcode": "123456789",
  "brand": "Highland Tea",
  "category": "Beverages",
  "price": 300,
  "stock": 8,
  "ingredients": "Black tea leaves"
}
```

## Example curl commands

```bash
curl http://127.0.0.1:5000/inventory
curl http://127.0.0.1:5000/inventory/1
curl -X POST http://127.0.0.1:5000/inventory -H "Content-Type: application/json" -d '{"name":"Tea","price":300,"stock":5}'
curl -X PATCH http://127.0.0.1:5000/inventory/1 -H "Content-Type: application/json" -d '{"stock":20}'
curl -X DELETE http://127.0.0.1:5000/inventory/1
```

## Run the CLI

Keep the Flask server running in one terminal. In another terminal run:

```bash
python cli.py
```

The menu supports list, view, add, update, delete, and external search.
Non-interactive examples are:

```bash
python cli.py list
python cli.py view 1
python cli.py search milk
python cli.py --base-url http://127.0.0.1:5000 list
```

## Run tests

```bash
pytest -q
```

The tests cover API routes, validation, CRUD behavior, CLI requests, parser
behavior, OpenFoodFacts normalization, and network failure handling. External
HTTP calls are mocked so tests remain reliable without an internet connection.

## Git workflow

Use a feature branch for each deliverable:

```bash
git checkout -b feature/crud-api
git add .
git commit -m "feat: add inventory CRUD API"
git checkout main
git merge feature/crud-api
git branch -d feature/crud-api
```

## Project files

- `app.py` contains Flask routes.
- `inventory.py` contains validation and in-memory storage.
- `external_api.py` contains OpenFoodFacts integration.
- `cli.py` contains the command-line client.
- `tests/` contains automated tests.

No TypeScript or TSX files are used in this project.
