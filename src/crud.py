"""
CRUD operations for vaccination coverage data.
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from src.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear,
    LocalAuthorityCoverage, EnglandTimeSeries
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
