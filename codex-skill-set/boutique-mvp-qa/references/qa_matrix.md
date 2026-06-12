# QA Matrix

## Global acceptance criteria

- CA-01: Critical operations (sale, return, transfer, adjustment, expense) record audit user/date/time.
- CA-02: Stock-insufficient sales are blocked per branch.
- CA-03: PDF/Excel exports respect filters and permissions.
- CA-04: Passwords use Argon2/BCrypt or strong Django-compatible hashing, and production traffic uses TLS.
- CA-05: Dashboard loads under 2 seconds p95 with the expected MVP scale, or the gap is documented.
- CA-06: Daily backups with at least 30-day retention and tested restore before production.

## MVP flow tests

| Flow | Minimum checks |
| --- | --- |
| Login | Valid login, invalid login, logout, protected route redirect |
| Product | Create, edit, deactivate, SKU uniqueness |
| Branch | Create, edit, deactivate, inactive branch blocks new sales |
| Stock entry | Creates inventory/movement/audit |
| Transfer | Origin decreases, destination increases, paired movements, insufficient stock blocked |
| Sale | Stock decreases, sale lines saved, income/audit created, receipt renders |
| Return | Stock/accounting adjusts, audit created |
| Expense | Role allowed, branch scoped, appears in cash/reporting |
| Reports | Filters by date, branch, user; role scope respected; export matches filters |
| Landing | Published content visible, inactive content hidden, gallery order respected |

## Permission regression grid

Test at least one allowed and one denied action per role:

- Administrador: allowed everywhere.
- Contador: allowed finances/reports/expenses, denied inventory mutation by default.
- Administrador de tienda: allowed own-branch inventory/sales/clients, denied other-branch operations.
- Colaborador: allowed own-branch sales/clients/view inventory, denied admin CRUD/cancellations by default.

## HTMX checks

- `GET` full page returns complete layout.
- HTMX `GET` returns partial layout only.
- Invalid `POST` returns form partial with errors.
- Valid `POST` returns refresh signal or updated partial.
- Non-HTMX fallback still works for core CRUD where practical.

## Performance seed targets

Use realistic MVP fixtures when checking reports/dashboard:

- 2 to 5 branches.
- 2,000 to 2,500 products.
- Inventory rows across branch/product combinations.
- Sales/movements over at least 90 days.
- Multiple users across roles.
