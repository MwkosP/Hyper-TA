import sqlite3
import pandas as pd
import os


#? The Database: 
DB_PATH = os.path.join(os.path.dirname(__file__), "market.db")

def _connect():
    return sqlite3.connect(DB_PATH)


# =====================================================
# Generic save (ANY TABLE, ANY DATAFRAME)
# =====================================================
def save_table(table: str, df: pd.DataFrame):
    if df is None or len(df) == 0:
        raise ValueError(f"❌ save_table('{table}') received empty df.")

    df = df.copy()

    # Convert datetime to string for SQLite
    for col in df.columns:
        if isinstance(df[col].dtype, pd.DatetimeTZDtype) or df[col].dtype == "datetime64[ns]":
            df[col] = df[col].astype(str)

    conn = _connect()
    df.to_sql(table, conn, if_exists="replace", index=False)
    conn.close()

    print(f"📌 Saved {len(df)} rows → table '{table}'")
    


# =====================================================
# Generic load (ANY TABLE)
# =====================================================
def load_table(table: str) -> pd.DataFrame:
    conn = _connect()
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()

    # Convert anything named 'date' or 'Date' back to datetime
    for col in df.columns:
        if col.lower() == "date":
            df[col] = pd.to_datetime(df[col])

    return df



# =====================================================
# Drop a specific table
# =====================================================
def drop_table(table: str):
    conn = _connect()
    conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    conn.close()
    print(f"🗑 Dropped table '{table}'")





# =====================================================
# List all tables in the database
# =====================================================
def list_tables():
    conn = _connect()
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [t[0] for t in cur.fetchall()]

    conn.close()

    print("📋 Tables:", tables)
    return tables



# =====================================================
# Drop ALL tables — full wipe
# =====================================================
def drop_all_tables():
    conn = _connect()
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cur.fetchall()]

    if not tables:
        print("⚠️ No tables found — DB already empty.")
        conn.close()
        return

    print("🔥 Dropping ALL tables:", tables)

    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table};")
        print(f"   ✔ Dropped table '{table}'")

    conn.commit()
    conn.close()

    print("🚨 Database fully wiped!")
