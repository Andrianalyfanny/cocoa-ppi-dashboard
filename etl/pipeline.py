import os
import sys
import pandas as pd
import bcrypt
from sqlalchemy import create_engine, text
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASOURCES_DIR = os.path.join(BASE_DIR, "datasources")
DATABASE_DIR = os.path.join(BASE_DIR, "database")

DB_TYPE = os.getenv("DB_TYPE")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_engine():
    """Connect to the database."""
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print(f"[ETL] Connecting to PostgreSQL: {url}")
    return create_engine(url)


def extract_cocoa():
    """Extract cocoa price data from a CSV file."""
    path = os.path.join(DATASOURCES_DIR, "PCOCOUSDM.csv")
    df = pd.read_csv(path, parse_dates=["observation_date"])
    df.rename(columns={"observation_date": "DATE"}, inplace=True)
    df.rename(columns={"PCOCOUSDM": "value"}, inplace=True)
    df["series"] = "PCOCOUSDM"
    print(f"[ETL] Extracted {len(df)} cocoa price rows.")
    return df


def extract_ppi():
    """Extract PPI data from a CSV file."""
    path = os.path.join(DATASOURCES_DIR, "PCU3113513113517.csv")
    df = pd.read_csv(path, parse_dates=["observation_date"])
    df.rename(columns={"observation_date": "DATE"}, inplace=True)
    df.rename(columns={"PCU3113513113517": "value"}, inplace=True)
    df["series"] = "PCU3113513113517"
    print(f"[ETL] Extracted {len(df)} PPI rows.")
    return df


# Transformation

def transform_to_yearly(df):
    """Transform monthly data to yearly data."""
    df["year"] = df["DATE"].dt.yearly

    df = df[df["year"].between(2020, 2026)].copy()

    yearly = (
        df.groupby(["series", "year"])["value"]
        .mean()
        .reset_index()
        .rename(columns={"value": "avg_value"})
    )
    yearly = yearly.sort_values(["series", "year"]).reset_index(drop=True)

    yearly["yoy_change"] = yearly.groupby("series")["avg_value"].diff()
    yearly["yoy_pct_change"] = yearly.groupby("series")["avg_value"].pct_change() * 100

    ppi_base = 100.0
    mask_ppi = yearly["series"] == "PCU3113513113517"
    yearly.loc[mask_ppi, "pct_change_ref"] = (
        (yearly.loc[mask_ppi, "avg_value"] - ppi_base) / ppi_base * 100
    )

    print(f"[ETL] Transformed to {len(yearly)} yearly rows.")
    return yearly


def transform_monthly(cocoa_df, ppi_df):
    """Transform monthly data to yearly data."""
    combined = pd.concat([cocoa_df, ppi_df], ignore_index=True)
    combined["year"] = combined["DATE"].dt.year
    combined = combined[combined["year"].between(2020, 2026)].copy()
    combined["date_str"] = combined["DATE"].dt.strftime("%Y-%m-%d")
    print(f"[ETL] Combined {len(combined)} monthly rows.")
    return combined[["date_str", "series", "value"]]


# Load

def create_schema(engine):
    """Create the database schema."""
    ddl = """
    CREATE TABLE IF NOT EXISTS raw_monthly (
        id SERIAL PRIMARY KEY,
        date_str TEXT NOT NULL,
        series TEXT NOT NULL,
        value DOUBLE PRECISION NOT NULL
    );

    CREATE TABLE IF NOT EXISTS yearly_indicators (
        id SERIAL PRIMARY KEY,
        series TEXT NOT NULL,
        year INTEGER NOT NULL,
        avg_value DOUBLE PRECISION,
        yoy_change DOUBLE PRECISION,
        yoy_pct_change DOUBLE PRECISION,
        pct_change_ref DOUBLE PRECISION,
        UNIQUE(series, year)
    );

    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()

    print("[ETL] Schema created in PostgreSQL.")

def load_data(engine, yearly_df, monthly_df):
    """Load data into the database."""
    monthly_df.to_sql("raw_monthly", engine, if_exists="replace", index=False)
    print(f"[ETL] Loaded {len(monthly_df)} rows into raw_monthly.")

    yearly_df.to_sql("yearly_indicators", engine, if_exists="replace", index=False)
    print(f"[ETL] Loaded {len(yearly_df)} rows into yearly_indicators.")


def seed_default_user(engine):
    """Seed the database with a default user."""
    username = os.getenv("ADMIN_USER", "admin")
    password = os.getenv("ADMIN_PASS", "admin123")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with engine.connect() as conn:
        existing = conn.execute(
            text("SELECT id FROM users WHERE username = :u"), {"u": username}
        ).fetchone()
        if not existing:
            conn.execute(
                text("INSERT INTO users (username, password_hash) VALUES (:u, :h)"),
                {"u": username, "h": hashed},
            )
            conn.commit()
            print(f"[ETL] Default user '{username}' created (password: '{password}').")
        else:
            print(f"[ETL] User '{username}' already exists — skipping seed.")



def run():
    """Run the ETL pipeline."""
    print("=" * 60)
    print(" COCOA DASHBOARD — ETL PIPELINE")
    print(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Extract
    cocoa_df = extract_cocoa()
    ppi_df = extract_ppi()

    # Transform
    combined_raw = pd.concat([cocoa_df, ppi_df], ignore_index=True)
    combined_raw["year"] = combined_raw["DATE"].dt.year
    filtered = combined_raw[combined_raw["year"].between(2020, 2026)].copy()
    filtered["date_str"] = filtered["DATE"].dt.strftime("%Y-%m-%d")

    monthly_df = filtered[["date_str", "series", "value"]]
    yearly_df = transform_to_yearly(filtered)

    # Load
    engine = get_engine()
    create_schema(engine)
    load_data(engine, yearly_df, monthly_df)
    seed_default_user(engine)

    print("=" * 60)
    print(" ETL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    run()