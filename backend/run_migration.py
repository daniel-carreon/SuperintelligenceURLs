"""
Apply YouTube Analytics Migration to Supabase
Uses psycopg2 for direct PostgreSQL connection
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Extract project ref from URL
project_ref = SUPABASE_URL.replace("https://", "").split(".")[0]

# Build PostgreSQL connection string
DATABASE_URL = f"postgresql://postgres:{SUPABASE_SERVICE_KEY}@db.{project_ref}.supabase.co:5432/postgres"

def read_migration():
    """Read migration SQL file"""
    migration_path = "../supabase/migrations/002_youtube_analytics_enhancement.sql"

    with open(migration_path, 'r') as f:
        return f.read()

def apply_migration():
    """Apply migration to Supabase"""

    print("=" * 70)
    print("🔧 APPLYING YOUTUBE ANALYTICS MIGRATION")
    print("=" * 70)

    # Read migration
    print("\n📄 Reading migration file...")
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

    # Connect to Supabase
    print("🔗 Connecting to Supabase PostgreSQL...")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("✅ Connected to Supabase!")

        # Execute migration
        print("\n📝 Executing migration SQL...")
        cursor.execute(migration_sql)
        conn.commit()

        print("✅ Migration applied successfully!")

        # Verify new columns exist
        print("\n🔍 Verifying new columns...")
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'clicks'
            AND column_name IN (
                'video_id', 'hour_of_day', 'session_id',
                'channel_id', 'day_of_week', 'is_returning_visitor',
                'viral_coefficient', 'yt_feature'
            )
            ORDER BY column_name
        """)

        results = cursor.fetchall()

        print(f"\n✅ Verified {len(results)} new columns in 'clicks' table:")
        for col_name, data_type in results:
            print(f"   ✓ {col_name}: {data_type}")

        # Verify materialized views
        print("\n🔍 Verifying materialized views...")
        cursor.execute("""
            SELECT matviewname
            FROM pg_matviews
            WHERE matviewname IN (
                'mv_top_youtube_videos',
                'mv_hour_heatmap',
                'mv_channel_performance'
            )
        """)

        views = cursor.fetchall()

        print(f"\n✅ Verified {len(views)} materialized views:")
        for (view_name,) in views:
            print(f"   ✓ {view_name}")

        # Close connection
        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print("🎉 MIGRATION COMPLETE!")
        print("=" * 70)

        print("\n📊 Next Steps:")
        print("   1. Integrate parsers in click tracking pipeline")
        print("   2. Test YouTube URL creation locally")
        print("   3. Verify analytics data saves correctly")
        print()

        return True

    except psycopg2.Error as e:
        print(f"\n❌ Database Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
