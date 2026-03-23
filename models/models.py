from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional
from datetime import date, datetime


class Flight(BaseModel):
    origin: str = Field(
        ..., description="IATA airport code for the departure airport (e.g. 'PTY')"
    )
    destination: str = Field(
        ..., description="IATA airport code for the arrival airport (e.g. 'JFK')"
    )
    departure_date: date = Field(
        ...,
        description="Departure date in YYYY-MM-DD format, must be today or in the future",
    )
    trip: Literal["one-way", "round-trip"] = Field(
        "one-way", description="Trip type — 'one-way' or 'round-trip'"
    )
    return_date: Optional[date] = Field(
        None,
        description="Return date in YYYY-MM-DD format, required for round-trips and must be after departure_date",
    )
    adults: int = Field(1, ge=1, description="Number of adult passengers")
    children: int = Field(0, ge=0, description="Number of child passengers")
    infants_in_seat: int = Field(
        0, ge=0, description="Number of infants occupying their own seat"
    )
    infants_on_lap: int = Field(0, ge=0, description="Number of infants on a lap")
    seat: Literal["economy", "premium_economy", "business", "first"] = Field(
        "economy", description="Cabin class"
    )
    max_stops: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum number of stops allowed (None for no restriction)",
    )

    @field_validator("departure_date")
    @classmethod
    def departure_must_be_future(cls, v: date) -> date:
        if v < datetime.now().date():
            raise ValueError("departure_date must be today or in the future")
        return v

    @model_validator(mode="after")
    def validate_trip_and_passengers(self) -> "Flight":
        if self.trip == "round-trip":
            if self.return_date is None:
                raise ValueError("return_date is required for round-trip searches")
            if self.return_date <= self.departure_date:
                raise ValueError("return_date must be after departure_date")

        if self.infants_on_lap > self.adults:
            raise ValueError("infants_on_lap must not exceed the number of adults")

        total_passengers = (
            self.adults + self.children + self.infants_in_seat + self.infants_on_lap
        )
        if total_passengers > 9:
            raise ValueError(f"Total passengers ({total_passengers}) must not exceed 9")

        return self
