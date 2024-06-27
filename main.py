import json

import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

import src.local_settings.local_database as db
from src.models.store import Store
from utils.get_parser import get_store_obj

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red"
})

console = Console(theme=custom_theme)
app = typer.Typer()

add_app = typer.Typer()
app.add_typer(add_app, name="add")

show_app = typer.Typer()
app.add_typer(show_app, name="show")

delete_app = typer.Typer()
app.add_typer(delete_app, name="delete")

commit_app = typer.Typer()
app.add_typer(commit_app, name="commit")

@add_app.command("store", short_help='adds brand')
def add_store(brand: str, alias: str, comments: str = None):
    store: Store = get_store_obj(brand)
    data = json.dumps(store.get_data(), indent=2)
    db.add_store(brand, alias, comments, data=data)
    try:
        pass
    except Exception as e:
        console.print(f'Error: {e}', style='danger')
    show_stores()


@add_app.command("catalog", short_help='add catalogue of products for a store')
def add_catalog(store_alias: str, alias: str, comments: str = None):
    try:
        db.add_catalog(store_alias, alias, comments=comments)
    except Exception as e:
        console.print(f'Error: {e}', style='danger')
    show_catalogs()


@app.command()
def show():
    show_stores()

@show_app.command("stores", short_help="show a table of all brands")
def show_stores():
    stores = db.get_all_stores()

    print("[bold magenta]Stores[/bold magenta]!", "🛒")

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("#", style="dim", width=6)
    table.add_column("Brand")
    table.add_column("Time Created")
    table.add_column("Alias")
    table.add_column("Comments")

    for store in stores:
        table.add_row(*store)
    print(table)

@show_app.command("catalog", short_help="show a table of all brands")
def show_catalogs():
    catalogs = db.get_all_catalogs()

    print("[bold magenta]Catalogs[/bold magenta]!", "🛒")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=6)
    table.add_column("Store")
    table.add_column("Time Created")
    table.add_column("Alias")
    table.add_column("Comments")
    table.add_column("Committed")
    table.add_column("Error")

    for catalog in catalogs:
        table.add_row(*catalog)
    print(table)

@show_app.command("store", short_help="delete a store from the list")
def delete_stores(alias: str):
    try:
        db.delete_store(alias)
    except Exception as e:
        console.print(f'Warning: {e}', style='warning')
    show_catalogs()


@delete_app.command("catalog", short_help="delete a catalog from the list")
def delete_catalogs(alias: str):
    try:
        db.delete_catalog(alias)
    except Exception as e:
        console.print(f'Warning: {e}', style='warning')
    show_catalogs()

@commit_app.command("catalog", short_help="commit a catalog from the list")
def commit_catalog(alias: str):
    db.commit_catalog(alias)
    try:
        pass
    except Exception as e:
        console.print(f'Error: {e}', style='danger')
    show_catalogs()

if __name__ == "__main__":
    app()
