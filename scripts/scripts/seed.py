"""Create two demonstration users and a few tasks (safe to run repeatedly)."""

import os

from sqlalchemy import select

from app.db.session import SessionLocal
from app.infrastructure.security import hash_password
from app.models.task import Task
from app.models.user import User


def get_or_create_user(db, email: str, password: str) -> User:
    email = email.lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, hashed_password=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def main() -> None:
    required = ("SEED_USER1_EMAIL", "SEED_USER1_PASSWORD", "SEED_USER2_EMAIL", "SEED_USER2_PASSWORD")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing seed environment variables: {', '.join(missing)}")

    user1_email = os.environ["SEED_USER1_EMAIL"]
    user1_password = os.environ["SEED_USER1_PASSWORD"]
    user2_email = os.environ["SEED_USER2_EMAIL"]
    user2_password = os.environ["SEED_USER2_PASSWORD"]

    with SessionLocal() as db:
        first = get_or_create_user(db, user1_email, user1_password)
        second = get_or_create_user(db, user2_email, user2_password)

        for user, title, description, task_status in [
            (first, "Review API requirements", "Check the Week 3 brief", "todo"),
            (first, "Build task endpoints", "Implement and test CRUD", "in_progress"),
            (second, "Explore FastAPI", "Read the official tutorial", "todo"),
        ]:
            existing = db.scalar(
                select(Task).where(Task.user_id == user.id, Task.title == title)
            )
            if existing is None:
                db.add(
                    Task(
                        user_id=user.id,
                        title=title,
                        description=description,
                        status=task_status,
                    )
                )
        db.commit()

    print("Seed complete: two users and demonstration tasks are available.")


if __name__ == "__main__":
    main()
