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
    import datetime, random

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
        if not Category.query.filter_by(name=name).first():
            cat = Category(name=name, color=color, icon=icon, is_default=True)
            db.session.add(cat)
            created_cats += 1
        cat = Category.query.filter_by(name=name).first()
        if cat:
            categories[name] = cat.id

    db.session.commit()
    click.echo(f" Created {created_cats} categories.")

    if User.query.count() == 0:
        demo = User(username="demo", email="demo@example.com", role="analyst")
        demo.set_password("Demo@1234")
        db.session.add(demo)
        db.session.commit()
        click.echo(" Demo user created: demo / Demo@1234")

        demo_user = User.query.filter_by(username="demo").first()
        today = datetime.date.today()
        sample = [
            (5000, "income",  "Salary",       today.replace(day=1), "Monthly salary"),
            (120,  "expense", "Food & Dining", today,               "Groceries"),
            (50,   "expense", "Transport",     today,               "Bus pass"),
            (200,  "expense", "Entertainment", today,               "Concert tickets"),
            (300,  "expense", "Utilities",     today,               "Electricity bill"),
        ]
        for amount, ttype, cat_name, date, desc in sample:
            txn = Transaction(
                user_id=demo_user.id,
                amount=amount,
                transaction_type=ttype,
                category_id=categories.get(cat_name),
                date=date,
                description=desc,
            )
            db.session.add(txn)
        db.session.commit()
        click.echo(" Sample transactions seeded.")
    else:
        click.echo("Users already exist – skipping transaction seed.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=app.debug, host="0.0.0.0", port=port)
