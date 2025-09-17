# supabase_handler.py

"""
Supabase Database Handler for Crawl4AI Integration

Based on production patterns from supa-crawl-chat project:
https://github.com/bigsk1/supa-crawl-chat

This handler uses direct PostgreSQL connections via psycopg2 rather than
the Supabase Python client library, following proven production patterns.
"""

import os
import uuid
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import Json
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database connection configuration"""

    host: str
    port: int
    database: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create config from environment variables"""
        # Support both direct connection and Supabase URL parsing
        supabase_url = os.getenv("SUPABASE_URL")

        if supabase_url and "://" in supabase_url:
            # Parse full URL
            from urllib.parse import urlparse

            parsed = urlparse(supabase_url)
            host = parsed.hostname
            port = parsed.port or 5432
        elif supabase_url:
            # Handle host:port format
            parts = supabase_url.split(":")
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 5432
        else:
            # Use individual components
            host = os.getenv("SUPABASE_HOST", "localhost")
            port = int(os.getenv("SUPABASE_PORT", "5432"))

        return cls(
            host=host,
            port=port,
            database=os.getenv("SUPABASE_DB", "postgres"),
            user=os.getenv("SUPABASE_KEY", "postgres"),
            password=os.getenv("SUPABASE_PASSWORD", "postgres"),
        )


