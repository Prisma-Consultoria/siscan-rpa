import secrets

import typer

from src.env import get_db, Base, engine, init_engine
from src.models import ApiKey

app = typer.Typer(help="Utility CLI for the SISCAN RPA API")


@app.command()
def create_apikey(db_path: str | None = None) -> None:
    """Generate and store a new API key."""
    if db_path:
        init_engine(db_path)
        Base.metadata.create_all(bind=engine)

    key = secrets.token_hex(32)
    db = get_db()
    db.add(ApiKey(key=key))
    db.commit()
    db.close()
    typer.echo(f"API key: {key}")


@app.command()
def delete_apikey(key: str, db_path: str | None = None) -> None:
    """Delete an existing API key."""
    if db_path:
        init_engine(db_path)
        Base.metadata.create_all(bind=engine)

    db = get_db()
    key = db.query(ApiKey).filter_by(key=key).first()
    if key:
        db.delete(key)
        db.commit()
        typer.echo(f"API key {key} deleted.")
    else:
        typer.echo(f"API key {key} not found.")


if __name__ == "__main__":
    app()
