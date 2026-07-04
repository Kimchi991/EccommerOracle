import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    user = os.getenv("DB_USER", "shop_user")
    password = os.getenv("DB_PASSWORD", "shop_pwd")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "1521")
    service_name = os.getenv("DB_SERVICE_NAME", "XE")
    
    dsn = f"{host}:{port}/{service_name}"
    
    print("==========================================================")
    print("       ORACLE DATABASE XE THIN CONNECTIVITY TEST")
    print("==========================================================")
    print(f"Target DSN : {dsn}")
    print(f"Target User: {user}")
    print("Connecting...")
    
    try:
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        print("\n[+] SUCCESS: Connection established to Oracle DB successfully!")
        
        cursor = conn.cursor()
        
        # Retrieve DB Version
        try:
            cursor.execute("SELECT banner_full FROM v$version")
            row = cursor.fetchone()
            print(f"[+] DB Version : {row[0]}")
        except Exception:
            try:
                cursor.execute("SELECT banner FROM v$version")
                row = cursor.fetchone()
                print(f"[+] DB Version : {row[0]}")
            except Exception as ex:
                print(f"[-] Could not query version banner: {ex}")
                
        # Retrieve active tables list
        cursor.execute("SELECT table_name FROM user_tables ORDER BY table_name")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"[+] Existing Tables: {', '.join(tables) if tables else 'No tables created yet.'}")
        
        cursor.close()
        conn.close()
        print("\nConnectivity checks complete. Your database configuration is ready!")
        print("==========================================================")
    except Exception as e:
        print("\n[-] CONNECTION FAILED!")
        print(f"Error Details: {e}")
        print("\nTroubleshooting Steps:")
        print("1. Open Windows 'Services' app (services.msc). Verify that 'OracleServiceXE'")
        print("   and 'OracleOraDB21Home2TNSListener' are running.")
        print("2. Verify your .env connection string properties match your database.")
        print("3. Ensure that you have run 'setup_db.py' first if you are checking tables.")
        print("==========================================================")

if __name__ == "__main__":
    test_connection()
