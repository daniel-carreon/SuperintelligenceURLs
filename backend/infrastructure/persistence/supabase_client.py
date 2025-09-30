"""
Supabase Client Singleton
Provides centralized access to Supabase database and storage
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseClient:
    """
    Singleton Supabase client for database operations
    """
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        """Initialize Supabase client with credentials from environment"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY (or SUPABASE_ANON_KEY) "
                "must be set in environment variables"
            )

        self._client = create_client(supabase_url, supabase_key)
        print(f" Supabase client initialized: {supabase_url}")

    @property
    def client(self) -> Client:
        """Get Supabase client instance"""
        if self._client is None:
            self._initialize_client()
        return self._client

    def get_table(self, table_name: str):
        """
        Get table reference for queries

        Args:
            table_name: Name of the table

        Returns:
            Table reference for chaining queries
        """
        return self.client.table(table_name)

    def execute_rpc(self, function_name: str, params: dict = None):
        """
        Execute a Postgres RPC function

        Args:
            function_name: Name of the stored procedure
            params: Parameters to pass to the function

        Returns:
            Function execution result
        """
        return self.client.rpc(function_name, params or {})


# Singleton instance for global use
supabase_client = SupabaseClient()


def get_supabase() -> Client:
    """
    Convenience function to get Supabase client

    Returns:
        Supabase client instance
    """
    return supabase_client.client


if __name__ == "__main__":
    # Test connection
    try:
        client = get_supabase()
        # Try a simple query
        response = client.table('urls').select('*').limit(1).execute()
        print(f" Connection successful! URLs in database: {len(response.data)}")
    except Exception as e:
        print(f"L Connection failed: {e}")