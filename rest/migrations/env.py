import os

from alembic.context import config
from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from alembic import context

# Load environment variables from .env file
load_dotenv()

def run_migrations_online():
    # Get the database URL from the environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set.")

    config.set_main_option("sqlalchemy.url", database_url)

    # Continue with the migration process
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.')
    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
