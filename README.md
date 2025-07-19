# ParKing app

A simple web application to manage parking lots, built as part of the MAD I – May 2025 project.

## Overview

**ParKing** lets admins create and manage parking lots and spots, while users can register, book and release parking spots for their cars. The app works fully on your local machine.

## Features

- **Admin (superuser):**
  - No registration required
  - Create, edit, delete parking lots (each with multiple spots)
  - View and search all parking spots
  - View all users
  - Get dashboard and summary charts

- **User:**
  - Register and log in
  - See available lots and book a parking spot (auto-assigned)
  - Release/vacate parking spot when leaving
  - Check booking history and personal summary charts

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** Jinja2, HTML, CSS, Bootstrap
- **Database:** SQLite (auto-created, no manual setup needed)

## Start with the project

**Clone the repo**

```bash
git clone git@github.com:robotecht/ParKing-app.git
```

**Navigate to the folder and create a virtual environment (recommended)**
```bash
cd ParKing-app
python -m venv venv
```
**Activate the Virtual Environment**

On Linux
```bash
source venv/bin/activate
```
On Windows
```bash
venv\Scripts\activate
```
**Install Dependencies**
```bash
pip install flask flask_sqlalchemy flask_bootstrap

```
**Run the flask container**
```bash
flask run
```