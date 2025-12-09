"""
UK Vaccination Coverage Database Models

SQLAlchemy ORM models based on comprehensive data analysis.
Schema designed to handle:
- National aggregate data (UK/country level)
- Local authority (UTLA) data
- Time series historical data
- Special vaccination programs (HepB, BCG)

Data volumes:
- 163 geographic areas (4 countries, 9 regions, 150 UTLAs)
- 16 vaccines
- 4 age cohorts
- 17 financial years (2009-2025)
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text, ForeignKey,
    UniqueConstraint, CheckConstraint, event
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# =============================================================================
# REFERENCE TABLES (Dimensions)
# =============================================================================

class GeographicArea(Base):
    """
    Geographic entities: countries, regions, UTLAs
    
    Total: 163 areas
    - 4 countries (England, Scotland, Wales, NI)
    - 9 regions
    - 150 UTLAs
    """
    __tablename__ = 'geographic_areas'
    
    area_code = Column(String(20), primary_key=True)
    area_name = Column(Text, nullable=False)
    area_type = Column(Text, nullable=False)  # 'country', 'region', 'utla'
    parent_region_code = Column(String(20), ForeignKey('geographic_areas.area_code'))
    ods_code = Column(String(20))  # Organisation Data Service code
    notes = Column(Text)
    
    # Self-referential relationship
    parent_region = relationship("GeographicArea", remote_side=[area_code], backref="child_areas")
    
    # Relationships to fact tables
    national_coverage_records = relationship("NationalCoverage", back_populates="geographic_area")
    local_authority_records = relationship("LocalAuthorityCoverage", back_populates="geographic_area")
    regional_time_series = relationship("RegionalTimeSeries", back_populates="geographic_area")
    special_programs = relationship("SpecialProgram", back_populates="geographic_area")
    
    __table_args__ = (
        CheckConstraint("area_type IN ('country', 'region', 'utla')", name='check_area_type'),
    )


class Vaccine(Base):
    """
    Vaccine catalog
    
    Total: 16 vaccines including:
    - DTaP/IPV/Hib/HepB (6-in-1)
    - PCV, Rotavirus, MenB, MMR, etc.
    """
    __tablename__ = 'vaccines'
    
    vaccine_id = Column(Integer, primary_key=True, autoincrement=True)
    vaccine_code = Column(Text, unique=True, nullable=False)
    vaccine_name = Column(Text, nullable=False)
    vaccine_description = Column(Text)
    
    # Relationships
    national_coverage_records = relationship("NationalCoverage", back_populates="vaccine")
    local_authority_records = relationship("LocalAuthorityCoverage", back_populates="vaccine")
    england_time_series = relationship("EnglandTimeSeries", back_populates="vaccine")
    regional_time_series = relationship("RegionalTimeSeries", back_populates="vaccine")


class AgeCohort(Base):
    """
    Age cohorts for vaccination tracking
    
    Total: 4 cohorts
    - 12 months, 24 months, 5 years, 3 months (BCG)
    """
    __tablename__ = 'age_cohorts'
    
    cohort_id = Column(Integer, primary_key=True, autoincrement=True)
    cohort_name = Column(Text, unique=True, nullable=False)
    age_months = Column(Integer, nullable=False)
    birth_year_start = Column(Integer)
    birth_year_end = Column(Integer)
    description = Column(Text)
    
    # Relationships
    national_coverage_records = relationship("NationalCoverage", back_populates="age_cohort")
    local_authority_records = relationship("LocalAuthorityCoverage", back_populates="age_cohort")
    england_time_series = relationship("EnglandTimeSeries", back_populates="age_cohort")
    regional_time_series = relationship("RegionalTimeSeries", back_populates="age_cohort")
    special_programs = relationship("SpecialProgram", back_populates="age_cohort")


class FinancialYear(Base):
    """
    Financial years for data collection
    
    Total: 17 years (2009-2025)
    """
    __tablename__ = 'financial_years'
    
    year_id = Column(Integer, primary_key=True, autoincrement=True)
    year_label = Column(Text, unique=True, nullable=False)  # e.g., "2024-2025"
    year_start = Column(Integer, nullable=False)
    year_end = Column(Integer, nullable=False)
    evaluation_start_date = Column(Text)
    evaluation_end_date = Column(Text)
    
    # Relationships
    national_coverage_records = relationship("NationalCoverage", back_populates="financial_year")
    local_authority_records = relationship("LocalAuthorityCoverage", back_populates="financial_year")
    england_time_series = relationship("EnglandTimeSeries", back_populates="financial_year")
    regional_time_series = relationship("RegionalTimeSeries", back_populates="financial_year")
    special_programs = relationship("SpecialProgram", back_populates="financial_year")


# =============================================================================
# FACT TABLES (Measurements)
# =============================================================================

class NationalCoverage(Base):
    """
    Current year national/UK coverage data
    
    Data volume: ~70 records
    """
    __tablename__ = 'national_coverage'
    
    coverage_id = Column(Integer, primary_key=True, autoincrement=True)
    year_id = Column(Integer, ForeignKey('financial_years.year_id'), nullable=False)
    area_code = Column(String(20), ForeignKey('geographic_areas.area_code'), nullable=False)
    cohort_id = Column(Integer, ForeignKey('age_cohorts.cohort_id'), nullable=False)
    vaccine_id = Column(Integer, ForeignKey('vaccines.vaccine_id'), nullable=False)
    eligible_population = Column(Integer)
    vaccinated_count = Column(Integer)
    coverage_percentage = Column(Float)
    notes = Column(Text)
    
    # Relationships
    financial_year = relationship("FinancialYear", back_populates="national_coverage_records")
    geographic_area = relationship("GeographicArea", back_populates="national_coverage_records")
    age_cohort = relationship("AgeCohort", back_populates="national_coverage_records")
    vaccine = relationship("Vaccine", back_populates="national_coverage_records")
    
    __table_args__ = (
        UniqueConstraint('year_id', 'area_code', 'cohort_id', 'vaccine_id', 
                        name='unique_national_coverage'),
    )


class LocalAuthorityCoverage(Base):
    """
    Current year local authority (UTLA) coverage data
    
    Data volume: ~2,086 records
    """
    __tablename__ = 'local_authority_coverage'
    
    coverage_id = Column(Integer, primary_key=True, autoincrement=True)
    year_id = Column(Integer, ForeignKey('financial_years.year_id'), nullable=False)
    area_code = Column(String(20), ForeignKey('geographic_areas.area_code'), nullable=False)
    cohort_id = Column(Integer, ForeignKey('age_cohorts.cohort_id'), nullable=False)
    vaccine_id = Column(Integer, ForeignKey('vaccines.vaccine_id'), nullable=False)
    eligible_population = Column(Integer)
    vaccinated_count = Column(Integer)
    coverage_percentage = Column(Float)
    notes = Column(Text)
    
    # Relationships
    financial_year = relationship("FinancialYear", back_populates="local_authority_records")
    geographic_area = relationship("GeographicArea", back_populates="local_authority_records")
    age_cohort = relationship("AgeCohort", back_populates="local_authority_records")
    vaccine = relationship("Vaccine", back_populates="local_authority_records")
    
    __table_args__ = (
        UniqueConstraint('year_id', 'area_code', 'cohort_id', 'vaccine_id',
                        name='unique_local_authority_coverage'),
    )


class EnglandTimeSeries(Base):
    """
    Historical England coverage data (2009-2025)
    
    Data volume: ~205 records
    """
    __tablename__ = 'england_time_series'
    
    series_id = Column(Integer, primary_key=True, autoincrement=True)
    year_id = Column(Integer, ForeignKey('financial_years.year_id'), nullable=False)
    cohort_id = Column(Integer, ForeignKey('age_cohorts.cohort_id'), nullable=False)
    vaccine_id = Column(Integer, ForeignKey('vaccines.vaccine_id'), nullable=False)
    eligible_population = Column(Integer)
    vaccinated_count = Column(Integer)
    coverage_percentage = Column(Float)
    notes = Column(Text)
    
    # Relationships
    financial_year = relationship("FinancialYear", back_populates="england_time_series")
    age_cohort = relationship("AgeCohort", back_populates="england_time_series")
    vaccine = relationship("Vaccine", back_populates="england_time_series")
    
    __table_args__ = (
        UniqueConstraint('year_id', 'cohort_id', 'vaccine_id',
                        name='unique_england_time_series'),
    )


class RegionalTimeSeries(Base):
    """
    Regional coverage over time
    
    Data volume: Variable based on years and regions
    """
    __tablename__ = 'regional_time_series'
    
    series_id = Column(Integer, primary_key=True, autoincrement=True)
    year_id = Column(Integer, ForeignKey('financial_years.year_id'), nullable=False)
    area_code = Column(String(20), ForeignKey('geographic_areas.area_code'), nullable=False)
    cohort_id = Column(Integer, ForeignKey('age_cohorts.cohort_id'), nullable=False)
    vaccine_id = Column(Integer, ForeignKey('vaccines.vaccine_id'), nullable=False)
    eligible_population = Column(Integer)
    coverage_percentage = Column(Float)
    notes = Column(Text)
    
    # Relationships
    financial_year = relationship("FinancialYear", back_populates="regional_time_series")
    geographic_area = relationship("GeographicArea", back_populates="regional_time_series")
    age_cohort = relationship("AgeCohort", back_populates="regional_time_series")
    vaccine = relationship("Vaccine", back_populates="regional_time_series")
    
    __table_args__ = (
        UniqueConstraint('year_id', 'area_code', 'cohort_id', 'vaccine_id',
                        name='unique_regional_time_series'),
    )


class SpecialProgram(Base):
    """
    Special vaccination programs (Hepatitis B, BCG)
    
    Data volume: ~623 records
    """
    __tablename__ = 'special_programs'
    
    program_id = Column(Integer, primary_key=True, autoincrement=True)
    year_id = Column(Integer, ForeignKey('financial_years.year_id'), nullable=False)
    area_code = Column(String(20), ForeignKey('geographic_areas.area_code'), nullable=False)
    program_type = Column(Text, nullable=False)  # 'HepB' or 'BCG'
    cohort_id = Column(Integer, ForeignKey('age_cohorts.cohort_id'), nullable=False)
    eligible_population = Column(Integer)
    vaccinated_count = Column(Integer)
    coverage_percentage = Column(Float)
    coverage_range = Column(Text)  # For suppressed data (e.g., "35% to 69%")
    notes = Column(Text)
    
    # Relationships
    financial_year = relationship("FinancialYear", back_populates="special_programs")
    geographic_area = relationship("GeographicArea", back_populates="special_programs")
    age_cohort = relationship("AgeCohort", back_populates="special_programs")
    
    __table_args__ = (
        UniqueConstraint('year_id', 'area_code', 'program_type', 'cohort_id',
                        name='unique_special_program'),
        CheckConstraint("program_type IN ('HepB', 'BCG')", name='check_program_type'),
    )


# =============================================================================
# DATABASE UTILITY FUNCTIONS
# =============================================================================

def create_database_engine(database_url="sqlite:///data/vaccination_coverage.db"):
    """
    Create SQLAlchemy engine for SQLite database
    
    Args:
        database_url: SQLite connection string
    
    Returns:
        SQLAlchemy Engine instance
    """
    engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        connect_args={'check_same_thread': False}
    )
    
    # Enable foreign key constraints in SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    return engine


def init_database(engine):
    """
    Initialize database by creating all tables
    
    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(engine)


def drop_all_tables(engine):
    """
    Drop all tables (use with caution!)
    
    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.drop_all(engine)
