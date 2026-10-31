import os
import click
from flask.cli import with_appcontext
from app import create_app, db

app = create_app()

@app.cli.command("init-db")
@with_appcontext
def init_db():
    db.create_all()
    click.echo(" Database tables created.")

@app.cli.command("create-admin")
@with_appcontext
def create_admin():
    from app.models.user import User

    username = click.prompt("Admin username")
    email    = click.prompt("Admin email")
    password = click.prompt("Admin password", hide_input=True, confirmation_prompt=True)

    if User.query.filter_by(username=username).first():
        click.echo(f" Username '{username}' already exists.")
        return

    user = User(username=username, email=email, role="admin")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f" Admin user '{username}' created.")

@app.cli.command("seed-data")
@with_appcontext
def seed_data():
    from app.models.category import Category
    from app.models.user import User
    from app.models.transaction import Transaction
    import datetime

    default_categories = [
        ("Food & Dining",    "#FF6B6B", ""),
        ("Salary",           "#4ECDC4", ""),
        ("Transport",        "#45B7D1", ""),
        ("Entertainment",    "#96CEB4", ""),
        ("Utilities",        "#FFEAA7", ""),
        ("Healthcare",       "#DDA0DD", ""),
        ("Shopping",         "#98D8C8", ""),
        ("Savings",          "#F7DC6F", ""),
    ]

    created_cats = 0
    categories = {}
    for name, color, icon in default_categories:
        cat = Category.query.filter_by(name=name).first()
        if not cat:
            cat = Category(name=name, color=color, icon=icon, is_default=True)
            db.session.add(cat)
            created_cats += 1
        categories[name] = cat

    db.session.commit()
    click.echo(f" Created {created_cats} categories.")

    demo_users = [
        ("admin", "admin@example.com", "admin", "Admin@1234"),
        ("demo", "demo@example.com", "analyst", "Demo@1234"),
        ("viewer", "viewer@example.com", "viewer", "Viewer@1234"),
    ]
    created_users = []
    for username, email, role, password in demo_users:
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            created_users.append(username)
        elif not user.check_password(password):
            user.set_password(password)
            click.echo(f" Synchronized password for {username}.")
    db.session.commit()

    if created_users:
        click.echo(f" Demo users created: {', '.join(created_users)}")
    else:
        click.echo(" Demo users already exist; passwords synchronized.")

    demo_user = User.query.filter_by(username="demo").first()
    if demo_user and not Transaction.query.filter_by(user_id=demo_user.id).first():
        today = datetime.date.today()
        sample = [
            (5000, "income",  "Salary",        today.replace(day=1), "Monthly salary"),
            (120,  "expense", "Food & Dining", today,                "Groceries"),
            (50,   "expense", "Transport",     today,                "Bus pass"),
            (200,  "expense", "Entertainment", today,                "Concert tickets"),
            (300,  "expense", "Utilities",     today,                "Electricity bill"),
        ]
        for amount, ttype, cat_name, date, desc in sample:
            db.session.add(Transaction(
                user_id=demo_user.id,
                amount=amount,
                transaction_type=ttype,
                category_id=categories[cat_name].id,
                date=date,
                description=desc,
            ))
        db.session.commit()
        click.echo(" Sample transactions seeded for demo.")
    else:
        click.echo(" Demo transactions already exist – skipping.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=app.debug, host="0.0.0.0", port=port)
