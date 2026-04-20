from __future__ import annotations

import typer

from app.db import init_db

app = typer.Typer()


@app.command("init-db")
def init_db_command() -> None:
    init_db()
    typer.echo("Database initialized successfully. All tables have been created.")


if __name__ == "__main__":
    app()
