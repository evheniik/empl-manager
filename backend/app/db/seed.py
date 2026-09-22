import random

from faker import Faker
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.company import Company
from app.models.employee import Employee
from app.models.project import Project
from app.models.user import User

N_COMPANIES = 10
N_EMPLOYEES = 50
N_PROJECTS = 20


def ensure_admin(db: Session) -> None:
    existing = db.scalar(select(User).where(User.email == settings.ADMIN_EMAIL))
    if existing is not None:
        print(f"Admin user {settings.ADMIN_EMAIL} already exists, skipping.")
        return
    admin = User(
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
    )
    db.add(admin)
    db.commit()
    print(f"Admin user {settings.ADMIN_EMAIL} created.")


def seed() -> None:
    fake = Faker()
    Faker.seed(42)
    random.seed(42)

    db = SessionLocal()
    try:
        ensure_admin(db)

        companies_count = db.scalar(select(func.count()).select_from(Company)) or 0
        if companies_count > 0:
            print(
                f"Companies table already has {companies_count} rows, skipping seeding."
            )
            return

        companies = [
            Company(
                name=fake.unique.company(),
                description=fake.catch_phrase(),
                website=fake.url(),
            )
            for _ in range(N_COMPANIES)
        ]
        db.add_all(companies)
        db.flush()

        employees = [
            Employee(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                position=fake.job()[:100],
                company_id=random.choice(companies).id,
            )
            for _ in range(N_EMPLOYEES)
        ]
        db.add_all(employees)

        projects = [
            Project(
                name=fake.catch_phrase(),
                description=fake.text(max_nb_chars=200),
                company_id=random.choice(companies).id,
            )
            for _ in range(N_PROJECTS)
        ]
        db.add_all(projects)

        db.commit()
        print(
            f"Seeded {len(companies)} companies, "
            f"{len(employees)} employees, {len(projects)} projects."
        )
    finally:
        db.close()


def main() -> None:
    seed()


if __name__ == "__main__":
    main()
