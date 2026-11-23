# CraftLoom: Artisan Material Inventory and Supply Cost Estimator

CraftLoom is a web application for small-scale artisans and local craft businesses. It tracks raw material stock, calculates exact material costs per finished product, and suggests selling prices, so makers can price their work with confidence.

## Core Feature: Supply Manager and Recipe & Pricing Creator

**Supply Manager**
- Add categories and materials with a unit, stock quantity, cost per unit and low-stock alert level
- Search materials and filter them by category
- Low-stock badges and a total stock value summary

**Recipe & Pricing Creator**
- Create products with pieces made per batch, labor cost and profit markup
- Add materials from your own supplies with the quantity used per batch
- See materials cost, batch total, cost per piece, suggested price and profit per piece
- Costs update automatically when a material's price changes
- A material that is used in a recipe cannot be deleted

## Account Features

- Registration with validation and hashed passwords
- Login and logout, with login by username or email
- Role-based dashboards (Admin and Artisan)
- User profile with view and edit

| Role | What they can do |
|------|------------------|
| Artisan | Manage their own categories, materials, products and recipes |
| Admin | Read-only view of all supplies and products, plus user overview |

Users can only see and change their own records. Public registration always creates an Artisan; Admin accounts are created with `createsuperuser`.

## Tech Stack

- Django (templates for the frontend)
- PostgreSQL / Supabase
- Python 3.10 or newer

## Project Structure

```
accounts/   registration, login, dashboards, profile
supplies/   categories and materials
recipes/    products and recipe items
craftloom/  project settings and URLs
templates/  base layout
static/     CSS and images
docs/       project documents
```

## Setup

1. Clone the repository and open the folder that contains `manage.py`.

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   On macOS or Linux, use `source venv/bin/activate`.

3. Install the packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file next to `manage.py` (this file is ignored by Git and must never be committed):
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   DB_NAME=postgres
   DB_USER=your-db-user
   DB_PASSWORD=your-db-password
   DB_HOST=your-db-host
   DB_PORT=5432
   DB_SSLMODE=require
   ```
   For Supabase, copy the Session pooler values from the project's **Connect** dialog. For a local PostgreSQL database, use `DB_HOST=localhost` and `DB_SSLMODE=prefer`.

5. Create the database tables and an Admin account:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Start the server:
   ```
   python manage.py runserver 8080
   ```

7. Open http://127.0.0.1:8080/ and log in. New users can register as Artisans from the Register page.

## Git Workflow

- `main`: stable code only, no direct commits
- `develop`: integration branch
- `feature/<name>`: one branch per feature, merged into `develop` by Pull Request
- When an increment is done, `develop` is merged into `main` by Pull Request

## Documentation

The Project Development 2 completion report is in the `docs/` folder.

## Author

Justine Kirby Lepon, Section G6
