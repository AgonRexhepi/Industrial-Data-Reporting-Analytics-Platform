# Industrial Data Analytics & Reporting SaaS

## Current foundation bootstrap

The repository now includes the initial production-oriented Django foundation for Phase 1:

- Django + Django REST Framework
- PostgreSQL-ready configuration
- Redis + Celery wiring
- Docker + Docker Compose services
- Nginx reverse proxy
- Environment-based settings for development and production
- Basic structured console logging
- Health check endpoints at `/health/` and `/api/health/`

### Quick start

```bash
cp .env.example .env
docker compose up -d --build
curl http://127.0.0.1/health/
```

### Initial project structure

```text
config/
apps/
common/
tests/
requirements/
docker/
```

## 1. Project Overview

Build a production-ready, multi-tenant SaaS web application for companies and industries in Kosovo and the wider Balkan market.

The platform allows companies to upload business and industrial data from files such as:

* Excel (`.xlsx`, `.xls`)
* CSV (`.csv`)
* JSON (`.json`)
* XML (`.xml`)
* Parquet (`.parquet`)
* Other structured data formats where appropriate

The system automatically analyzes the uploaded data, detects columns and data types, validates data quality, calculates statistics, and allows users to build interactive charts, tables, dashboards, and reports.

The primary goal is to provide a simpler, localized alternative to complex BI platforms for companies that currently manage most of their reporting through Excel files.

---

# 2. Main Product Concept

The core workflow is:

```text
Upload Data
    ↓
Data Processing
    ↓
Data Profiling
    ↓
Data Validation
    ↓
Statistics & Analytics
    ↓
Data Exploration
    ↓
Chart Builder
    ↓
Dashboard Builder
    ↓
Report Generator
    ↓
PDF / Excel / CSV / Web Report
```

The application should be designed as a SaaS platform from the beginning.

Each company must have an isolated workspace containing its own:

* Users
* Datasets
* Dashboards
* Reports
* Analytics
* Files
* Industry templates
* Audit logs

---

# 3. Target Users

The platform should target:

* Manufacturing companies
* Construction companies
* Logistics companies
* Energy companies
* Retail companies
* Service companies
* Hotels and hospitality
* Warehouses
* SMEs
* Enterprise organizations
* Business analysts
* Managers
* Company administrators

The initial market focus is Kosovo, but the architecture must support international expansion.

---

# 4. Core Features

## 4.1 Authentication

Implement:

* User registration
* Login
* Logout
* JWT authentication
* Refresh tokens
* Password reset
* Email verification
* User profile
* Session management

Roles:

```text
Owner
Admin
Analyst
Viewer
```

---

# 5. Multi-Tenant Architecture

The application must support multiple organizations.

Example:

```text
Platform
│
├── Company A
│   ├── Users
│   ├── Datasets
│   ├── Dashboards
│   └── Reports
│
├── Company B
│   ├── Users
│   ├── Datasets
│   ├── Dashboards
│   └── Reports
│
└── Company C
    ├── Users
    ├── Datasets
    ├── Dashboards
    └── Reports
```

Every organization-owned resource must contain an `organization_id`.

Users must never be able to access another organization's data.

Implement strict organization-level authorization and object-level permissions.

---

# 6. Technology Stack

## Backend

Use:

* Python 3.12+
* Django
* Django REST Framework
* PostgreSQL
* Celery
* Redis

## Data Processing

Use:

* Pandas
* Polars
* PyArrow
* OpenPyXL

Use Polars/PyArrow where appropriate for large datasets and performance.

## Frontend

Use:

* HTML5
* CSS3
* Bootstrap 5
* JavaScript
* ECharts or Chart.js
* DataTables
* AJAX / Fetch API

The frontend should be responsive and suitable for desktop and tablet usage.

## Infrastructure

Use:

* Docker
* Docker Compose
* Nginx
* PostgreSQL
* Redis
* MinIO or S3-compatible object storage

---

# 7. Django Project Structure

Use a modular Django architecture.

