"""
CRUD operations for vaccination coverage data.
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Tuple

from src.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear,
    LocalAuthorityCoverage, NationalCoverage, EnglandTimeSeries
)


class VaccinationCRUD:
    """Manages Create, Read, Update, Delete operations for vaccination data."""

    def __init__(self, session: Session):
        """
        Initialize CRUD manager.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    # CREATE operations
    def create_geographic_area(
        self,
        area_code: str,
        area_name: str,
        area_type: str,
        parent_region_code: Optional[str] = None,
        ods_code: Optional[str] = None
    ) -> GeographicArea:
        """
        Create a new geographic area.

        Args:
            area_code: Unique area code
            area_name: Name of the area
            area_type: Type ('country', 'region', 'utla')
            parent_region_code: Optional parent region code
            ods_code: Optional ODS code

        Returns:
            Created GeographicArea object
        """
        area = GeographicArea(
            area_code=area_code,
            area_name=area_name,
            area_type=area_type,
            parent_region_code=parent_region_code,
            ods_code=ods_code
        )
        self.session.add(area)
        self.session.commit()
        return area

    def create_vaccine(
        self,
        vaccine_code: str,
        vaccine_name: str
    ) -> Vaccine:
        """
        Create a new vaccine.

        Args:
            vaccine_code: Unique vaccine code
            vaccine_name: Name of the vaccine

        Returns:
            Created Vaccine object
        """
        vaccine = Vaccine(
            vaccine_code=vaccine_code,
            vaccine_name=vaccine_name
        )
        self.session.add(vaccine)
        self.session.commit()
        return vaccine

    def create_coverage_record(
        self,
        area_code: str,
        vaccine_id: int,
        cohort_id: int,
        year_id: int,
        coverage_percentage: float,
        vaccinated_count: Optional[int] = None,
        eligible_population: Optional[int] = None,
        notes: Optional[str] = None
    ) -> LocalAuthorityCoverage:
        """
        Create a new coverage record.

        Args:
            area_code: Geographic area code
            vaccine_id: Vaccine ID
            cohort_id: Age cohort ID
            year_id: Financial year ID
            coverage_percentage: Coverage percentage
            vaccinated_count: Number vaccinated
            eligible_population: Total eligible population
            notes: Optional notes

        Returns:
            Created LocalAuthorityCoverage object
        """
        coverage = LocalAuthorityCoverage(
            area_code=area_code,
            vaccine_id=vaccine_id,
            cohort_id=cohort_id,
            year_id=year_id,
            coverage_percentage=coverage_percentage,
            vaccinated_count=vaccinated_count,
            eligible_population=eligible_population,
            notes=notes
        )
        self.session.add(coverage)
        self.session.commit()
        return coverage

    # READ operations
    def get_geographic_area(self, area_code: str) -> Optional[GeographicArea]:
        """
        Retrieve a geographic area by code.

        Args:
            area_code: Area code to look up

        Returns:
            GeographicArea object or None if not found
        """
        return self.session.query(GeographicArea).filter_by(
            area_code=area_code
        ).first()

    def get_vaccine(self, vaccine_code: str) -> Optional[Vaccine]:
        """
        Retrieve a vaccine by code.

        Args:
            vaccine_code: Vaccine code to look up

        Returns:
            Vaccine object or None if not found
        """
        return self.session.query(Vaccine).filter_by(
            vaccine_code=vaccine_code
        ).first()

    def get_all_vaccines(self) -> List[Vaccine]:
        """
        Retrieve all vaccines.

        Returns:
            List of all Vaccine objects
        """
        return self.session.query(Vaccine).all()

    def get_coverage_records(
        self,
        vaccine_code: Optional[str] = None,
        area_code: Optional[str] = None,
        cohort_id: Optional[int] = None,
        year_id: Optional[int] = None
    ) -> List[LocalAuthorityCoverage]:
        """
        Retrieve coverage records with optional filters.

        Args:
            vaccine_code: Filter by vaccine code
            area_code: Filter by area code
            cohort_id: Filter by cohort ID
            year_id: Filter by year ID

        Returns:
            List of matching LocalAuthorityCoverage objects
        """
        query = self.session.query(LocalAuthorityCoverage)

        if vaccine_code:
            # Join with Vaccine table to filter by code
            query = query.join(Vaccine).filter(
                Vaccine.vaccine_code == vaccine_code
            )

        if area_code:
            query = query.filter(LocalAuthorityCoverage.area_code == area_code)

        if cohort_id:
            query = query.filter(LocalAuthorityCoverage.cohort_id == cohort_id)

        if year_id:
            query = query.filter(LocalAuthorityCoverage.year_id == year_id)

        return query.all()

    # UPDATE operations
    def update_geographic_area(
        self,
        area_code: str,
        **kwargs
    ) -> Optional[GeographicArea]:
        """
        Update a geographic area.

        Args:
            area_code: Area code to update
            **kwargs: Fields to update (area_name, area_type, parent_region_code, ods_code)

        Returns:
            Updated GeographicArea object or None if not found
        """
        area = self.get_geographic_area(area_code)
        if not area:
            return None

        for key, value in kwargs.items():
            if hasattr(area, key):
                setattr(area, key, value)

        self.session.commit()
        return area

    def update_vaccine(
        self,
        vaccine_code: str,
        **kwargs
    ) -> Optional[Vaccine]:
        """
        Update a vaccine.

        Args:
            vaccine_code: Vaccine code to update
            **kwargs: Fields to update (vaccine_name)

        Returns:
            Updated Vaccine object or None if not found
        """
        vaccine = self.get_vaccine(vaccine_code)
        if not vaccine:
            return None

        for key, value in kwargs.items():
            if hasattr(vaccine, key):
                setattr(vaccine, key, value)

        self.session.commit()
        return vaccine

    def update_coverage_record(
        self,
        coverage_id: int,
        **kwargs
    ) -> Optional[LocalAuthorityCoverage]:
        """
        Update a coverage record.

        Args:
            coverage_id: Coverage ID to update
            **kwargs: Fields to update (coverage_percentage, vaccinated_count, eligible_population, notes)

        Returns:
            Updated LocalAuthorityCoverage object or None if not found
        """
        coverage = self.session.query(LocalAuthorityCoverage).filter_by(
            coverage_id=coverage_id
        ).first()

        if not coverage:
            return None

        for key, value in kwargs.items():
            if hasattr(coverage, key):
                setattr(coverage, key, value)

        self.session.commit()
        return coverage

    def get_coverage_by_keys(
        self,
        area_code: str,
        vaccine_id: int,
        cohort_id: int,
        year_id: int
    ) -> Optional[LocalAuthorityCoverage]:
        """
        Retrieve a coverage record by its unique keys.
        """
        return self.session.query(LocalAuthorityCoverage).filter_by(
            area_code=area_code,
            vaccine_id=vaccine_id,
            cohort_id=cohort_id,
            year_id=year_id
        ).first()

    # DELETE operations
    def delete_geographic_area(self, area_code: str) -> bool:
        """
        Delete a geographic area.

        Args:
            area_code: Area code to delete

        Returns:
            True if deleted, False if not found
        """
        area = self.get_geographic_area(area_code)
        if not area:
            return False

        self.session.delete(area)
        self.session.commit()
        return True

    def delete_vaccine(self, vaccine_code: str) -> bool:
        """
        Delete a vaccine.

        Args:
            vaccine_code: Vaccine code to delete

        Returns:
            True if deleted, False if not found
        """
        vaccine = self.get_vaccine(vaccine_code)
        if not vaccine:
            return False

        self.session.delete(vaccine)
        self.session.commit()
        return True

    def delete_coverage_record(self, coverage_id: int) -> bool:
        """
        Delete a coverage record.

        Args:
            coverage_id: Coverage ID to delete

        Returns:
            True if deleted, False if not found
        """
        coverage = self.session.query(LocalAuthorityCoverage).filter_by(
            coverage_id=coverage_id
        ).first()

        if not coverage:
            return False

        self.session.delete(coverage)
        self.session.commit()
        return True

    # Bulk Row Operations (for frontend table editing)
    def update_row_vaccines(
        self,
        area_code: str,
        cohort_name: str,
        year: int,
        vaccine_updates: List[Dict[str, Any]]
    ) -> int:
        """
        Update multiple vaccine records for a single area/cohort/year.
        
        This method handles the complete workflow for editing a row in the table:
        - Resolves references (year, cohort, area)
        - Determines correct table (National vs LocalAuthority)
        - For each vaccine: resolves vaccine ID, calculates coverage, upserts record
        
        Args:
            area_code: Geographic area code  
            cohort_name: Age cohort name (e.g., '24 months')
            year: Financial year start (e.g., 2024)
            vaccine_updates: List of dicts with keys:
                - vaccine_code: str
                - eligible_population: int or str or None
                - vaccinated_count: int or str or None
                - coverage_percentage: float or str or None (fallback if counts missing)
        
        Returns:
            Number of records successfully updated/created
            
        Raises:
            ValueError: If reference data (year, cohort, area) is invalid
        
        Example:
            >>> updates = [
            ...     {'vaccine_code': 'MMR1', 'eligible_population': 1000, 'vaccinated_count': 950},
            ...     {'vaccine_code': 'DTaP/IPV/Hib', 'eligible_population': 1000, 'vaccinated_count': 980}
            ... ]
            >>> count = crud.update_row_vaccines('E12000001', '24 months', 2024, updates)
        """
        # Resolve references
        year_obj = self.session.query(FinancialYear).filter_by(year_start=year).first()
        cohort = self.session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
        area = self.session.query(GeographicArea).filter_by(area_code=area_code).first()
        
        if not all([year_obj, cohort, area]):
            raise ValueError("Invalid reference data: year, cohort, or area not found")
        
        # Determine coverage model based on area type
        is_national = area.area_type in ['country', 'uk']
        CoverageModel = NationalCoverage if is_national else LocalAuthorityCoverage
        
        success_count = 0
        
        for item in vaccine_updates:
            # Resolve vaccine with fuzzy matching
            vaccine = self._resolve_vaccine(item.get('vaccine_code'))
            if not vaccine:
                # Skip invalid vaccines (already logged in _resolve_vaccine)
                continue
            
            # Calculate coverage percentage from inputs
            eligible, vaccinated, coverage_pct = self._calculate_coverage(
                item.get('eligible_population'),
                item.get('vaccinated_count'),
                item.get('coverage_percentage')
            )
            
            # Upsert (update or insert) the coverage record
            self._upsert_coverage(
                CoverageModel,
                area_code=area_code,
                vaccine_id=vaccine.vaccine_id,
                cohort_id=cohort.cohort_id,
                year_id=year_obj.year_id,
                eligible=eligible,
                vaccinated=vaccinated,
                coverage_pct=coverage_pct
            )
            success_count += 1
        
        # Commit all changes at once (transaction)
        self.session.commit()
        # Clear session cache to ensure fresh data on next query
        self.session.expire_all()
        
        return success_count

    def _resolve_vaccine(self, vaccine_code: str) -> Optional[Vaccine]:
        """
        Resolve vaccine by code with fuzzy matching.
        
        Handles common variations like DTaP/IPV/Hib vs DTaP_IPV_Hib.
        
        Args:
            vaccine_code: Vaccine code to resolve
            
        Returns:
            Vaccine object if found, None otherwise
        """
        if not vaccine_code:
            return None
            
        # Try exact match first
        vaccine = self.session.query(Vaccine).filter_by(vaccine_code=vaccine_code).first()
        
        # If not found and code contains underscore, try replacing with slash
        if not vaccine and '_' in vaccine_code and '/' not in vaccine_code:
            alt_code = vaccine_code.replace('_', '/')
            vaccine = self.session.query(Vaccine).filter_by(vaccine_code=alt_code).first()
        
        return vaccine

    def _calculate_coverage(
        self,
        eligible: Any,
        vaccinated: Any,
        coverage_pct: Any
    ) -> Tuple[Optional[int], Optional[int], float]:
        """
        Calculate coverage percentage from inputs.
        
        Handles various input formats (empty strings, None, numbers).
        Calculates percentage from counts if available, otherwise uses provided percentage.
        
        Args:
            eligible: Eligible population (may be int, str, or None)
            vaccinated: Vaccinated count (may be int, str, or None)
            coverage_pct: Coverage percentage (may be float, str, or None)
            
        Returns:
            Tuple of (eligible_int, vaccinated_int, coverage_percentage_float)
        """
        # Handle empty strings/nulls by converting to None
        if eligible == '':
            eligible = None
        if vaccinated == '':
            vaccinated = None
        
        # Convert to integers if present
        if eligible is not None:
            eligible = int(eligible)
        if vaccinated is not None:
            vaccinated = int(vaccinated)
        
        # Calculate percentage from counts if available
        if eligible and vaccinated is not None and eligible > 0:
            calculated_pct = (vaccinated / eligible) * 100
            return eligible, vaccinated, calculated_pct
        
        # Otherwise use provided percentage (if available)
        elif coverage_pct not in [None, '']:
            return eligible, vaccinated, float(coverage_pct)
        
        # Default to 0% if no data
        else:
            return eligible, vaccinated, 0.0

    def _upsert_coverage(
        self,
        CoverageModel,
        area_code: str,
        vaccine_id: int,
        cohort_id: int,
        year_id: int,
        eligible: Optional[int],
        vaccinated: Optional[int],
        coverage_pct: float
    ):
        """
        Update existing coverage record or create new one.
        
        Args:
            CoverageModel: Either NationalCoverage or LocalAuthorityCoverage class
            area_code: Geographic area code
            vaccine_id: Vaccine ID
            cohort_id: Age cohort ID
            year_id: Financial year ID
            eligible: Eligible population count
            vaccinated: Vaccinated count
            coverage_pct: Coverage percentage
        """
        # Find existing record
        existing = self.session.query(CoverageModel).filter_by(
            area_code=area_code,
            vaccine_id=vaccine_id,
            cohort_id=cohort_id,
            year_id=year_id
        ).first()
        
        if existing:
            # Update existing record
            existing.eligible_population = eligible
            existing.vaccinated_count = vaccinated
            existing.coverage_percentage = coverage_pct
        else:
            # Create new record only if we have actual data
            if eligible is not None or vaccinated is not None:
                new_record = CoverageModel(
                    area_code=area_code,
                    vaccine_id=vaccine_id,
                    cohort_id=cohort_id,
                    year_id=year_id,
                    eligible_population=eligible,
                    vaccinated_count=vaccinated,
                    coverage_percentage=coverage_pct
                )
                self.session.add(new_record)

    def upsert_coverage_by_codes(
        self,
        area_code: str,
        vaccine_code: str,
        cohort_name: str,
        year: int,
        eligible_population: Optional[int] = None,
        vaccinated_count: Optional[int] = None,
        coverage_percentage: Optional[float] = None
    ):
        """
        Create or update a single coverage record using human-readable codes.
        
        This is a convenience method that resolves codes to IDs and handles upsert logic.
        
        Args:
            area_code: Geographic area code
            vaccine_code: Vaccine code (e.g., 'MMR1')
            cohort_name: Age cohort name (e.g., '24 months')
            year: Financial year start (e.g., 2024)
            eligible_population: Eligible population count
            vaccinated_count: Vaccinated count
            coverage_percentage: Coverage percentage
            
        Returns:
            Created or updated coverage record
            
        Raises:
            ValueError: If any reference data (year, cohort, vaccine, area) is invalid
        """
        # Resolve references
        year_obj = self.session.query(FinancialYear).filter_by(year_start=year).first()
        cohort = self.session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
        vaccine = self.session.query(Vaccine).filter_by(vaccine_code=vaccine_code).first()
        
        if not all([year_obj, cohort, vaccine, area_code]):
            raise ValueError("Invalid reference data: year, cohort, vaccine, or area not found")
        
        # Check if exists
        existing = self.get_coverage_by_keys(
            area_code=area_code,
            vaccine_id=vaccine.vaccine_id,
            cohort_id=cohort.cohort_id,
            year_id=year_obj.year_id
        )
        
        if existing:
            # Update
            return self.update_coverage_record(
                coverage_id=existing.coverage_id,
                eligible_population=eligible_population,
                vaccinated_count=vaccinated_count,
                coverage_percentage=coverage_percentage
            )
        else:
            # Create
            return self.create_coverage_record(
                area_code=area_code,
                vaccine_id=vaccine.vaccine_id,
                cohort_id=cohort.cohort_id,
                year_id=year_obj.year_id,
                eligible_population=eligible_population,
                vaccinated_count=vaccinated_count,
                coverage_percentage=coverage_percentage
            )

    def delete_coverage_by_codes(
        self,
        area_code: str,
        vaccine_code: str,
        cohort_name: str,
        year: int
    ) -> bool:
        """
        Delete a coverage record using human-readable codes.
        
        Args:
            area_code: Geographic area code
            vaccine_code: Vaccine code
            cohort_name: Age cohort name  
            year: Financial year start
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValueError: If reference data invalid
        """
        # Resolve references
        year_obj = self.session.query(FinancialYear).filter_by(year_start=year).first()
        cohort = self.session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
        vaccine = self.session.query(Vaccine).filter_by(vaccine_code=vaccine_code).first()
        
        if not all([year_obj, cohort, vaccine, area_code]):
            raise ValueError("Invalid reference data")
        
        # Find and delete
        existing = self.get_coverage_by_keys(
            area_code=area_code,
            vaccine_id=vaccine.vaccine_id,
            cohort_id=cohort.cohort_id,
            year_id=year_obj.year_id
        )
        
        if existing:
            return self.delete_coverage_record(existing.coverage_id)
        
        return False
