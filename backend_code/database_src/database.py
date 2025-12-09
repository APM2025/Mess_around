"""
Database Connection and Session Management

Provides utilities for creating database sessions and managing connections.
Optimized for SQLite.

Requirements:
- DB-NFR-002: Configurable database credentials
- DB-NFR-001: Testable database operations
"""

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Engine
from pathlib import Path
from backend_code.database_src.models import create_database_engine, init_database, Base


def create_test_session(db_path: Path) -> Session:
    """
    Create a database session for testing
    
    Args:
        db_path: Path to SQLite database file (Path object or string)
    
    Returns:
        SQLAlchemy Session instance
    
    Creates a temporary database for testing.
    Tables are created automatically.
    """
    # Ensure path is a Path object
    if not isinstance(db_path, Path):
        db_path = Path(db_path)
    
    # Create parent directory if needed
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create engine and initialize schema
    engine = create_database_engine(f"sqlite:///{db_path}")
    init_database(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session


def create_production_session(database_path: str = "data/vaccination_coverage.db") -> Session:
    """
    Create a database session for production use
    
    Args:
        database_path: Path to SQLite database file
    
    Returns:
        SQLAlchemy Session instance
    
    For production use with persistent database.
    """
    db_path = Path(database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    engine = create_database_engine(f"sqlite:///{db_path}")
    init_database(engine)
    
    Session = sessionmaker(bind=engine)
    return Session()


def get_session(database_path: str = None) -> Session:
    """
    Get a database session (convenience function)
    
    Args:
        database_path: Optional path to database file
    
    Returns:
        SQLAlchemy Session instance
    """
    if database_path:
        return create_production_session(database_path)
    else:
        return create_production_session()
