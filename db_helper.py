import os
import oracledb
from dotenv import load_dotenv

# Load configurations
load_dotenv()

def get_connection():
    """Establishes a direct connection to the Oracle Database."""
    user = os.getenv("DB_USER", "shop_user")
    password = os.getenv("DB_PASSWORD", "shop_pwd")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "1521")
    service_name = os.getenv("DB_SERVICE_NAME", "XE")
    
    dsn = f"{host}:{port}/{service_name}"
    
    return oracledb.connect(user=user, password=password, dsn=dsn)

def execute_read(query, params=None, fetch_all=True):
    """
    Executes a read query and returns results mapped as dictionaries.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        # Get column names in lowercase
        if cursor.description:
            columns = [col[0].lower() for col in cursor.description]
        else:
            return None
            
        if fetch_all:
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None
    except Exception as e:
        print(f"Error executing read query: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def execute_write(query, params=None, commit=True):
    """
    Executes a DML query (INSERT, UPDATE, DELETE).
    
    Args:
        query (str): SQL query text.
        params (dict/list): Query parameters for binding.
        commit (bool): Whether to commit the transaction immediately.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        row_count = cursor.rowcount
        if commit:
            conn.commit()
        return row_count
    except Exception as e:
        if commit:
            conn.rollback()
        print(f"Error executing write query: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()
