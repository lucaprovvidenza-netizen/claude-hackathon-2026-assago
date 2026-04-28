# Challenge 1: The Stories

## Context

Brennero Logistics S.p.A. manages an internal order portal used by operators, warehouse staff, and management. The current system is a Java/Servlet monolith from 2015, with no up-to-date documentation. The board has approved a "modernisation" project that includes: expanding the product catalogue, enriching the customer registry, a modern dashboard with charts, migration from Java to Python, and database optimisation.

This document defines the user stories for **existing and evolving** business capabilities, with acceptance criteria that can be executed by a tester. Priorities reflect stakeholder disagreements, documented explicitly.

---

## Stakeholders and conflicting priorities

| Stakeholder | Stated priority | Motivation |
|---|---|---|
| **Operations (Logistics Manager)** | Richer service catalogue, reliable tracking | "We need different product types: transport, customs, warehouse, insurance. Today everything is mixed together." |
| **Finance (CFO)** | Consistent totals, dashboard for the board | "We need clear charts, not HTML tables. The board wants trends and KPIs at a glance." |
| **Warehouse (Warehouse Manager)** | Aligned stock levels, materials catalogue | "I need to distinguish services from physical materials. Only materials have stock." |
| **IT (CTO)** | Migration to Python, security, maintainability | "Java/Servlet from 2015 is unsustainable. Python with a modern framework lets us iterate 3x faster." |
| **Management (CEO)** | Zero downtime, historical data preserved | "The portal cannot go down. And we are not losing the last 10 years of orders." |
| **Sales (Sales Manager)** | Customer classification by priority | "I need to know immediately who the Gold, Silver, and Bronze customers are. Today I have to open every record." |
| **Customer Service** | Quick search by customer name or product | "I waste 5 minutes looking for a customer. I need a search bar that works." |

### Explicit disagreements

1. **Finance vs Operations**: Finance wants to block order creation until totals are correct. Operations says "ship first, fix later" because delays incur penalties.
2. **IT vs Management**: IT wants to rewrite everything in Python. Management demands zero downtime and compatibility with historical data.
3. **Warehouse vs Operations**: Warehouse wants to distinguish services (without stock) from materials (with stock). Operations does not want to complicate the order form.
4. **Sales vs IT**: Sales wants customer classification immediately. IT says the customer registry must be migrated to the new stack first.

---

## Epic 1: Order Management — Service and Material Catalogue

> **Objective:** Expand the product catalogue with different types (transport services, customs procedures, warehouse materials, insurance, consulting) to support more articulated commercial offers.

### US-1.1: Order list view with filters

**As** a logistics operator  
**I want** to see the order list filtered by customer, status, period, and product type  
**So that** I can quickly find the orders I need to act on

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | The list shows: order number, customer, date, expected delivery, status, amount | Open `/orders` → verify all columns are present |
| AC-2 | The customer filter searches by company name (partial match) | Enter "Alpini" in the customer field → only orders for "Trasporti Alpini" visible |
| AC-3 | The status filter shows only orders in that status | Select "Delivered" → verify all results have status "Delivered" |
| AC-4 | The date filter filters on DATA_ORDINE in the range [from, to] | Enter from=2024-02-01, to=2024-02-28 → only orders from February 2024 |
| AC-5 | Without filters, all orders are visible sorted by descending date | Load the page without parameters → most recent order is first |
| AC-6 | All statuses are mapped with a readable label (no raw numeric codes exposed) | No order shows a raw number as its status |

**Priority:** MUST

---

### US-1.2: Product catalogue with categories and types

