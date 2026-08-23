"""B.E.A.M. AI workspace.

Dataset preparation and (future) modeling code. Independent from the
scraper (beam-scraper) and the API (beam-api): this package only consumes
raw dataset files / database rows as input.
"""

__version__ = "0.1.0"

# Bumped whenever preprocessing/feature logic changes in an observable way.
# Stored on every processed record so datasets remain auditable.
PROCESSING_VERSION = "prep-1.0.0"
