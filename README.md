README.md - Complete Project Documentation
Markdown

# 🔗 OneLink — All Important Links in One Place

> A professional link directory portal built with Django + PostgreSQL.
> Organize, discover, and access all important government, information,
> and service links from one central place.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?style=flat-square&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=flat-square&logo=bootstrap)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Local Development Setup](#local-development-setup)
- [Database Setup](#database-setup)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [Admin Portal](#admin-portal)
- [Deployment](#deployment)
- [How It Works](#how-it-works)
- [CSV Import/Export](#csv-importexport)
- [PWA Support](#pwa-support)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)

---

## 🌐 Overview

**OneLink** is a full-stack web application that serves as a centralized
directory of important links — government portals, information services,
utility websites, and more.

Users can:
- Browse and search links by category, tag, or keyword
- Bookmark favorite links (session-based)
- Rate and report links
- View most popular and recently added links
- Install as a PWA (Progressive Web App)

Admins can:
- Add, edit, delete categories and links
- Tag links with multiple tags
- Pin featured links
- Import links via CSV
- Export all data
- View click analytics
- Manage user reports and feedback

### Live Demo


🌍 Live Site:  https://link-portal.onrender.com
🔐 Admin:      https://link-portal.onrender.com/secret-admin-portal/
✨ Features
Public Portal
✅ Homepage with search, filters, featured links
✅ Category-based filtering
✅ Multi-tag system
✅ Smart search with synonym expansion
✅ Auto-suggest dropdown while typing
✅ Sort by: Newest, Popular, Rating, A-Z
✅ Featured/Pinned links section
✅ Most Popular links (Top 10)
✅ Recently Added (This Week)
✅ Recently Visited (session-based history)
✅ Bookmarking / Favorites
✅ Star Rating system (1-5)
✅ Report broken/wrong links
✅ Feedback submission
✅ Click tracking & analytics
✅ Dark Mode / Light Mode toggle
✅ PWA — installable as mobile app
✅ Fully responsive (Mobile + Desktop)
✅ SEO-friendly URLs
✅ Auto-generated sitemap
✅ Open Graph meta tags
✅ Keyboard shortcut: Press / to search




### Admin Portal (Hidden)


✅ Hidden URL: /secret-admin-portal/
✅ Staff/Superuser access only
✅ Add / Edit / Delete Categories
✅ Add / Edit / Delete Links
✅ Multi-category support per link
✅ Multi-tag support per link
✅ Pin/Unpin featured links
✅ CSV import (bulk upload)
✅ CSV export (full backup)
✅ Click analytics chart (30 days)
✅ Top 10 most clicked links
✅ View and resolve user reports
✅ Read user feedback
✅ Manage tags
✅ Version history on link edits
✅ Duplicate URL detection
🛠️ Tech Stack
Backend: Python 3.11 + Django 4.2
Database: PostgreSQL (Production) / SQLite (Development)
Frontend: Bootstrap 5.3 + Custom CSS (CSS Variables)
Icons: Bootstrap Icons 1.11
Fonts: Inter + JetBrains Mono (Google Fonts)
Server: Gunicorn
Static: WhiteNoise
Hosting: Render.com (App) + Railway.app (Database)
PWA: Service Worker + Web Manifest




---

## 📁 Project Structure


OneLink/                              ← Project Root
│
├── manage.py                         ← Django CLI entry point
├── requirements.txt                  ← Python dependencies
├── Procfile                          ← Render/Heroku start command
├── runtime.txt                       ← Python version for deployment
├── nixpacks.toml                     ← Railway build config
├── build.sh                          ← Deployment build script
├── .gitignore                        ← Git ignore rules
├── db.sqlite3                        ← Local SQLite database
│
├── linkportal/                       ← Django Project Config
│   ├── __init__.py
│   ├── settings.py                   ← All settings (DB, static, etc.)
│   ├── urls.py                       ← Root URL configuration
│   ├── wsgi.py                       ← WSGI entry point
│   └── asgi.py                       ← ASGI entry point
│
├── core/                             ← Main Django Application
│   ├── __init__.py
│   ├── models.py                     ← Database models
│   ├── views.py                      ← All view logic
│   ├── urls.py                       ← App URL patterns
│   ├── forms.py                      ← Django forms
│   ├── admin.py                      ← Django admin registration
│   ├── context_processors.py         ← Global template variables
│   │
│   ├── migrations/                   ← Database migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   │
│   ├── management/                   ← Custom management commands
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── check_links.py        ← Broken link detector
│   │
│   ├── templatetags/                 ← Custom template filters
│   │   ├── __init__.py
│   │   └── core_tags.py              ← star_range, empty_star_range
│   │
│   └── templates/
│       └── core/
│           ├── base.html             ← Base template (head, scripts)
│           ├── index.html            ← Public homepage
│           ├── admin_login.html      ← Hidden admin login page
│           └── admin_dashboard.html  ← Full admin panel
│
└── static/                           ← Static Assets
    ├── css/
    │   └── style.css                 ← All custom CSS + Dark mode
    ├── js/
    │   └── app.js                    ← All JavaScript (search, rating, etc.)
    ├── manifest.json                 ← PWA manifest
    └── sw.js                         ← Service Worker (offline support)
🗄️ Database Models
┌─────────────────────────────────────────────────────────┐
│ DATABASE SCHEMA │
├───────────────┬─────────────────────────────────────────┤
│ Category │ name, slug, icon, color, description, │
│ │ order, is_active │
├───────────────┼─────────────────────────────────────────┤
│ Tag │ name, slug │
├───────────────┼─────────────────────────────────────────┤
│ Link │ title, slug, url, description, │
│ │ categories(M2M), tags(M2M), │
│ │ is_featured, is_active, click_count, │
│ │ avg_rating, total_ratings, link_status, │
│ │ favicon, created_at, created_by │
├───────────────┼─────────────────────────────────────────┤
│ LinkVersion │ link, title, url, description, │
│ │ changed_by, changed_at, change_note │
├───────────────┼─────────────────────────────────────────┤
│ ClickLog │ link, clicked_at, ip_address, │
│ │ user_agent, session_key │
├───────────────┼─────────────────────────────────────────┤
│ Rating │ link, score(1-5), session_key │
├───────────────┼─────────────────────────────────────────┤
│ Bookmark │ link, session_key │
├───────────────┼─────────────────────────────────────────┤
│ Report │ link, report_type, message, │
│ │ email, is_resolved │
├───────────────┼─────────────────────────────────────────┤
│ Feedback │ name, email, message, is_read │
├───────────────┼─────────────────────────────────────────┤
│ BrowsingHistory│ link, session_key, visited_at │
└───────────────┴─────────────────────────────────────────┘




---

## 💻 Local Development Setup

### Prerequisites


✓ Python 3.11+ installed
✓ Git installed
✓ VS Code (recommended)
Step 1 — Clone the Repository

git clone https://github.com/yourusername/OneLink.git
cd OneLink
Step 2 — Create Virtual Environment


# Create
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# You should see (venv) in your terminal
Step 3 — Install Dependencies

pip install -r requirements.txt
Step 4 — Run Migrations (Creates db.sqlite3)

# Make sure DATABASE_URL is NOT set
# Windows:
set DATABASE_URL=

# Run migrations
python manage.py makemigrations core
python manage.py migrate
Step 5 — Create Admin User

python manage.py createsuperuser

# Fill in:
# Username: admin
# Email: admin@example.com
# Password: yourpassword
Step 6 — Run the Server

python manage.py runserver
Step 7 — Open in Browser
Public Site: http://127.0.0.1:8000/
Admin Login: http://127.0.0.1:8000/secret-admin-portal/
Django Admin: http://127.0.0.1:8000/django-admin/

---

## 🗃️ Database Setup

### Local Development (SQLite — Default)

No setup needed!
When DATABASE_URL is NOT set, Django automatically
uses SQLite and creates db.sqlite3 in the project root.
Production (PostgreSQL — Railway)
Create account at railway.app
New Project → Add PostgreSQL
Copy the PUBLIC connection URL:
postgresql://postgres:password@host:port/railway
Add as DATABASE_URL environment variable in Render


### How Django Chooses the Database

```python
# In settings.py:

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production → Uses Railway PostgreSQL
    DATABASES = {'default': dj_database_url.config(...)}
else:
    # Local → Uses SQLite file
    DATABASES = {'default': {'ENGINE': 'sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
🔐 Environment Variables
Local Development
No .env file needed for basic local development.
SQLite is used automatically.

Optional .env for connecting to Railway DB locally:



```env
# .env (not committed to git)
DATABASE_URL=postgresql://postgres:pass@host:port/railway
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=any-local-key
Production (Set in Render Dashboard)
┌──────────────────────────┬──────────────────────────────────────┐
│ Variable │ Value │
├──────────────────────────┼──────────────────────────────────────┤
│ DATABASE_URL │ postgresql://... (Railway public URL)│
│ DJANGO_SECRET_KEY │ generated secure key │
│ DJANGO_DEBUG │ False │
│ DJANGO_ALLOWED_HOSTS │ .onrender.com,link-portal.onrender.com│
│ PYTHON_VERSION │ 3.11.0 │
│ DJANGO_SUPERUSER_USERNAME│ admin │
│ DJANGO_SUPERUSER_EMAIL │ admin@example.com │
│ DJANGO_SUPERUSER_PASSWORD│ securepassword │
└──────────────────────────┴──────────────────────────────────────┘


### Generate a Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
▶️ Running the Project
Daily Development Commands

# 1. Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# 2. Make sure local DB is used
set DATABASE_URL=              # Windows (clears Railway URL if set)

# 3. Run development server
python manage.py runserver

# 4. Open browser
# http://127.0.0.1:8000/

# 5. Stop server
# Press Ctrl + C
Database Commands

# Create new migration after model changes
python manage.py makemigrations core

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Create superuser
python manage.py createsuperuser
Useful Utility Commands

# Check for broken links
python manage.py check_links

# Export data backup
python manage.py dumpdata core --indent 2 > backup.json

# Restore from backup
python manage.py loaddata backup.json

# Open Django shell
python manage.py shell

# Check for code issues
python manage.py check
🔑 Admin Portal
Access
URL: http://127.0.0.1:8000/secret-admin-portal/
(Hidden from public — direct URL access only)

Login: Use your superuser credentials


### Admin Dashboard Sections

┌─────────────────────────────────────────────────────┐
│  Tab         │ Features                             │
├──────────────┼──────────────────────────────────────┤
│  Links       │ Add/Edit/Delete links                │
│              │ Search links                         │
│              │ Toggle featured                      │
│              │ See click count and rating           │
│              │ See link status (Active/Broken)      │
├──────────────┼──────────────────────────────────────┤
│  Categories  │ Add/Edit/Delete categories           │
│              │ Set icon and color                   │
│              │ Set display order                    │
├──────────────┼──────────────────────────────────────┤
│  Analytics   │ 30-day click chart                   │
│              │ Top 10 most clicked links            │
├──────────────┼──────────────────────────────────────┤
│  Import/Export│ CSV bulk import                     │
│              │ CSV full export/backup               │
├──────────────┼──────────────────────────────────────┤
│  Reports     │ View user-submitted reports          │
│              │ Mark as resolved                     │
├──────────────┼──────────────────────────────────────┤
│  Feedback    │ View user feedback                   │
│              │ Mark as read                         │
├──────────────┼──────────────────────────────────────┤
│  Tags        │ View all tags                        │
│              │ Delete unused tags                   │
└──────────────┴──────────────────────────────────────┘
Adding Your First Links
Step 1: Go to admin → Categories tab → Add Category
Example:
Name: Government
Icon: bi-bank
Color: #0d6efd
Order: 1

Step 2: Go to admin → Links tab → Add Link
Example:
Title: Ahara Karnataka
URL: https://ahara.karnataka.gov.in
Description: Check Food, BPL and Ration Card Details
Categories: ✓ Government
Tags: Ration, Food, BPL, Ration Card
Featured: ✓

---

## 🚀 Deployment

### Architecture

GitHub Repo
    │
    │ git push (auto-trigger)
    ▼
Render.com (Web Server)
    │ Django App
    │ Gunicorn
    │ WhiteNoise (static files)
    │
    ▼
Railway.app (Database)
    │ PostgreSQL
    │ Public URL: thomas.proxy.rlwy.net
    └─────────────────────────────────
Step 1 — Push to GitHub

git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/OneLink.git
git branch -M main
git push -u origin main
Step 2 — Create Railway PostgreSQL
Go to railway.app → Login with GitHub
New Project → Add PostgreSQL
Copy the PUBLIC connection URL
(thomas.proxy.rlwy.net:PORT format)


### Step 3 — Deploy on Render

1. Go to render.com → New → Web Service
2. Connect your GitHub repo
3. Fill in settings:

   Name:          link-portal
   Branch:        main
   Runtime:       Python 3
   Build Command: ./build.sh
   Start Command: gunicorn linkportal.wsgi:application

4. Add Environment Variables (see table above)
5. Click "Create Web Service"
6. Wait 3-5 minutes for first deploy
Step 4 — Create Production Admin User
Option A: Via build.sh (automatic)
Add to Render environment variables:
DJANGO_SUPERUSER_USERNAME = admin
DJANGO_SUPERUSER_EMAIL = admin@example.com
DJANGO_SUPERUSER_PASSWORD = yourpassword

Option B: Via Render Shell
python manage.py createsuperuser

### Step 5 — Access Live Site

Public Site:  https://link-portal.onrender.com
Admin:        https://link-portal.onrender.com/secret-admin-portal/
build.sh (Runs on Every Deploy)

#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser --noinput || true
🌐 URL Structure
Public URLs:
┌─────────────────────────────────────┬──────────────────────────┐
│ URL │ View │
├─────────────────────────────────────┼──────────────────────────┤
│ / │ Homepage │
│ /go/<id>/ │ Track click + redirect │
│ /service/<slug>/ │ SEO service page │
│ /category/<slug>/ │ Category filter page │
│ /sitemap.xml │ Auto sitemap │
├─────────────────────────────────────┼──────────────────────────┤
│ API Endpoints: │ │
│ /api/suggest/?q= │ Auto-suggest (AJAX) │
│ /api/bookmark/<id>/ │ Toggle bookmark (POST) │
│ /api/rate/<id>/ │ Rate link (POST) │
│ /api/report/<id>/ │ Submit report (POST) │
│ /api/feedback/ │ Submit feedback (POST) │
│ /api/bookmarks/ │ Get bookmarks │
├─────────────────────────────────────┼──────────────────────────┤
│ Admin URLs (Hidden): │ │
│ /secret-admin-portal/ │ Admin login │
│ /secret-admin-portal/dashboard/ │ Admin dashboard │
│ /secret-admin-portal/logout/ │ Admin logout │
│ /secret-admin-portal/export-csv/ │ Export CSV │
│ /django-admin/ │ Django built-in admin │
└─────────────────────────────────────┴──────────────────────────┘

---

## 📊 How It Works — Web Flow

User visits homepage /
        │
        ▼
index view loads:
  - All active categories
  - All active links (filtered/sorted)
  - Featured links
  - Popular links (top 10 by clicks)
  - Recent links (this week)
  - Tags (with link count)
  - User bookmarks (from session)
  - User history (from session)
        │
        ▼
User clicks a link
        │
        ▼
/go/<id>/ → track_click view:
  1. Increments click_count
  2. Creates ClickLog record
  3. Updates BrowsingHistory
  4. Redirects to actual URL
        │
        ▼
User lands on external website
Search Flow
User types in search box
│
├─ After 300ms debounce →
│ AJAX call to /api/suggest/?q=query
│ Returns top 8 matching links
│ Shown in dropdown
│
└─ User presses Enter / clicks Search →
GET request to / with ?q=query
Server expands query with synonyms
Searches title + description + tags + categories
Returns filtered results


### Admin Add Link Flow

Admin fills "Add Link" form
        │
        ▼
POST to /secret-admin-portal/dashboard/?action=add_link
        │
        ├─ Check duplicate URL
        ├─ Save Link object
        ├─ Save M2M categories
        ├─ Parse tags (comma separated)
        ├─ Get or create Tag objects
        └─ Set tags on link
        │
        ▼
Link appears on homepage instantly
📤 CSV Import/Export
Import Format
csv

Category,Website Name,URL,Description,Tags
Government,Ahara Karnataka,https://ahara.karnataka.gov.in,Food and Ration Details,Ration Food BPL
Information,Parivahan,https://parivahan.gov.in,Vehicle Details,Vehicle License RC
Government + Information,Traffic Portal,https://kspapp.ksp.gov.in,Check Challan,Traffic Challan
Rules:

Column 1: Category name (use + for multiple categories)
Column 2: Link title
Column 3: Full URL with https://
Column 4: Short description
Column 5: Tags (space separated) — optional
How to import:
Admin Dashboard → Import/Export tab → Choose file → Import

### Export

Admin Dashboard → Import/Export tab → Export All Links
Downloads: links_export.csv with all data
📱 PWA Support
OneLink works as a Progressive Web App!

Users can install it:

On Android: Chrome → 3 dots menu → Add to Home Screen
On iOS: Safari → Share → Add to Home Screen
On Desktop: Chrome address bar → Install icon
Features:
✓ Works offline (cached pages)
✓ App-like experience
✓ No browser chrome
✓ Fast loading

---

## 🔍 Smart Search

The search uses synonym expansion.
When you search for one term, it also
searches for related terms.

Examples:
"RC"      → also finds: ration card, ration, ahara
"DL"      → also finds: driving license, licence
"vehicle" → also finds: parivahan, vahan, registration
"aadhar"  → also finds: aadhaar, uidai, aadhar card
"pan"     → also finds: pan card, income tax
"challan" → also finds: traffic, fine
"ration"  → also finds: bpl, ahara, food

Add more synonyms in settings.py under SEARCH_SYNONYMS
🔧 Troubleshooting
Common Issues
Problem: "No module named 'django'"
Fix: venv\Scripts\activate
(virtual environment not activated)

Problem: "relation does not exist"
Fix: python manage.py migrate

Problem: "DisallowedHost"
Fix: Add your domain to DJANGO_ALLOWED_HOSTS
environment variable in Render

Problem: CSS not loading locally
Fix: Make sure DEBUG=True in settings.py
Hard refresh: Ctrl + Shift + R

Problem: CSS not loading on Render
Fix: Check STATICFILES_STORAGE setting
Check whitenoise in requirements.txt
Check whitenoise in MIDDLEWARE

Problem: Database connection refused (local)
Fix: PostgreSQL service not running
OR set DATABASE_URL= to use SQLite

Problem: "Port 8000 already in use"
Fix: python manage.py runserver 8080

Problem: Render site sleeping (free tier)
Fix: Set up uptimerobot.com to ping every 5 min

Problem: Supabase paused (free tier)
Fix: Login to supabase.com → Click Restore

### Check Everything is Working

```bash
# Run this to verify setup
python manage.py check

# Should output:
# System check identified no issues (0 silenced).
📦 Dependencies
Package Version Purpose
──────────────────── ───────── ──────────────────────────
Django >=4.2,<5 Web framework
psycopg2-binary >=2.9.9 PostgreSQL adapter
requests >=2.31.0 HTTP for link checking
Pillow >=10.1.0 Image processing
gunicorn >=21.2.0 Production WSGI server
whitenoise >=6.6.0 Static file serving
dj-database-url >=2.1.0 Database URL parser
python-dotenv >=1.0.0 .env file support

---

## 🗓️ Roadmap

Phase 1 — Core ✅ DONE
  ✅ Public portal with search
  ✅ Category + tag filtering
  ✅ Admin portal (hidden)
  ✅ Click tracking
  ✅ Rating system
  ✅ Bookmarks
  ✅ Reports + Feedback
  ✅ CSV import/export
  ✅ Dark mode
  ✅ PWA support
  ✅ Broken link detection

Phase 2 — In Progress 🔄
  🔄 Better UI design
  🔄 Admin dashboard UI improvements
  ⬜ Email notifications for reports

Phase 3 — Planned ⬜
  ⬜ User accounts (optional login)
  ⬜ Personal dashboards
  ⬜ AI-powered search
  ⬜ Automatic broken link emails
  ⬜ Link categories API
  ⬜ Multi-language support (Kannada)
  ⬜ Google Analytics integration
📁 Key Files Reference
File Purpose
──────────────────────────────── ──────────────────────────────
linkportal/settings.py All configuration
linkportal/urls.py Root URL routing
core/models.py All database models
core/views.py All page and API logic
core/urls.py App URL patterns
core/forms.py All forms (Admin, Report, etc.)
core/context_processors.py site_name, site_tagline globals
core/templatetags/core_tags.py star_range template filter
core/templates/core/base.html HTML head, scripts, meta
core/templates/core/index.html Public homepage
core/templates/core/admin_login.html Admin login page
core/templates/core/admin_dashboard.html Full admin panel
static/css/style.css All styling + dark mode
static/js/app.js Search, bookmarks, rating, PWA
static/manifest.json PWA configuration
static/sw.js Service Worker
build.sh Render deployment script
Procfile Gunicorn start command
runtime.txt Python version
requirements.txt All Python packages
.gitignore Files excluded from git

---

## 👨‍💻 Development Notes

Local vs Production:

Setting          Local               Production
───────────────  ──────────────────  ──────────────────
DEBUG            True                False
DATABASE         SQLite (db.sqlite3) Railway PostgreSQL
STATIC_STORAGE   Default Django      WhiteNoise
SECRET_KEY       Hardcoded (dev)     Environment variable
SSL              No                  Yes (auto via Render)
ALLOWED_HOSTS    localhost           .onrender.com

Every time you push to GitHub:
→ Render auto-detects the push
→ Runs build.sh (install, collectstatic, migrate)
→ Restarts with Gunicorn
→ Zero downtime deployment
📝 License
MIT License

Copyright (c) 2024 Sanjay

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software to deal in the Software
without restriction.

---

## 🙏 Credits

Built with:
- Django — https://www.djangoproject.com
- Bootstrap 5 — https://getbootstrap.com
- Bootstrap Icons — https://icons.getbootstrap.com
- Inter Font — https://rsms.me/inter
- Render.com — https://render.com
- Railway.app — https://railway.app

Developed by: Sanjay
GitHub: https://github.com/yourusername/OneLink
Last updated: June 2026

---

## Save This File
Save as: README.md
Location: OneLink/ (project root, same level as manage.py)

## Then Push to GitHub

```bash
git add README.md
git commit -m "Add complete README documentation"
git push

GitHub will automatically display this README
on your repository homepage! ✅