class SupabaseHandler:
    """
    Production-ready Supabase handler for Crawl4AI integration.

    Follows patterns from supa-crawl-chat for proven reliability:
    - Direct PostgreSQL connections via psycopg2
    - Proper connection management with context managers
    - Error handling and logging
    - Schema-aware operations
    """

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize handler with database configuration"""
        self.config = config or DatabaseConfig.from_env()
        self._test_connection()

    def _get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password,
        )

    def _test_connection(self):
        """Test database connection on initialization"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            print(
                f"✅ Database connection successful: {self.config.host}:{self.config.port}"
            )
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise

    # ==================== EXTRACTION SCHEMAS ====================

    def get_extraction_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get extraction schema by name"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, description, base_url, patterns, usage_count, last_used_at
                    FROM extraction_schemas 
                    WHERE name = %s
                    """,
                    (name,),
                )
                row = cur.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "base_url": row[3],
                        "patterns": row[4],
                        "usage_count": row[5],
                        "last_used_at": row[6],
                    }
        return None

    def save_extraction_schema(
        self, name: str, description: str, base_url: str, patterns: Dict[str, Any]
    ) -> str:
        """Save or update extraction schema"""
        schema_id = str(uuid.uuid4())

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO extraction_schemas (id, name, description, base_url, patterns)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        description = EXCLUDED.description,
                        base_url = EXCLUDED.base_url,
                        patterns = EXCLUDED.patterns,
                        updated_at = now()
                    RETURNING id
                    """,
                    (schema_id, name, description, base_url, Json(patterns)),
                )
                result = cur.fetchone()
                return result[0] if result else schema_id

    def increment_schema_usage(self, schema_id: str):
        """Increment usage count for schema"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE extraction_schemas 
                    SET usage_count = COALESCE(usage_count, 0) + 1,
                        last_used_at = now()
                    WHERE id = %s
                    """,
                    (schema_id,),
                )

    # ==================== CRAWL JOBS ====================

    def create_crawl_job(
        self,
        url: str,
        extraction_schema_id: Optional[str] = None,
        priority: str = "normal",
        crawl_config: Optional[Dict] = None,
        extraction_config: Optional[Dict] = None,
    ) -> str:
        """Create a new crawl job"""
        job_id = str(uuid.uuid4())

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO crawl_jobs (
                        id, url, extraction_schema_id, priority, 
                        crawl_config, extraction_config
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        job_id,
                        url,
                        extraction_schema_id,
                        priority,
                        Json(crawl_config or {}),
                        Json(extraction_config or {}),
                    ),
                )
                result = cur.fetchone()
                return result[0]

    def update_job_status(
        self,
        job_id: str,
        status: str,
        error_message: Optional[str] = None,
        error_details: Optional[Dict] = None,
    ):
        """Update crawl job status"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                if status == "running":
                    cur.execute(
                        """
                        UPDATE crawl_jobs 
                        SET status = %s, started_at = now(), updated_at = now()
                        WHERE id = %s
                        """,
                        (status, job_id),
                    )
                elif status == "completed":
                    cur.execute(
                        """
                        UPDATE crawl_jobs 
                        SET status = %s, completed_at = now(), updated_at = now()
                        WHERE id = %s
                        """,
                        (status, job_id),
                    )
                elif status == "failed":
                    cur.execute(
                        """
                        UPDATE crawl_jobs 
                        SET status = %s, error_message = %s, error_details = %s, 
                            completed_at = now(), updated_at = now()
                        WHERE id = %s
                        """,
                        (status, error_message, Json(error_details or {}), job_id),
                    )

    def link_job_to_result(self, job_id: str, result_id: int):
        """Link crawl job to its result"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE crawl_jobs SET result_id = %s WHERE id = %s",
                    (result_id, job_id),
                )

    # ==================== CRAWL RESULTS ====================

    def save_crawl_result(
        self,
        url: str,
        title: Optional[str],
        content: str,
        metadata: Dict[str, Any],
        extraction_data: Optional[Dict] = None,
        extraction_schema_id: Optional[str] = None,
        extraction_quality: Optional[float] = None,
        schema_match_score: Optional[float] = None,
    ) -> int:
        """Save crawl result to database"""

        # Calculate content metrics
        content_length = len(content) if content else 0
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        content_hash_int = int(content_hash[:16], 16)  # Convert to bigint

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO crawl_results (
                        url, title, content, metadata, extraction_data,
                        content_length, content_hash, extraction_schema_id,
                        extraction_quality, schema_match_score
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        extraction_data = EXCLUDED.extraction_data,
                        content_length = EXCLUDED.content_length,
                        content_hash = EXCLUDED.content_hash,
                        extraction_schema_id = EXCLUDED.extraction_schema_id,
                        extraction_quality = EXCLUDED.extraction_quality,
                        schema_match_score = EXCLUDED.schema_match_score,
                        updated_at = now()
                    RETURNING id
                    """,
                    (
                        url,
                        title,
                        content,
                        Json(metadata),
                        Json(extraction_data or {}),
                        content_length,
                        content_hash_int,
                        extraction_schema_id,
                        extraction_quality,
                        schema_match_score,
                    ),
                )
                result = cur.fetchone()
                return result[0]

    def get_crawl_result(self, url: str) -> Optional[Dict[str, Any]]:
        """Get crawl result by URL"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, url, title, content, metadata, extraction_data,
                           crawled_at, content_length, extraction_quality, schema_match_score
                    FROM crawl_results 
                    WHERE url = %s
                    """,
                    (url,),
                )
                row = cur.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "url": row[1],
                        "title": row[2],
                        "content": row[3],
                        "metadata": row[4],
                        "extraction_data": row[5],
                        "crawled_at": row[6],
                        "content_length": row[7],
                        "extraction_quality": row[8],
                        "schema_match_score": row[9],
                    }
        return None

    # ==================== SEARCH & ANALYTICS ====================

    def search_results(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search crawl results by text"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, url, title, content, metadata, extraction_data, crawled_at,
                           ts_rank_cd(
                               to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(content, '')), 
                               plainto_tsquery('english', %s)
                           ) AS rank
                    FROM crawl_results
                    WHERE to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(content, '')) 
                          @@ plainto_tsquery('english', %s)
                    ORDER BY rank DESC
                    LIMIT %s
                    """,
                    (query, query, limit),
                )

                results = []
                for row in cur.fetchall():
                    results.append(
                        {
                            "id": row[0],
                            "url": row[1],
                            "title": row[2],
                            "content": row[3][:500] + "..."
                            if len(row[3]) > 500
                            else row[3],
                            "metadata": row[4],
                            "extraction_data": row[5],
                            "crawled_at": row[6],
                            "rank": float(row[7]),
                        }
                    )
                return results

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Get counts
                cur.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM crawl_results) as total_results,
                        (SELECT COUNT(*) FROM crawl_jobs) as total_jobs,
                        (SELECT COUNT(*) FROM extraction_schemas) as total_schemas,
                        (SELECT COUNT(*) FROM crawl_jobs WHERE status = 'completed') as completed_jobs,
                        (SELECT COUNT(*) FROM crawl_jobs WHERE status = 'failed') as failed_jobs,
                        (SELECT AVG(content_length) FROM crawl_results) as avg_content_length
                """)
                row = cur.fetchone()

                return {
                    "total_results": row[0],
                    "total_jobs": row[1],
                    "total_schemas": row[2],
                    "completed_jobs": row[3],
                    "failed_jobs": row[4],
                    "avg_content_length": float(row[5]) if row[5] else 0,
                }

    # ==================== UTILITY METHODS ====================

    def check_health(self) -> Dict[str, Any]:
        """Check database health and connectivity"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Check basic connectivity
                    cur.execute("SELECT version()")
                    version = cur.fetchone()[0]

                    # Check extensions
                    cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                    has_vector = cur.fetchone() is not None

                    return {
                        "status": "healthy",
                        "postgres_version": version,
                        "vector_extension": has_vector,
                        "connection_config": {
                            "host": self.config.host,
                            "port": self.config.port,
                            "database": self.config.database,
                            "user": self.config.user,
                        },
                    }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# ==================== INTEGRATION FUNCTIONS ====================


