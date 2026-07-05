"""DataSource — abstract base for all data-acquisition abstractions."""

from abc import ABC


class DataSource(ABC):
    """Common marker base for all data-acquisition sources.

    Subclass via the appropriate specialisation:
    - ``JsonDataSource`` — REST JSON APIs (OpenF1, Jolpica, …)
    - ``HtmlDataSource`` — HTML page scraping (WEC, ELMS, …)
    - ``IcsDataSource`` — iCalendar / ICS feeds
    """
