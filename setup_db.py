"""
setup_db.py
────────────
One-time database initialisation script.

Run this once after creating your MySQL database:
    python setup_db.py

It will:
  1. Create all tables
  2. Seed default categories
  3. Create a default admin user (admin / Admin@1234)
"""

from app import create_app, db
from app.models.user import User
from app.models.category import Category


def setup():
    """Initialise database, seed categories, create admin."""
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Tables created.")

        # ── Default categories ─────────────────────────────────────────────
        default_categories = [
            ("Food & Dining",  "Restaurants, groceries, delivery",      "#FF6B6B", "🍔"),
            ("Salary",         "Employment income and bonuses",          "#4ECDC4", "💰"),
            ("Transport",      "Fuel, public transit, rideshare",        "#45B7D1", "🚗"),
            ("Entertainment",  "Movies, concerts, subscriptions",        "#96CEB4", "🎬"),
            ("Utilities",      "Electricity, water, internet, phone",    "#FFEAA7", "⚡"),
            ("Healthcare",     "Doctor visits, medicine, gym",           "#DDA0DD", "🏥"),
            ("Shopping",       "Clothing, electronics, household",       "#98D8C8", "🛍️"),
            ("Savings",        "Investments, emergency fund deposits",   "#F7DC6F", "💎"),
            ("Rent/Mortgage",  "Housing payments",                       "#A29BFE", "🏠"),
            ("Education",      "Courses, books, tuition",                "#FD79A8", "📚"),
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
        print(f"✅ {created} default categories seeded.")

        # ── Default admin user ─────────────────────────────────────────────
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                email="admin@financetracker.local",
                role="admin",
            )
            admin.set_password("Admin@1234")   # change after first login!
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created → username: admin  password: Admin@1234")
            print("   ⚠️  Change the admin password immediately after first login!")
        else:
            print("ℹ️  Admin user already exists – skipping.")

        print("\n🎉 Database setup complete! You can now run: python run.py")


if __name__ == "__main__":
    setup()