async def crawl_with_schema(
    handler: SupabaseHandler, url: str, schema_name: str
) -> Optional[int]:
    """
    Integration function: Crawl a URL using a predefined schema

    This combines our crawl4ai scripts with the Supabase handler for
    a complete crawling pipeline.
    """
    from schema_crawler import run_schema_crawl
    import json

    print(f"🚀 Starting schema-based crawl for: {url}")

    # Get extraction schema
    schema_data = handler.get_extraction_schema(schema_name)
    if not schema_data:
        print(f"❌ Schema '{schema_name}' not found")
        return None

    # Create crawl job
    job_id = handler.create_crawl_job(
        url=url,
        extraction_schema_id=schema_data["id"],
        crawl_config={"schema_name": schema_name},
    )

    try:
        # Update job status to running
        handler.update_job_status(job_id, "running")

        # Perform crawl
        extraction_result = await run_schema_crawl(url, schema_data["patterns"])

        if extraction_result:
            # Calculate quality metrics
            extraction_quality = 1.0 if extraction_result else 0.0
            schema_match_score = 0.95  # Would be calculated based on schema matching

            # Save result
            result_id = handler.save_crawl_result(
                url=url,
                title=extraction_result[0].get("title") if extraction_result else None,
                content=json.dumps(extraction_result),
                metadata={
                    "crawl_method": "schema_based",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                extraction_data=extraction_result,
                extraction_schema_id=schema_data["id"],
                extraction_quality=extraction_quality,
                schema_match_score=schema_match_score,
            )

            # Link job to result and mark complete
            handler.link_job_to_result(job_id, result_id)
            handler.update_job_status(job_id, "completed")
            handler.increment_schema_usage(schema_data["id"])

            print(f"✅ Successfully crawled {url} - Result ID: {result_id}")
            return result_id
        else:
            handler.update_job_status(job_id, "failed", "No extraction result")
            return None

    except Exception as e:
        handler.update_job_status(job_id, "failed", str(e), {"traceback": str(e)})
        print(f"❌ Crawl failed for {url}: {e}")
        return None


if __name__ == "__main__":
    """Test the Supabase handler"""

    print("🧪 Testing Supabase Handler...")

    # Initialize handler
    handler = SupabaseHandler()

    # Test health check
    health = handler.check_health()
    print(f"Database Health: {health}")

    # Test stats
    stats = handler.get_stats()
    print(f"Database Stats: {stats}")

    print("✅ Supabase Handler test complete!")
