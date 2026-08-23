"""Development-only seed/reset utility.

Recreates the local development test account:

    username: tester
    password: test1234
    email:    tester@beam.example.com

The email uses the IANA-reserved documentation domain (example.com) because
the API validates emails with pydantic's EmailStr, which rejects reserved
special-use TLDs such as `.local`.

The password is hashed with the same bcrypt mechanism used by the
authentication system (`app.core.security.get_password_hash`) - it is
never stored or logged in plaintext.

Behavior:
* `tester` exists      -> reset its password, reactivate, normalize email
* other dev/test users -> removed (testuser / devuser / test emails)
* `tester` missing     -> created fresh

Usage (from beam-api/):
    python scripts/seed_dev.py

Connection defaults to localhost; override via environment variables
(POSTGRES_SERVER / POSTGRES_PORT / DATABASE_URL) when needed - e.g.
POSTGRES_PORT=5433 for the docker-compose database on this machine.

NOTE: development use only. Never run against production data.
"""

import os
import sys

# Ensure we connect to localhost when running outside docker.
if not os.getenv("DATABASE_URL"):
    if not os.getenv("POSTGRES_SERVER") or os.getenv("POSTGRES_SERVER") == "postgres":
        os.environ["POSTGRES_SERVER"] = "localhost"

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.security import get_password_hash  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.models.user import User  # noqa: E402

TEST_USERNAME = "tester"
TEST_EMAIL = "tester@beam.example.com"
TEST_PASSWORD = "test1234"
OTHER_TEST_USERNAMES = ["testuser", "devuser"]
OTHER_TEST_EMAILS = ["test@beam.local", "tester@beam.local"]


def seed() -> int:
    db = SessionLocal()
    try:
        # First, find existing dev/test users we want to clean up or reset.
        target_usernames = [TEST_USERNAME] + OTHER_TEST_USERNAMES
        target_emails = [TEST_EMAIL] + OTHER_TEST_EMAILS

        try:
            existing_users = (
                db.query(User)
                .filter(
                    (User.username.in_(target_usernames)) | (User.email.in_(target_emails))
                )
                .all()
            )
        except Exception as error:
            print(
                "error: could not query users table - has the schema been created? "
                "Run 'alembic upgrade head' first."
            )
            print(f"detail: {type(error).__name__}")
            return 1

        found_tester = False

        for user in existing_users:
            if user.username == TEST_USERNAME:
                print(f"Resetting existing test account: {user.username} ({user.email})")
                user.hashed_password = get_password_hash(TEST_PASSWORD)
                user.is_active = True
                user.email = TEST_EMAIL
                found_tester = True
            else:
                print(f"Removing unrelated test account: {user.username} ({user.email})")
                db.delete(user)

        if not found_tester:
            print(f"Creating fresh test user: {TEST_USERNAME} ({TEST_EMAIL})")
            db.add(
                User(
                    username=TEST_USERNAME,
                    email=TEST_EMAIL,
                    hashed_password=get_password_hash(TEST_PASSWORD),
                    is_active=True,
                )
            )

        db.commit()

        total = db.query(User).count()
        print(f"Seed complete. Users in local dev database: {total}")
        return 0
    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")
        db.rollback()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(seed())
