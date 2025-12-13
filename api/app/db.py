"""Database module for Agno agent persistence.

This module provides the PostgresDb connection for Agno agents to persist
sessions, memory, metrics, and knowledge in the Supabase `agno` schema.

Usage:
    from app.db import get_agno_db
    
    db = get_agno_db()
    if db:
        agent = Agent(db=db, ...)
"""

from functools import lru_cache
from typing import Optional

from agno.db.postgres import PostgresDb

from app.config import get_settings


@lru_cache
def get_agno_db() -> Optional[PostgresDb]:
    """
    Get a cached PostgresDb instance for Agno agents.
    
    Returns None if the required database credentials are not configured.
    The database connection uses the `agno` schema to keep agent data
    separate from application tables in the `public` schema.
    
    Tables created by Agno in the `agno` schema:
      - agno_sessions: Agent/Team/Workflow session data
      - agno_memory: Agent memory storage
      - agno_metrics: Execution metrics
      - agno_knowledge: Knowledge base content
    
    Returns:
        PostgresDb instance if configured, None otherwise
    """
    settings = get_settings()
    db_url = settings.supabase_db_url
    
    if not db_url:
        return None
    
    return PostgresDb(
        db_url=db_url,
        db_schema="agno",
    )

