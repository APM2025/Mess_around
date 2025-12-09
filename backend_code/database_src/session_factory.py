"""
Database Session Factory

Factory pattern for creating database sessions with different configurations.
Simplifies session creation and makes testing easier.
"""

from pathlib import Path
from sqlalchemy.orm import Session, sessionmaker

from backend_code.database_src.models import create_database_engine, init_database


class DatabaseSessionFactory:
    """
    Factory for creating database sessions with different configurations.
    """
    
    @staticmethod
    def create_test_session(db_path: Path) -> Session:
        """
        Create isolated session for testing.
        
        Args:
            db_path: Path to temporary test database
        
        Returns:
            Configured Session instance
        """
        if not isinstance(db_path, Path):
            db_path = Path(db_path)
        
        db_path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_database_engine(f"sqlite:///{db_path}")
        init_database(engine)
        
        SessionClass = sessionmaker(bind=engine)
        return SessionClass()
    
    @staticmethod
    def create_production_session(database_path: str = "data/vaccination_coverage.db") -> Session:
        """
        Create session for production use.
        
        Args:
            database_path: Path to persistent database
        
        Returns:
            Configured Session instance
        """
        db_path = Path(database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        engine = create_database_engine(f"sqlite:///{db_path}")
        init_database(engine)
        
        SessionClass = sessionmaker(bind=engine)
        return SessionClass()
    
    @classmethod
    def get_session(cls, environment: str = "production", **kwargs) -> Session:
        """
        Unified session creation with environment selection.
        
        Args:
            environment: 'test' or 'production'
            **kwargs: Additional arguments for specific session types
                - db_path: for test environment
                - database_path: for production environment
        
        Returns:
            Session instance
        """
        if environment == "test":
            return cls.create_test_session(kwargs.get('db_path'))
        else:
            return cls.create_production_session(kwargs.get('database_path', "data/vaccination_coverage.db"))