**As** a commercial operator  
**I want** a product catalogue organised by type (Transport Services, Customs, Warehouse, Insurance, Consulting)  
**So that** I can compose orders with diversified offerings

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | Each product has a type: TRASPORTO, DOGANA, MAGAZZINO, ASSICURAZIONE, CONSULENZA | Query: `SELECT DISTINCT TIPOLOGIA FROM PRODOTTI` → 5 values |
| AC-2 | Services (TRASPORTO, DOGANA, ASSICURAZIONE, CONSULENZA) have no stock | Products with service type → GIACENZA = NULL or not shown |
| AC-3 | Materials (MAGAZZINO) have tracked stock | Products with type MAGAZZINO → GIACENZA visible and decremented on order |
| AC-4 | The catalogue can be browsed with a filter by type | Catalogue page → type dropdown → filter working |
| AC-5 | Each product has: code, description, type, unit of measure, unit price, VAT | Verify all fields in the product detail |
| AC-6 | The catalogue contains at least 15 products distributed across the 5 types | Query: `SELECT TIPOLOGIA, COUNT(*) FROM PRODOTTI GROUP BY TIPOLOGIA` → min 2 per type |

**Priority:** MUST

**Reference catalogue:**

| Type | Example products |
|---|---|
| TRASPORTO | Domestic transport, EU international, non-EU, express, groupage, full truck |
| DOGANA | Import customs procedure, export, triangulation, customs warehouse |
| MAGAZZINO | Pallet storage/month, picking & packing, labelling, cross-docking |
| ASSICURAZIONE | Basic cargo insurance, all-risk, carrier liability |
| CONSULENZA | Logistics consulting, supply chain audit, operator training |

---

### US-1.3: Order creation with expanded catalogue

**As** an operator  
**I want** to create a new order by selecting products from different types  
**So that** I can compose mixed orders (e.g. transport + customs + insurance)

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | The form shows products grouped by type | Open new order → products organised in sections/tabs by type |
| AC-2 | It is possible to add products of different types in the same order | Create order with 1 TRASPORTO product + 1 DOGANA + 1 ASSICURAZIONE → valid order |
| AC-3 | The order is created with status "Draft" | Create order → status = "Draft" |
| AC-4 | The order number follows the format ORD-YYYY-NNNN | Create order → number conforms |
| AC-5 | The expected delivery is automatically calculated as +7 days | Create order → expected delivery = today + 7 |
| AC-6 | The customer discount is applied uniformly to all lines | Create order for customer with 5% discount → each line discounted by 5% |
| AC-7 | Only MAGAZZINO products decrement stock | Create mixed order → only MAGAZZINO products have stock decrement |

**Priority:** MUST

---

### US-1.4: Order status update with workflow

**As** a logistics operator  
**I want** to update the status of an order following valid transitions  
**So that** I can track progress without errors

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | Valid transitions are: Draft→Confirmed→In Progress→Shipped→Delivered | Attempt transition Draft→Shipped → blocked |
| AC-2 | The "Cancelled" status is reachable from Draft and Confirmed, not from subsequent statuses | Attempt cancellation from "Shipped" → blocked |
| AC-3 | The status change is recorded with user and timestamp | Update status → MODIFIED_BY and MODIFIED_DATE updated |
| AC-4 | When status changes to "Delivered", the actual delivery date is set | Set status "Delivered" → DATA_CONSEGNA_EFFETTIVA = now |
| AC-5 | The dropdown shows only valid transitions from the current status | Order in status "In Progress" → dropdown shows only "Shipped" and not "Draft" |

**Priority:** MUST

---

## Epic 2: Customer Management — Enriched Registry and Classification

> **Objective:** Enrich the customer registry with additional fields, implement advanced search (by customer name or product), and classify customers by priority (Gold/Silver/Bronze).

### US-2.1: Extended customer registry

**As** a commercial operator  
**I want** to manage a complete customer registry with all necessary data  
**So that** I have a full picture of the customer without consulting other systems

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | The registry includes the base fields: company name, VAT number, tax code, address, postal code, city, province, phone, email | Open customer record → all fields present |
| AC-2 | Additional fields: PEC, SDI code, business sector, commercial contact, contact phone | Verify additional fields in the record |
| AC-3 | The "commercial notes" field is editable (free text) | Enter a note → saved correctly |
| AC-4 | The last order date is calculated automatically | Verify it matches the customer's most recent order |
| AC-5 | Annual turnover is calculated automatically (sum of non-cancelled orders for the year) | Verify consistency with the report |

