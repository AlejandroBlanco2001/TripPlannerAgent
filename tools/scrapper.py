import logging
import sqlite3
import threading
from pathlib import Path
from fast_flights import FlightData, Passengers, Result, get_flights
from typing import Literal
from pydantic import ValidationError
from google.adk.tools import ToolContext

from cachetools import TTLCache, cached
from models.models import Flight


AIRPORTS_SQLITE_PATH = Path(__file__).resolve().parent.parent / "airports.sqlite"

_airports_conn: sqlite3.Connection | None = None
_airports_lock = threading.Lock()

Trip = Literal["one-way", "round-trip"]
_FlightsSeat = Literal["economy", "premium-economy", "business", "first"]

_SEAT_MAP: dict[str, _FlightsSeat] = {
    "economy": "economy",
    "premium-economy": "premium-economy",
    "business": "business",
    "first": "first",
}

logger = logging.getLogger(__name__)

def user_persona(user_persona: str, tool_context: ToolContext) -> dict:
    """Get the user's persona.
    """
    tool_context.state["user_persona"] = user_persona
    return {"status": "success", "user_persona": user_persona}


def user_selected_flight(flight_information: dict, tool_context: ToolContext) -> dict:
    """Confirm and store the flight the user has chosen.

    Call this tool once the user has explicitly selected a specific flight from
    the options presented. The selection is saved to session state so downstream
    agents (e.g. itinerary planner) can access it.

    Args:
        flight_information: The full flight details of the chosen flight.
        tool_context: ADK tool context used to persist the selection in session state.

    Returns:
        The confirmed flight information dict.
    """
    tool_context.state["selected_flight_information"] = flight_information
    return flight_information


def search_google_flights(
    origin: str,
    destination: str,
    date: str = "",
    trip: Trip = "one-way",
    return_date: str = "",
    adults: int = 1,
    children: int = 0,
    infants_in_seat: int = 0,
    infants_on_lap: int = 0,
    seat: _FlightsSeat = "economy",
    max_stops: int | None = None,
) -> Result | None:
    """Search for flights on Google Flights between two airports.

    This specifies the trip type (round-trip or one-way). Note that multi-city
    is not yet supported. Note that if you're having a round-trip, you need to
    add more than one item of flight data (in other words, 2+), so `return_date`
    is required when `trip` is "round-trip".

    Args:
        origin: IATA airport code for the departure airport (e.g. "PTY").
        destination: IATA airport code for the arrival airport (e.g. "JFK").
        date: Departure date in YYYY-MM-DD format. Defaults to today if not provided.
        trip: Trip type — "one-way" or "round-trip" (default "one-way").
        return_date: Return date in YYYY-MM-DD format, must be greater than departure_date. Required for round-trips; ignored for one-way.
        adults: Number of adult passengers (default 1).
        children: Number of child passengers (default 0).
        infants_in_seat: Number of infants occupying their own seat (default 0).
        infants_on_lap: Number of infants on a lap; must not exceed number of adults (default 0).
        seat: Cabin class — one of "economy", "premium_economy", "business", or "first" (default "economy").
        max_stops: Maximum number of stops allowed. Omit for no restriction (default None).

    Returns:
        A dict with the flight results, or a dict with "status": "error" and "error_message" on failure.
    """
    from datetime import date as date_type

    resolved_date = date_type.fromisoformat(date) if date else date_type.today()
    resolved_return_date = date_type.fromisoformat(return_date) if return_date else None

    try:
        flight = Flight(
            origin=origin,
            destination=destination,
            departure_date=resolved_date,
            trip=trip,
            return_date=resolved_return_date,
            adults=adults,
            children=children,
            infants_in_seat=infants_in_seat,
            infants_on_lap=infants_on_lap,
            seat=seat,
            max_stops=max_stops,
        )
    except ValidationError as e:
        errors = "; ".join(err["msg"] for err in e.errors())
        logger.error(f"Error validating flight: {errors}")
        return None

    flight_data = [
        FlightData(
            from_airport=flight.origin,
            to_airport=flight.destination,
            date=str(flight.departure_date),
        )
    ]
    if flight.trip == "round-trip":
        flight_data.append(
            FlightData(
                from_airport=flight.destination,
                to_airport=flight.origin,
                date=str(flight.return_date),
            )
        )

    try:
        seat: _FlightsSeat = _SEAT_MAP[flight.seat]
        result: Result = get_flights(
            flight_data=flight_data,
            trip=flight.trip,
            passengers=Passengers(
                adults=flight.adults,
                children=flight.children,
                infants_in_seat=flight.infants_in_seat,
                infants_on_lap=flight.infants_on_lap,
            ),
            seat=seat,
            fetch_mode="fallback",
        )
    except Exception as e:
        logger.error(
            f"Error fetching Google Flights ({origin} → {destination}, {date}): {e}"
        )
        return None

    return result


def open_airports_connection(path: Path | str) -> None:
    """Open a long-lived SQLite connection (call once at app startup)."""
    global _airports_conn
    close_airports_connection()
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Airports database not found: {p}")

    _airports_conn = sqlite3.connect(str(p.resolve()), check_same_thread=False)


def close_airports_connection() -> None:
    global _airports_conn
    if _airports_conn is not None:
        _airports_conn.close()
        _airports_conn = None


@cached(cache=TTLCache(maxsize=33, ttl=600))
def search_iata_code_airpots_city(city: str) -> str | dict:
    """
    Query the airports.sqlite database for the iata code of the first airport matching the city name.
    Uses the shared connection from open_airports_connection when set; otherwise opens per call.
    Returns the IATA code as a string, or an error dict if not found.
    """
    city_key = city.strip()

    if not city_key:
        return {"status": "error", "error_message": "Empty city name"}

    sql = (
        "SELECT iata FROM airports WHERE city = ? COLLATE NOCASE ORDER BY iata LIMIT 1"
    )

    if _airports_conn is not None:
        with _airports_lock:
            row = _airports_conn.execute(sql, (city_key,)).fetchone()
    else:
        if not AIRPORTS_SQLITE_PATH.is_file():
            return {
                "status": "error",
                "error_message": f"Database not found: {AIRPORTS_SQLITE_PATH}",
            }
        conn = sqlite3.connect(str(AIRPORTS_SQLITE_PATH.resolve()))
        try:
            row = conn.execute(sql, (city_key,)).fetchone()
        finally:
            conn.close()

    if row is None:
        return {
            "status": "error",
            "error_message": f"No airport found for city: {city_key!r}",
        }

    return row[0]
