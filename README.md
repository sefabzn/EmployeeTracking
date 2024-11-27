# Employee Tracking System

A comprehensive Django-based employee management system that handles leave requests, attendance tracking, and employee notifications.

## Features

- **Leave Management**
  - Request, approve, and reject leave applications
  - Automatic leave balance tracking
  - Leave history visualization
  - Email notifications for leave status updates

- **Attendance Tracking**
  - Daily check-in/check-out
  - Work hours calculation
  - Late arrival notifications
  - Monthly attendance reports

- **Employee Management**
  - Employee profiles and permissions
  - Admin dashboard for employee oversight
  - Leave balance management
  - Real-time notifications

## Tech Stack

- Django 4.2
- Django REST Framework
- Celery for async tasks
- PostgreSQL
- Docker & Docker Compose
- Bootstrap 5
- Swagger/OpenAPI for API documentation

## Quick Start

1. Clone the repository
2. Start the application using Docker:
docker-compose up --build

3. Create a superuser:
docker-compose exec web python manage.py createsuperuser

4. Access the application:
- Web Interface: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- API Documentation: http://localhost:8000/swagger/

## API Endpoints
- `/api/leave/` - Leave request management
- `/api/attendance/` - Attendance tracking
- `/api/employees/` - Employee management
- `/api/notifications/` - Notification system

## Environment Variables
Create a `.env` file in the root directory:
env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://postgres:postgres@db:5432/employee_tracking
CELERY_BROKER_URL=redis://redis:6379/0


## Development
1. Install dependencies:
 pip install -r requirements.txt
2. Run migrations:
 python manage.py migrate if u are using docker try: docker-compose docker-compose exec web python manage.py migrate
3. Start development server:
   python manage.py runserver
     if u are using docker try:
       docker-compose up --build