**Priority:** MUST

---

### US-2.2: Customer classification by priority

**As** a sales manager  
**I want** to classify customers into 3 priority levels (Gold, Silver, Bronze)  
**So that** I can differentiate service and commercial terms

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | Each customer has a "Classification" field with values: Gold (1), Silver (2), Bronze (3) | Open customer record → classification field present |
| AC-2 | The classification is visible in the customer list with a coloured badge | Customer list → Gold (gold), Silver (silver), Bronze (bronze) badge |
| AC-3 | The classification is editable by the operator | Change classification → saved correctly |
| AC-4 | The customer list can be filtered by classification | Filter "Gold Only" → only Gold customers visible |
| AC-5 | The order detail shows the customer's classification | Open order detail → customer classification badge visible |

**Priority:** MUST

---

### US-2.3: Advanced customer and product search

**As** an operator  
**I want** a search bar that searches both by customer name and by product name  
**So that** I can quickly find what I need without navigating through different menus

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | A global search bar exists accessible from every page (header) | Verify search bar presence in the navigation header |
| AC-2 | Searching a customer name, results show matching customers | Search "Alpini" → result "Trasporti Alpini S.r.l." |
| AC-3 | Searching a product name, results show matching products | Search "Trasporto" → results for products of type TRASPORTO |
| AC-4 | Results are grouped by type (Customers / Products) | Search "Alpini" → "Customers" section with results, "Products" section empty or with matches |
| AC-5 | Clicking a customer result opens the customer record | Click "Trasporti Alpini" → customer detail page |
| AC-6 | Clicking a product result opens the product detail in the catalogue | Click "Trasporto Nazionale" → product detail |
| AC-7 | The search is case-insensitive and supports partial match | Search "alpini" (lowercase) → finds "Trasporti Alpini" |

**Priority:** MUST

---

## Epic 3: Reporting — Modern Dashboard

> **Objective:** Replace tabular reports with an interactive dashboard featuring charts, KPIs, and modern visualisations.

### US-3.1: KPI Dashboard

**As** a manager  
**I want** a dashboard with key indicators at a glance  
**So that** I can monitor business performance without downloading reports

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | Visible KPI cards: Total orders, Total revenue, Orders in progress, Average ticket | Dashboard → 4 KPI cards in the upper section |
| AC-2 | KPIs filter by year (default: current year) | Change year → KPIs updated |
| AC-3 | Each card shows % change vs the previous period (if data available) | Revenue KPI shows "+12%" or "−5%" compared to the previous year |
| AC-4 | Cancelled orders are excluded from revenue and average ticket | Verify consistency excluding status 5 |

**Priority:** MUST

---

### US-3.2: Revenue by customer chart (bar chart)

**As** a manager  
**I want** a bar chart of revenue by customer  
**So that** I can visually identify the most important customers

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | Horizontal bar chart: X axis = revenue, Y axis = customers | Dashboard → chart present and readable |
| AC-2 | Customers are sorted by descending revenue | The customer with the highest revenue is at the top |
| AC-3 | Hovering over a bar shows a tooltip with: customer, number of orders, total revenue | Hover → tooltip with correct data |
| AC-4 | Bars are coloured by customer classification (Gold/Silver/Bronze) | Gold bars = gold colour, Silver = silver, Bronze = bronze |

**Priority:** SHOULD

---

### US-3.3: Order trend over time chart (line chart)

**As** a manager  
**I want** a line chart showing the order trend by month  
**So that** I can identify trends and seasonality

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | Line chart: X axis = months, Y axis = number of orders | Dashboard → chart present |
| AC-2 | A second line shows revenue by month | Two distinguishable lines (orders and revenue) |
| AC-3 | Filter by year | Change year → chart updated |
| AC-4 | Hovering over a point shows: month, number of orders, revenue | Tooltip with correct data |

**Priority:** SHOULD

---

### US-3.4: Order status distribution chart (pie/donut chart)

