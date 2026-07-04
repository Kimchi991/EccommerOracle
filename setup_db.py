import os
import sys
import argparse
import getpass
import oracledb
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description="Initialize OracleShop Manager Oracle Database Schema")
    parser.add_argument("--host", default=os.getenv("DB_HOST", "localhost"), help="Oracle DB Host")
    parser.add_argument("--port", default=os.getenv("DB_PORT", "1521"), help="Oracle DB Port")
    parser.add_argument("--service", default=os.getenv("DB_SERVICE_NAME", "XE"), help="Oracle DB Service Name")
    parser.add_argument("--admin-user", default="SYSTEM", help="Admin username (default: SYSTEM)")
    parser.add_argument("--admin-password", help="Admin password. Will prompt if not provided.")
    parser.add_argument("--app-user", default=os.getenv("DB_USER", "shop_user"), help="Application User to create")
    parser.add_argument("--app-password", default=os.getenv("DB_PASSWORD", "shop_pwd"), help="Application User password")
    return parser.parse_args()

def run_sql_script(connection, script_path):
    print(f"Reading SQL script: {script_path}")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split script by '/' at the end of a line or on its own line
    # This separates PL/SQL blocks and independent SQL groups
    raw_blocks = content.split("\n/")
    
    cursor = connection.cursor()
    
    for i, raw_block in enumerate(raw_blocks):
        block = raw_block.strip()
        if not block:
            continue
            
        # Check if the block is a PL/SQL block or trigger definition by ignoring comments
        lines_clean = [line.strip() for line in block.split('\n') if line.strip() and not line.strip().startswith('--')]
        first_line = lines_clean[0].upper() if lines_clean else ""
        is_plsql = any(first_line.startswith(keyword) for keyword in ["DECLARE", "BEGIN", "CREATE OR REPLACE TRIGGER", "CREATE TRIGGER"])
        
        if is_plsql:
            print(f"Executing PL/SQL block {i+1}...")
            try:
                cursor.execute(block)
            except Exception as e:
                print(f"Error executing PL/SQL block {i+1}:\n{e}")
                connection.rollback()
                raise
        else:
            # Regular SQL statements (like CREATE TABLE or INSERT) separated by semicolons
            statements = block.split(";")
            for stmt in statements:
                stmt_clean = stmt.strip()
                if not stmt_clean:
                    continue
                # Ignore SQL developer specific commands if any
                if stmt_clean.upper().startswith("COMMIT"):
                    print("Committing transaction...")
                    connection.commit()
                elif stmt_clean.upper().startswith("SHOW ERRORS"):
                    continue
                else:
                    print(f"Executing SQL Statement: {stmt_clean[:60]}...")
                    try:
                        cursor.execute(stmt_clean)
                    except Exception as e:
                        print(f"Error executing statement:\n{stmt_clean}\nError: {e}")
                        connection.rollback()
                        raise
    connection.commit()
    cursor.close()
    print("Database schema script executed successfully!")

def main():
    args = parse_args()
    
    admin_pwd = args.admin_password or os.getenv("DB_SYSTEM_PASSWORD")
    if not admin_pwd:
        admin_pwd = getpass.getpass(prompt=f"Enter Oracle password for administrative user '{args.admin_user}': ")
        
    dsn = f"{args.host}:{args.port}/{args.service}"
    print(f"\nConnecting to Oracle XE admin account ({args.admin_user}@{dsn}) in THIN mode...")
    
    admin_conn = None
    try:
        admin_conn = oracledb.connect(
            user=args.admin_user,
            password=admin_pwd,
            dsn=dsn
        )
        print("Connected as administrator!")
        
        # Step 1: Drop/Create Dedicated App User
        cursor = admin_conn.cursor()
        
        # Bypass Oracle common user constraint (ORA-65096)
        try:
            cursor.execute('ALTER SESSION SET "_ORACLE_SCRIPT"=true')
            print("Configured session for local user creation (_ORACLE_SCRIPT=true).")
        except Exception as e:
            print(f"Warning setting session parameter: {e}")
            
        print(f"\nPreparing schema user '{args.app_user}'...")
        
        # Drop user if exists
        try:
            cursor.execute(f"DROP USER {args.app_user} CASCADE")
            print(f"Dropped existing user '{args.app_user}' successfully.")
        except oracledb.DatabaseError as e:
            # ORA-01918: user does not exist
            if e.args[0].code == 1918:
                print(f"User '{args.app_user}' did not exist. Creating fresh.")
            else:
                print(f"Error dropping user: {e}")
                raise
                
        # Create user
        cursor.execute(f"CREATE USER {args.app_user} IDENTIFIED BY {args.app_password}")
        print(f"Created user '{args.app_user}' successfully.")
        
        # Grant basic privileges
        privileges = [
            f"GRANT CONNECT TO {args.app_user}",
            f"GRANT RESOURCE TO {args.app_user}",
            f"GRANT CREATE TRIGGER TO {args.app_user}",
            f"GRANT CREATE VIEW TO {args.app_user}",
            f"GRANT UNLIMITED TABLESPACE TO {args.app_user}"
        ]
        
        for priv in privileges:
            cursor.execute(priv)
            print(f"Executed privilege grant: {priv}")
            
        admin_conn.commit()
        cursor.close()
        admin_conn.close()
        print(f"Schema user '{args.app_user}' created and configured successfully!")
        
    except Exception as e:
        print(f"\nFATAL: Failed during administrator setup: {e}")
        if admin_conn:
            admin_conn.close()
        sys.exit(1)
        
    # Step 2: Connect as the newly created App User and run schema.sql
    print(f"\nConnecting as application user '{args.app_user}' to run schema.sql...")
    app_conn = None
    try:
        app_conn = oracledb.connect(
            user=args.app_user,
            password=args.app_password,
            dsn=dsn
        )
        print("Connected successfully as app user!")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(script_dir, "schema.sql")
        
        run_sql_script(app_conn, schema_path)
        app_conn.close()
        print("\n=== SYSTEM CREATED & SEEDED SUCCESSFULLY ===")
        print(f"Username: {args.app_user}")
        print(f"Password: {args.app_password}")
        print("Default App Credentials seeded:")
        print(" - Admin user: 'admin' / 'admin123'")
        print(" - Manager user: 'manager' / 'manager123'")
        print(" - Staff 1: 'staff1' / 'staff123'")
        print("============================================\n")
        
    except Exception as e:
        print(f"\nFATAL: Failed during schema script execution: {e}")
        if app_conn:
            app_conn.close()
        sys.exit(1)

if __name__ == "__main__":
    main()
