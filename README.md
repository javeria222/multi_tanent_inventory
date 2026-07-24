# Multi-Tenant Inventory & Order Management API

A B2B backend system for managing inventory, warehouses, customers, and orders across multiple companies (tenants) on a single shared platform. Built to demonstrate real backend engineering patterns — not just CRUD, but concurrency safety, transactional integrity, and role-based access control.

## Why this project

Most portfolio projects are single-tenant CRUD apps. This one simulates a real B2B SaaS problem: multiple companies share the same database and API, but must never see or affect each other's data — while also handling concurrent stock updates safely, a common failure point in real inventory systems.

## Tech Stack

- **Framework:** Python, Flask
- **Database:** PostgreSQL
- **ORM / Migrations:** SQLAlchemy, Flask-Migrate (Alembic)
- **Auth:** Flask-JWT-Extended (JWT tokens), Flask-Bcrypt (password hashing)


## Architecture Highlights

### Multi-tenancy
All tenant data (Users, Products, Warehouses, Customers, Orders) is scoped by a `company_id` foreign key, using a shared-table design. Every query is explicitly filtered by the logged-in user's company — never trusting tenant IDs supplied by the client.

### Role-based access control
A custom decorator (`@requires_role('admin')`) restricts sensitive operations (creating products, warehouses) to admin users, layered on top of JWT authentication (`@jwt_required()`).

### Concurrency-safe stock management
Stock adjustments and order creation use **row-level database locking** (`SELECT ... FOR UPDATE`) to prevent race conditions — e.g., two simultaneous orders can't both deduct from the same limited stock and cause an inconsistent (or negative) inventory count.

### Transactional order creation
Creating an order (with multiple line items) is wrapped in a single database transaction. If any item fails validation (insufficient stock, invalid product), the entire order — including any stock already deducted for earlier items in the same request — is rolled back. Nothing is partially saved.

### Order status state machine
Orders follow an explicit, enforced lifecycle:
```
Pending → Confirmed → Shipped → Delivered
   ↓           ↓           ↓
Cancelled   Cancelled   Returned
```
Invalid transitions (e.g., Pending → Delivered) are rejected. Cancelling or returning an order automatically restores the deducted stock.

## API Overview

| Endpoint | Method | Access | Description |
|---|---|---|---|
| `/register` | POST | Public | Register a new user |
| `/login` | POST | Public | Log in, receive JWT |
| `/warehouse` | POST / GET | Admin / Any | Create / list warehouses |
| `/product` | POST / GET | Admin / Any | Create / list products |
| `/stock` | POST / GET | Admin / Any | Create / list stock entries |
| `/stock/<id>/adjust` | PATCH | Authenticated | Safely adjust stock quantity |
| `/customer` | POST / GET | Admin / Any | Create / list customers |
| `/orders` | POST / GET | Authenticated | Create / list orders |
| `/orders/<id>/status` | PATCH | Authenticated | Transition an order's status |

All list endpoints support pagination via `?page=` and `?per_page=` query parameters.

## Setup

1. Clone the repo and create a virtual environment.
2. `pip install -r requirements.txt`
3. Create a PostgreSQL database.
4. Create a `.env` file:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/your_db_name
   JWT_SECRET_KEY=your-random-secret-key
   ```
5. Run migrations:
   ```
   flask db upgrade
   ```
6. Start the server:
   ```
   python run.py
   ```

## Testing

INCLUDE IMAGES

## Possible Future Improvements

- Credit-limit enforcement on order creation (partially modeled via `Customer.credit_limit`)
- Multi-warehouse stock selection per order
- Audit logging for sensitive actions
- OpenAPI/Swagger documentation
- Clean API architecture ready for future user interface integration