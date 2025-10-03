"""
Safely apply Supabase migration using Python
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def read_migration():
    """Read migration SQL file"""
    migration_path = "../supabase/migrations/002_youtube_analytics_enhancement.sql"

    with open(migration_path, 'r') as f:
        return f.read()

def apply_migration_via_rpc():
    """
    Apply migration using Supabase RPC

    Note: Supabase Python SDK doesn't support direct SQL execution.
    We need to use psycopg2 or execute via Supabase SQL Editor.
    """

    print("=" * 70)
    print("🔧 APPLYING MIGRATION TO SUPABASE")
    print("=" * 70)

    migration_sql = read_migration()

    # Count operations
    alter_count = migration_sql.count("ALTER TABLE")
    index_count = migration_sql.count("CREATE INDEX")
    view_count = migration_sql.count("CREATE MATERIALIZED VIEW")

    print(f"\n📋 Migration Summary:")
    print(f"   ALTER TABLE statements: {alter_count}")
    print(f"   CREATE INDEX statements: {index_count}")
    print(f"   CREATE MATERIALIZED VIEW statements: {view_count}")
    print()

    print("⚠️  Supabase Python client doesn't support raw SQL.")
    print("📝 You have 2 options:\n")

    print("OPTION 1: Via Supabase SQL Editor (RECOMMENDED)")
    print("-" * 70)
    print("1. Open: https://supabase.com/dashboard/project/hodawgekwhmbywubydau/sql")
    print("2. Copy migration file: supabase/migrations/002_youtube_analytics_enhancement.sql")
    print("3. Paste and click 'Run'")
    print()

    print("OPTION 2: Via psycopg2 (if installed)")
    print("-" * 70)
    print("Run: python apply_migration_psycopg2.py")
    print()

    print("=" * 70)

    # Try to use psycopg2 if available
    try:
        import psycopg2
        print("\n✅ psycopg2 is installed!")
        print("📝 Creating apply_migration_psycopg2.py...")

        create_psycopg2_script()

        print("\n🚀 Now run: python backend/apply_migration_psycopg2.py")

    except ImportError:
        print("\n⚠️  psycopg2 not installed")
        print("📝 Install with: pip install psycopg2-binary")
        print("    Then run: python backend/apply_migration_psycopg2.py")

def create_psycopg2_script():
    """Create script that uses psycopg2"""
    script = '''"""
Apply migration using psycopg2 direct connection
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Supabase connection details
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Extract project ref from URL
project_ref = SUPABASE_URL.split("//")[1].split(".")[0]

# Build connection string
# Format: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
DATABASE_URL = f"postgresql://postgres:{SUPABASE_SERVICE_KEY}@db.{project_ref}.supabase.co:5432/postgres"

def apply_migration():
    """Apply migration via direct DB connection"""

    migration_path = "../supabase/migrations/002_youtube_analytics_enhancement.sql"

    with open(migration_path, 'r') as f:
        migration_sql = f.read()

    print("🔗 Connecting to Supabase PostgreSQL...")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("✅ Connected!")
        print("📝 Executing migration...")

        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()

        print("✅ Migration applied successfully!")

        # Verify new columns
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'clicks'
            AND column_name IN ('video_id', 'hour_of_day', 'session_id')
        """)

        results = cursor.fetchall()
        print(f"\\n✅ Verified {len(results)} new columns:")
        for col_name, data_type in results:
            print(f"   - {col_name}: {data_type}")

        cursor.close()
        conn.close()

        print("\\n🎉 Migration complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    apply_migration()
'''

    with open("apply_migration_psycopg2.py", 'w') as f:
        f.write(script)

    print("✅ Created: backend/apply_migration_psycopg2.py")

if __name__ == "__main__":
    apply_migration_via_rpc()