```text
project/
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── celery.py
│
├── apps/
│   ├── accounts/
│   ├── tenants/
│   ├── datasets/
│   ├── ingestion/
│   ├── analytics/
│   ├── dashboards/
│   ├── reports/
│   ├── industries/
│   ├── notifications/
│   ├── audit/
│   └── ai/
│
├── common/
│   ├── permissions/
│   ├── exceptions/
│   ├── middleware/
│   ├── utils/
│   └── storage/
│
├── tests/
│
├── requirements/
│
├── docker/
│
├── manage.py
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

# 8. Django Applications

## accounts

Responsible for:

* Users
* Authentication
* JWT
* Password management
* User profiles
* Permissions

## tenants

Responsible for:

* Organizations
* Organization members
* Roles
* Organization settings
* Subscription information

## datasets

Responsible for:

* Dataset metadata
* Dataset versions
* Dataset columns
* Dataset lifecycle
* Dataset ownership

## ingestion

Responsible for:

* File uploads
* File validation
* Excel parsing
* CSV parsing
* JSON parsing
* XML parsing
* Parquet processing
* Data profiling
* Data quality checks
* Background processing

## analytics

Responsible for:

* Filtering
* Sorting
* Grouping
* Aggregations
* Statistics
* Time-series analysis
* Query building
* KPI calculations

## dashboards

Responsible for:

* Dashboards
* Widgets
* Dashboard layout
* Filters
* Widget configuration
* Dashboard sharing

## reports

Responsible for:

* PDF reports
* Excel reports
* CSV exports
* HTML reports
* Scheduled reports

## industries

Responsible for:

* Industry templates
* KPI definitions
* Industry-specific calculations
* Pre-built dashboards

Initial industries:

```text
Manufacturing
Construction
Logistics
Energy
Retail
Hospitality
Generic Business
```

## notifications

Responsible for:

* System notifications
* Email notifications
* Processing status
* Report completion notifications

## audit

Responsible for:

* User activity
* Dataset activity
* Dashboard activity
* Authentication events
* Administrative actions

## ai

Reserved for future functionality:

* Natural language analytics
* AI data assistant
* Automatic insights
* Anomaly detection
* Forecasting
* Automatic report generation

---

# 9. Database Design

The database must use PostgreSQL.

Core models:

```text
User
Organization
OrganizationMember

Dataset
DatasetFile
DatasetVersion
DatasetColumn
DatasetQuality

Dashboard
DashboardWidget
DashboardFilter

Report
ReportTemplate

Industry
IndustryTemplate
IndustryKPI

