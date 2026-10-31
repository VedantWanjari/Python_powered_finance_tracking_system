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

        if not User.query.filter_by(username="admin").first():
            admin_password = os.getenv("ADMIN_PASSWORD")
            if not admin_password:
                raise RuntimeError(
                    "ADMIN_PASSWORD must be set before creating the admin user."
                )
            admin = User(
                username="admin",
                email="admin@financetracker.local",
                role="admin",
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(" Default admin created. Use ADMIN_PASSWORD to log in.")
        else:
            print("Admin user already exists – skipping.")

        demo_password = os.getenv("DEMO_PASSWORD")
        demo = User.query.filter_by(username="demo").first()
        if not demo and demo_password:
            demo = User(
                username="demo",
                email="demo@financetracker.local",
                role="analyst",
            )
            demo.set_password(demo_password)
            db.session.add(demo)
            db.session.commit()
            print(" Demo user created. Use DEMO_PASSWORD to log in.")
        elif not demo:
            print("DEMO_PASSWORD not set – skipping demo user.")

        if demo and not Transaction.query.filter_by(user_id=demo.id).first():
            categories = {
                category.name: category
                for category in Category.query.filter_by(is_default=True).all()
            }
            today = datetime.date.today()
            for amount, transaction_type, category_name, day, description in DEMO_TRANSACTIONS:
                db.session.add(Transaction(
                    user_id=demo.id,
                    amount=amount,
                    transaction_type=transaction_type,
                    category_id=categories[category_name].id,
                    date=today - datetime.timedelta(days=day),
                    description=description,
                ))
            db.session.commit()
            print(" Demo transactions seeded.")
        elif demo:
            print("Demo transactions already exist – skipping.")

        print("\n Database setup complete! You can now run: python run.py")

if __name__ == "__main__":
    setup()
