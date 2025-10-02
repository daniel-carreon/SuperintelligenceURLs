"""
Apply Supabase Migration 002 - YouTube Analytics Enhancement
"""

import os
from supabase import create_client, Client

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def apply_migration():
    """Apply migration 002 to Supabase"""

    print("📦 Connecting to Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # Read migration file
    migration_path = "../supabase/migrations/002_youtube_analytics_enhancement.sql"
    print(f"📄 Reading migration from: {migration_path}")

    with open(migration_path, 'r') as f:
        migration_sql = f.read()

    print("🔧 Applying migration to Supabase...")
    print("=" * 60)

    try:
        # Execute SQL via Supabase RPC or direct query
        # Note: Supabase Python client doesn't support direct SQL execution
        # We'll need to use psycopg2 or execute via Supabase dashboard

        print("⚠️  Supabase Python client doesn't support raw SQL execution.")
        print("📋 Please apply migration manually via Supabase SQL Editor:")
        print()
        print("1. Go to: https://supabase.com/dashboard/project/hodawgekwhmbywubydau/sql")
        print("2. Copy the contents of: supabase/migrations/002_youtube_analytics_enhancement.sql")
        print("3. Paste and run in SQL Editor")
        print()
        print("Alternatively, use psql:")
        print("=" * 60)
        print(f"psql 'postgresql://postgres:[password]@db.hodawgekwhmbywubydau.supabase.co:5432/postgres' -f {migration_path}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    apply_migration()