AuditLog
Notification
Subscription
```

---

# 10. Organization Model

Example:

```python
class Organization(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(max_length=255)

    slug = models.SlugField(unique=True)

    industry = models.ForeignKey(
        "industries.Industry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
```

---

# 11. Dataset Model

A dataset represents a logical collection of data.

Example:

```text
Production 2026
Sales 2026
Employees 2026
Vehicle Fleet
Warehouse Inventory
```

Dataset statuses:

```text
UPLOADING
PROCESSING
VALIDATING
READY
FAILED
ARCHIVED
```

---

# 12. Dataset Versioning

Dataset changes must not overwrite previous versions.

Example:

```text
Production Dataset

Version 1
Version 2
Version 3
```

Users should be able to inspect previous versions and optionally restore them.

---

# 13. Dataset Columns

The system must automatically detect column types.

Supported logical types:

```text
string
integer
decimal
boolean
date
datetime
currency
percentage
category
email
url
```

For each column calculate:

* Null count
* Unique count
* Minimum
* Maximum
* Average where applicable
* Data type
* Position
* Cardinality

---

# 14. Data Quality

After every upload, automatically calculate:

```text
Total rows
Total columns
Missing values
Duplicate rows
Invalid values
Invalid dates
Invalid numeric values
Potential outliers
Quality score
```

Example:

```text
Dataset Quality Score: 94.2%

Rows:              125,430
Columns:                18
Missing values:       3.2%
Duplicate rows:        142
Invalid rows:           21
```

---

# 15. File Upload Workflow

The upload process must be asynchronous.

Do not process large files inside the HTTP request.

Workflow:

```text
User Upload
    ↓
Validate File
    ↓
Create Dataset
    ↓
Store File
    ↓
Create Celery Job
    ↓
Parse Dataset
    ↓
Detect Columns
    ↓
Detect Data Types
    ↓
Validate Data
    ↓
Calculate Data Quality
    ↓
Generate Dataset Profile
    ↓
Create Dataset Version
    ↓
Mark Dataset as READY
```

Large files must be processed by Celery workers.

---

# 16. File Storage

Use object storage for uploaded files.

Development:

```text
Local Docker Volume
```

Production:

```text
S3
or
MinIO
```

Recommended structure:

```text
organizations/
    {organization_id}/
        datasets/
        reports/
        exports/
```

Never expose raw storage paths directly to users.

---

# 17. Analytics Engine

The analytics engine must be independent from Django views.

Structure:

```text
analytics/
│
├── engine/
│   ├── aggregation.py
│   ├── filtering.py
│   ├── grouping.py
│   ├── statistics.py
│   ├── time_series.py
│   ├── query_builder.py
│   └── validators.py
```

Supported operations:

```text
COUNT
SUM
AVG
MIN
MAX
MEDIAN
STD
DISTINCT COUNT
PERCENTAGE
```

Supported operations:

```text
Filter
Sort
Group By
Date Grouping
Top N
Bottom N
Comparisons
Aggregations
```

---

# 18. Analytics Query API

Example:

```http
POST /api/v1/analytics/query/
```

Request:

```json
{
    "dataset_id": "uuid",
    "dimensions": [
        "Lokacioni"
    ],
    "measures": [
        {
            "column": "Sasia",
            "aggregation": "sum"
        }
    ],
    "filters": [
        {
            "column": "Viti",
            "operator": "=",
            "value": 2026
        }
    ],
    "limit": 100
}
```

The backend must validate all columns, operators and aggregation functions against an allowed whitelist.

Never execute arbitrary SQL generated by the user.

---

# 19. Dashboard Builder

The application must include a drag-and-drop dashboard builder.

Supported widgets:

```text
KPI
Table
Bar Chart
Line Chart
Pie Chart
Area Chart
Scatter Plot
Heatmap
Map
```

Example:

```text
┌────────────┬────────────┬────────────┐
│ KPI        │ KPI        │ KPI        │
├────────────┴────────────┼────────────┤
│                         │            │
│ Line Chart              │ Bar Chart  │
│                         │            │
├─────────────────────────┴────────────┤
│                                      │
│ Table                                │
│                                      │
└──────────────────────────────────────┘
```

---

# 20. Widget Configuration

Every widget must have a configuration object.

Example:

```json
{
    "dataset_id": "uuid",
    "dimension": "Lokacioni",
    "measure": {
        "column": "Sasia",
        "aggregation": "sum"
    },
    "filters": [],
    "sort": {
        "column": "Sasia",
        "direction": "desc"
    },
    "limit": 10
}
```

The frontend should render the visualization based on this configuration.

---

# 21. Dashboard Builder UI

The interface should contain:

```text
Left Sidebar
    ↓
Widget Types

Center
    ↓
Dashboard Canvas

Right Sidebar
    ↓
Widget Configuration
```

Example:

```text
┌──────────────┬─────────────────────────────┬──────────────┐
│ Components   │ Dashboard Canvas           │ Configuration│
│              │                             │              │
│ KPI          │ ┌──────┐ ┌──────┐          │ Dataset      │
│ Table        │ │ KPI  │ │ KPI  │          │ Dimension    │
│ Bar          │ └──────┘ └──────┘          │ Measure      │
│ Line         │                             │ Filters      │
│ Pie          │ ┌─────────────────────┐     │ Sort         │
│ Area         │ │     LINE CHART      │     │              │
│ Scatter      │ └─────────────────────┘     │              │
└──────────────┴─────────────────────────────┴──────────────┘
```

---

# 22. Global Dashboard Filters

Dashboards should support global filters.

Examples:

```text
Date
Location
Department
Machine
Product
Employee
Category
```

A global filter should be capable of affecting multiple widgets simultaneously.

---

# 23. Reports

Users must be able to generate reports from dashboards.

Supported formats:

```text
PDF
XLSX
CSV
HTML
```

Report structure:

```text
Company Logo

Report Title

Date Range

Executive Summary

KPIs

Charts

Tables

Statistics

Conclusions

Generated Date
```

---

# 24. Scheduled Reports

Future functionality:

```text
Daily
Weekly
Monthly
Custom Schedule
```

Example:

```text
Send Production Report
Every Monday at 08:00
Recipients:
manager@company.com
director@company.com
```

---

# 25. Industry Templates

The platform should provide ready-made templates.

## Manufacturing

KPIs:

```text
Production
Target
Efficiency
OEE
Downtime
Defect Rate
Waste
Cost
```

Dashboards:

```text
Production Overview
Machine Performance
Downtime Analysis
Quality Analysis
Cost Analysis
Employee Performance
```

## Logistics

KPIs:

```text
Total Deliveries
On-Time Delivery
Distance
Fuel Consumption
Cost per KM
Vehicle Utilization
```

## Construction

KPIs:

```text
Budget
Actual Cost
Remaining Budget
Project Progress
Labor Hours
Material Cost
Equipment Cost
```

## Energy

KPIs:

```text
Consumption
Production
Peak Load
Efficiency
Cost
Self Consumption
```

---

# 26. UI Pages

Main application structure:

```text
/auth
    /login
    /register
    /forgot-password

/app

    /dashboard

    /datasets
        /list
        /upload
        /:id
        /:id/preview
        /:id/profile

    /analytics
        /explorer

    /dashboards
        /list
        /create
        /:id
        /:id/edit

    /reports
        /list
        /create
        /:id

    /templates

    /settings
        /company
        /users
        /roles
        /billing
        /audit
```

---

# 27. API Structure

Use versioned REST APIs.

```text
/api/v1/
```

Authentication:

```http
POST /auth/login/
POST /auth/refresh/
POST /auth/logout/
GET  /auth/me/
```

Organizations:

```http
GET  /organizations/
POST /organizations/
GET  /organizations/{id}/
PUT  /organizations/{id}/
```

Datasets:

```http
GET    /datasets/
POST   /datasets/upload/
GET    /datasets/{id}/
DELETE /datasets/{id}/
GET    /datasets/{id}/preview/
GET    /datasets/{id}/columns/
GET    /datasets/{id}/quality/
GET    /datasets/{id}/versions/
POST   /datasets/{id}/reprocess/
```

Analytics:

```http
POST /analytics/query/
POST /analytics/profile/
POST /analytics/statistics/
```

Dashboards:

```http
GET    /dashboards/
POST   /dashboards/
GET    /dashboards/{id}/
PUT    /dashboards/{id}/
DELETE /dashboards/{id}/

POST   /dashboards/{id}/widgets/
PUT    /dashboards/{id}/widgets/{widget_id}/
DELETE /dashboards/{id}/widgets/{widget_id}/

POST   /dashboards/{id}/execute/
```

Reports:

```http
GET  /reports/
POST /reports/
GET  /reports/{id}/
POST /reports/{id}/generate/
GET  /reports/{id}/download/
```

---

# 28. Security Requirements

Security is a first-class requirement.

Implement:

* HTTPS
* JWT authentication
* RBAC
* Organization isolation
* Object-level permissions
* CSRF protection where applicable
* CORS configuration
* Rate limiting
* File size limits
* MIME type validation
* File extension validation
* Filename sanitization
* Malware/virus scanning integration
* Secure object storage
* Database backups
* Audit logging
* Password hashing
* Secure secrets management

Users must never be able to access files or datasets belonging to another organization.

Never allow arbitrary SQL execution from the analytics interface.

---

# 29. Audit Logging

Record important actions:

```text
LOGIN
LOGOUT
UPLOAD_DATASET
DELETE_DATASET
CREATE_DASHBOARD
UPDATE_DASHBOARD
DELETE_DASHBOARD
CREATE_REPORT
DOWNLOAD_REPORT
CREATE_USER
DELETE_USER
CHANGE_PERMISSION
```

Audit log should contain:

```text
User
Organization
Action
Resource
Resource ID
IP Address
Timestamp
Status
Metadata
```

---

# 30. Performance Requirements

The system should support:

* Small files: immediate processing
* Medium files: background processing
* Large files: chunked processing
* Multiple simultaneous uploads
* Multiple concurrent dashboard queries

Use:

```text
Celery
Redis
Polars
PyArrow
Parquet
Database indexing
Caching
Pagination
```

Do not load extremely large datasets completely into application memory unnecessarily.

---

# 31. Caching

Use Redis for:

* Dashboard query caching
* Frequently accessed statistics
* Dataset metadata
* Session-related data
* Temporary processing state

Cache keys must include the organization and dataset context to prevent cross-tenant data leakage.

---

# 32. Error Handling

Use centralized API error handling.

Return consistent responses:

```json
{
    "success": false,
    "error": {
        "code": "DATASET_NOT_FOUND",
        "message": "Dataset was not found."
    }
}
```

Never expose internal stack traces in production.

---

# 33. Testing

Implement:

## Unit Tests

* Models
* Services
* Analytics engine
* Data validators
* Permissions

## Integration Tests

* Upload workflow
* Celery processing
* Dashboard execution
* Report generation

## API Tests

Test:

* Authentication
* Authorization
* Tenant isolation
* Dataset endpoints
* Analytics endpoints
* Dashboard endpoints
* Report endpoints

A critical test must verify that Organization A cannot access Organization B data.

---

# 34. Docker Environment

Provide:

```text
Dockerfile
docker-compose.yml
docker-compose.dev.yml
docker-compose.prod.yml
.env.example
```

Services:

```text
nginx
web
worker
postgres
redis
minio
```

The application must be runnable with:

```bash
docker compose up -d
```

---

# 35. Environment Variables

Never commit secrets.

Provide `.env.example`:

```env
DEBUG=False

SECRET_KEY=

DATABASE_URL=

REDIS_URL=

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=

CELERY_BROKER_URL=

JWT_ACCESS_TOKEN_LIFETIME=
JWT_REFRESH_TOKEN_LIFETIME=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

---

# 36. Logging and Monitoring

Implement structured application logging.

Log:

```text
HTTP requests
Celery jobs
Dataset processing
Analytics execution
Errors
Authentication events
```

Production should support integration with monitoring systems such as:

```text
Sentry
Prometheus
Grafana
```

---

# 37. Internationalization

The platform should be designed for localization.

Initial languages:

```text
English
Albanian
```

Future:

```text
German
Serbian
Macedonian
```

Do not hard-code UI text.

Use Django internationalization.

---

# 38. Kosovo Market Localization

The initial product should support:

* Albanian language
* Euro currency
* Kosovo municipalities
* Local date formats
* Local number formatting
* Kosovo business-oriented terminology
* Industry-specific templates
* Exportable professional reports

The architecture must remain generic enough for international expansion.

---

# 39. Future AI Features

AI must be implemented as a separate service/module.

Potential functionality:

```text
"Show me production by machine."

"Which machine has the highest downtime?"

"Compare production between January and August."

"Why did production decrease in March?"

"Generate a monthly management report."

"Find unusual values in this dataset."
```

The AI layer should translate natural-language requests into validated analytics operations.

It must never execute unrestricted SQL.

---

# 40. Future Advanced Analytics

Planned features:

```text
Forecasting
Trend Analysis
Anomaly Detection
Correlation Analysis
Regression
Predictive Maintenance
Demand Forecasting
Cost Forecasting
```

---

# 41. SaaS Billing

Future subscription plans:

```text
FREE
STARTER
BUSINESS
ENTERPRISE
```

Possible limits:

```text
Users
Datasets
Storage
Rows
Dashboards
Reports
AI Queries
API Requests
```

Billing should be implemented as a separate module so it can later integrate with a payment provider.

---

# 42. API Documentation

Use OpenAPI / Swagger.

Expose:

```text
/api/docs/
/api/schema/
```

Every API endpoint must contain:

* Description
* Authentication requirements
* Request schema
* Response schema
* Error responses
* Example requests
* Example responses

---

# 43. Development Principles

Follow these principles:

1. Modular architecture
2. Clean separation of concerns
3. API-first design
4. Multi-tenant by default
5. Secure by default
6. Background processing for expensive operations
7. No arbitrary SQL from users
8. Strong validation
9. Automated testing
10. Production-ready Docker configuration
11. Proper logging
12. Database migrations
13. Type-safe and well-documented code
14. Reusable services instead of business logic inside views

---

# 44. MVP Development Order

The project should be implemented incrementally.

## Phase 1 — Foundation

```text
Django
PostgreSQL
Docker
Redis
Celery
JWT
Organizations
Users
Roles
```

## Phase 2 — Dataset Management

```text
Excel upload
CSV upload
JSON upload

Dataset preview
Column detection
Data profiling
Data quality
Dataset versioning
```

## Phase 3 — Analytics

```text
Filtering
Sorting
Grouping
Aggregation
Statistics
Date analysis
```

## Phase 4 — Visualization

```text
KPI
Table
Bar
Line
Pie
Area
Scatter
```

## Phase 5 — Dashboard Builder

```text
Drag & Drop
Widget configuration
Dashboard filters
Save dashboard
Edit dashboard
Share dashboard
```

## Phase 6 — Reports

```text
PDF
Excel
CSV
HTML
Scheduled reports
```

## Phase 7 — Industry Templates

```text
Manufacturing
Construction
Logistics
Energy
Retail
Hospitality
```

## Phase 8 — AI

```text
Natural language analytics
Automatic insights
Anomaly detection
Forecasting
Automatic report generation
```

---

# 45. Expected MVP User Experience

A new user should be able to perform the following flow:

```text
1. Register

2. Create Company

3. Select Industry

4. Upload Excel

5. System processes file

6. System detects:
   - columns
   - data types
   - missing values
   - duplicates
   - statistics

7. User opens Data Explorer

8. User creates a chart

9. User adds chart to Dashboard

10. User adds multiple widgets

11. User applies filters

12. User saves Dashboard

13. User generates PDF report

14. User downloads Excel report
```

The complete workflow should be simple enough for a non-technical business user.

---

# 46. Example Product Structure

```text
Industrial Analytics SaaS
│
├── Authentication
│
├── Organization
│
├── Dataset Management
│   ├── Upload
│   ├── Preview
│   ├── Profiling
│   ├── Quality
│   └── Versioning
│
├── Analytics
│   ├── Filter
│   ├── Group
│   ├── Aggregate
│   └── Statistics
│
├── Visualization
│   ├── KPI
│   ├── Table
│   ├── Bar
│   ├── Line
│   ├── Pie
│   └── Area
│
├── Dashboard Builder
│
├── Report Generator
│
├── Industry Templates
│
├── Notifications
│
├── Audit
│
└── AI Analytics
```

---

# 47. Final Product Goal

The final platform should become a localized industrial analytics platform that allows a company to go from:

```text
Raw Excel / CSV / JSON
        ↓
Clean Data
        ↓
Statistics
        ↓
Interactive Analysis
        ↓
Charts
        ↓
Dashboard
        ↓
Professional Report
        ↓
Business Decision
```

The platform should be easy enough for a manager who only knows Excel, while still providing enough flexibility for analysts and technical users.

The system should prioritize:

```text
Simplicity
Performance
Security
Data Privacy
Scalability
Localization
Professional Reporting
Industrial Analytics
```

The MVP must be production-oriented, Dockerized, tested, documented, and designed so that advanced analytics and AI capabilities can be added later without rewriting the core architecture.
