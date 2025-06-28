import secrets

import typer

from src.env import get_db, Base, engine, init_engine
from src.models import ApiKey

app = typer.Typer(help="Utility CLI for the SIScan RPA API")


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


if __name__ == "__main__":
    app()