**As** a logistics manager  
**I want** a pie chart of the distribution of orders by status  
**So that** I can understand how many orders are in queue, in progress, or completed

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | Donut chart with segments for each status (Draft, Confirmed, In Progress, Shipped, Delivered, Cancelled) | Dashboard → chart present |
| AC-2 | Each segment shows the count and the percentage | Hover/label → e.g. "Delivered: 3 (33%)" |
| AC-3 | Colours are semantic (e.g. green=Delivered, red=Cancelled, yellow=In Progress) | Colours consistent with the status |

**Priority:** SHOULD

---

## Epic 4: Modernisation — Java → Python Migration

> **Objective:** Rewrite the portal from Java/Servlet to Python (modern framework), resolving the known anomalies of the original monolith: SQL injection, plaintext passwords, God class, circular dependencies, absence of transactions.

### US-4.1: Python application with modern web framework

**As** a developer  
**I want** the portal to be rewritten in Python with a modern framework (Flask/FastAPI)  
**So that** I have a maintainable, testable, and secure codebase

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | The Python application serves all working pages of the Java portal | All actions (orders, orderDetail, newOrder, saveOrder, updateStatus, report, customers, login, logout) work |
| AC-2 | The architecture follows the MVC/MTV pattern with separation of responsibilities | No "God class": separate routes, model layer, template layer |
| AC-3 | The database is the same (H2 or SQLite for development, compatible schema) | The SQL schema is compatible with existing data |
| AC-4 | The application starts with a single command (`python app.py` or `flask run`) | Run command → portal accessible on localhost |

**Priority:** MUST

---

### US-4.2: Resolution of security anomalies

**As** a CTO  
**I want** all known vulnerabilities of the Java monolith to be resolved  
**So that** I can pass a security audit

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | No SQL injection: all queries use prepared parameters | Grep codebase: no string concatenation in SQL queries |
| AC-2 | Passwords stored with a secure hash (bcrypt or argon2) | DB query: password field contains hash, not plaintext |
| AC-3 | CSRF protection on all POST forms | Every form has a CSRF token, POST without token → 403 error |
| AC-4 | Secure sessions with timeout | Session expires after 30 minutes of inactivity |
| AC-5 | Input validation on all user fields | Enter `<script>alert(1)</script>` in a field → input sanitised |
| AC-6 | HTTP security headers present (X-Content-Type-Options, X-Frame-Options, CSP) | Verify headers in HTTP responses |

**Priority:** MUST

---

### US-4.3: Resolution of architectural anomalies

**As** a developer  
**I want** the structural problems of the monolith to be resolved  
**So that** I have an extensible codebase

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | No circular dependencies between modules | Import analysis → no cycles |
| AC-2 | Order operations use database transactions | Create order with an error halfway through → complete rollback, no partial data |
| AC-3 | The discount calculation logic is centralised and documented | A single point where the discount is applied, rule documented |
| AC-4 | Order statuses are defined as Enum, not magic numbers | Grep codebase: no hardcoded numbers for statuses |
| AC-5 | Error handling is structured (logging, user messages, no stacktrace in UI) | Trigger an error → log file updated, UI shows generic message |

**Priority:** MUST

---

## Epic 5: Data Integrity — Verification, DB Optimisation, and Archiving

> **Objective:** Implement a data integrity verification system, optimise the database schema, and create a mechanism for archiving old orders.

### US-5.1: Order total consistency

**As** a financial controller  
**I want** the order header total to always match the sum of the lines  
**So that** I can produce reliable reports for the board

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | For each order: IMPORTO_TOTALE = Σ(IMPORTO_RIGA) of the associated lines | Verification query → empty result (no discrepancies) |
| AC-2 | Line amount = quantity × unit price × (1 - discount/100) | For each line, verify the formula |
| AC-3 | An automatic verification job flags discrepancies | Run job → report of inconsistencies (if any) |

**Priority:** MUST

---

### US-5.2: Database schema optimisation

