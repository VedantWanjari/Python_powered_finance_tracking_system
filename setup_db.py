import os
import datetime

from app import create_app, db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction


DEMO_TRANSACTIONS = [
    (5000, "income", "Salary", 1, "Monthly salary"),
    (120, "expense", "Food & Dining", 3, "Groceries"),
    (50, "expense", "Transport", 5, "Bus pass"),
    (200, "expense", "Entertainment", 8, "Concert tickets"),
    (300, "expense", "Utilities", 12, "Electricity bill"),
    (150, "expense", "Shopping", 15, "Household items"),
]


DEMO_USERS = [
    ("admin", "admin@financetracker.local", "admin", "ADMIN_PASSWORD"),
    ("demo", "demo@financetracker.local", "analyst", "DEMO_PASSWORD"),
    ("viewer", "viewer@financetracker.local", "viewer", "VIEWER_PASSWORD"),
]


def seed_transactions(user, categories):
    if Transaction.query.filter_by(user_id=user.id).first():
        print(f"Transactions for {user.username} already exist – skipping.")
        return

    today = datetime.date.today()
    for amount, transaction_type, category_name, day, description in DEMO_TRANSACTIONS:
        db.session.add(Transaction(
            user_id=user.id,
            amount=amount,
            transaction_type=transaction_type,
            category_id=categories[category_name].id,
            date=today - datetime.timedelta(days=day),
            description=description,
        ))
    db.session.commit()
    print(f" Demo transactions seeded for {user.username}.")


def setup():
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print(" Tables created.")

        default_categories = [
            ("Food & Dining",  "Restaurants, groceries, delivery",      "#FF6B6B", ""),
            ("Salary",         "Employment income and bonuses",          "#4ECDC4", ""),
            ("Transport",      "Fuel, public transit, rideshare",        "#45B7D1", ""),
            ("Entertainment",  "Movies, concerts, subscriptions",        "#96CEB4", ""),
            ("Utilities",      "Electricity, water, internet, phone",    "#FFEAA7", ""),
            ("Healthcare",     "Doctor visits, medicine, gym",           "#DDA0DD", ""),
            ("Shopping",       "Clothing, electronics, household",       "#98D8C8", ""),
            ("Savings",        "Investments, emergency fund deposits",   "#F7DC6F", ""),
            ("Rent/Mortgage",  "Housing payments",                       "#A29BFE", ""),
            ("Education",      "Courses, books, tuition",                "#FD79A8", ""),
        ]

        created = 0
        for name, desc, color, icon in default_categories:
            if not Category.query.filter_by(name=name, is_default=True).first():
                cat = Category(
                    name=name, description=desc,
                    color=color, icon=icon, is_default=True,
                )
                db.session.add(cat)
                created += 1

        db.session.commit()
        print(f" {created} default categories seeded.")

        seeded_users = []
        for username, email, role, password_variable in DEMO_USERS:
            user = User.query.filter_by(username=username).first()
            password = os.getenv(password_variable)

            if not user and not password:
                if role == "admin":
                    raise RuntimeError(
                        f"{password_variable} must be set before creating the admin user."
                    )
                print(f"{password_variable} not set – skipping {role} demo user.")
                continue

            if not user:
                user = User(username=username, email=email, role=role)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                print(f" {role.title()} demo user created. Use {password_variable} to log in.")
            else:
                print(f"{username} user already exists – skipping.")
            seeded_users.append(user)

        categories = {
            category.name: category
            for category in Category.query.filter_by(is_default=True).all()
        }
        for user in seeded_users:
            seed_transactions(user, categories)

        print("\n Database setup complete! You can now run: python run.py")

if __name__ == "__main__":
    setup()
