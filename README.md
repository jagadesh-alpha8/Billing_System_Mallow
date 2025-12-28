# Django Billing System

A minimal full-stack Django implementation for a billing system with product CRUD (via admin), dynamic billing, denomination-aware change, async invoice emails, and purchase history.

## Quick start

1. Create and activate a virtual environment.
   - python -m venv .venv
   - source .venv/bin/activate  # On Windows: .venv\Scripts\activate

2. Install dependencies.
   - pip install -r requirements.txt

3. Set environment variables (for email if needed).
   - export EMAIL_HOST_USER="your_email@example.com"
   - export EMAIL_HOST_PASSWORD="your_password"

4. Run migrations and seed data.
   - python manage.py migrate
   - python manage.py createsuperuser
   - python manage.py seed_data

5. Start the server.
   - python manage.py runserver

6. Use the app.
   - Admin: http://127.0.0.1:8000/admin/
     - Manage Products and Denominations
   - Billing page: http://127.0.0.1:8000/
   - Purchase history: http://127.0.0.1:8000/purchases/?email=customer@example.com

## Assumptions

- Product tax is per-item percentage on purchase price.
- Net total is sum of purchase prices + tax; rounded-down net total is used for cash/change calculation.
- Change must be returned exactly using available denominations; if not possible, an error is shown.
- Denomination stock is decremented when change is given.
- Email invoice is sent asynchronously using a lightweight background thread; swap with Celery for full production setups.

## Notes

- Use Admin for CRUD of products and denominations.
- Stock is decremented on successful purchase.
- Basic templates, no fancy CSS per requirements.

## Tests

- Run `python manage.py test` for smoke tests.