**As** a DBA  
**I want** a clean and optimised database schema  
**So that** I have better performance and consistent data

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | Duplicate field QTA_MAGAZZINO removed, a single field GIACENZA | Schema → no QTA_MAGAZZINO field |
| AC-2 | Explicit foreign keys between tables (ORDINI→CLIENTI, RIGHE_ORDINE→ORDINI, RIGHE_ORDINE→PRODOTTI) | Schema → FKs present with appropriate ON DELETE/UPDATE |
| AC-3 | Indexes on frequently searched columns (STATO, DATA_ORDINE, ID_CLIENTE, RAGIONE_SOCIALE) | Schema → indexes present |
| AC-4 | VAT field standardised with valid values (22, 10, 4, 0) via CHECK constraint | Attempt INSERT with VAT=99 → error |
| AC-5 | Dead trigger (TRG_CALCOLA_TOTALE) removed, logic in the application code | Schema → no trigger |

**Priority:** MUST

---

### US-5.3: Order archiving

**As** an IT manager  
**I want** orders older than 2 years to be moved to archive tables  
**So that** the operational tables stay lean without losing historical data

**Acceptance Criteria:**

| # | Criterion | Verification |
|---|---|---|
| AC-1 | Tables ORDINI_ARCHIVIO and RIGHE_ORDINE_ARCHIVIO exist with the same structure | Schema → tables present |
| AC-2 | An archiving job moves orders with DATA_ORDINE > 2 years and a final status (Delivered/Cancelled) | Run job → old orders moved |
| AC-3 | Archived orders are not visible in the operational order list | Order list → no archived orders |
| AC-4 | Archived orders can be browsed in a dedicated "Archive" section | "Archive" menu → historical orders visible |
| AC-5 | The report includes both operational and archived data | Annual report → complete data regardless of archiving |
| AC-6 | Archiving is reversible (an order can be restored) | Restore order from archive → returns to the operational table |

**Priority:** SHOULD

---

## Priority summary (MoSCoW)

| ID | Story | MUST | SHOULD | COULD |
|---|---|---|---|---|
| US-1.1 | Order list with filters | ✓ | | |
| US-1.2 | Service and material catalogue | ✓ | | |
| US-1.3 | Order creation with expanded catalogue | ✓ | | |
| US-1.4 | Order status with workflow | ✓ | | |
| US-2.1 | Extended customer registry | ✓ | | |
| US-2.2 | Customer classification (Gold/Silver/Bronze) | ✓ | | |
| US-2.3 | Advanced customer and product search | ✓ | | |
| US-3.1 | KPI Dashboard | ✓ | | |
| US-3.2 | Revenue by customer chart | | ✓ | |
| US-3.3 | Order trend over time chart | | ✓ | |
| US-3.4 | Status distribution chart | | ✓ | |
| US-4.1 | Python application | ✓ | | |
| US-4.2 | Resolution of security anomalies | ✓ | | |
| US-4.3 | Resolution of architectural anomalies | ✓ | | |
| US-5.1 | Order total consistency | ✓ | | |
| US-5.2 | DB schema optimisation | ✓ | | |
| US-5.3 | Order archiving | | ✓ | |

---

## Pending decisions

| # | Decision | Owner | Deadline | Impact |
|---|---|---|---|---|
| D-1 | Python framework: Flask vs FastAPI vs Django | IT (Chiara + Lucia) | Sprint 1 | US-4.1 |
| D-2 | Target DB: SQLite (dev) + PostgreSQL (prod) or keep H2? | IT + DBA | Sprint 1 | US-5.2 |
| D-3 | Charting library: Chart.js vs Plotly vs D3.js | Dev + Finance | Sprint 1 | US-3.x |
| D-4 | Single rule for customer discount application (line vs order) | Finance + Operations | Sprint 1 | US-1.3 |
| D-5 | Time threshold for archiving (2 years? 3 years?) | Management + Finance | Sprint 2 | US-5.3 |
| D-6 | Data migration strategy from the Java monolith to the new Python app | IT | Sprint 1 | US-4.1, US-5.x |
