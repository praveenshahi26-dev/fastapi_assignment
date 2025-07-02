# BlokID Backend

A FastAPI-based backend service implementing a complete user authentication and authorization system with organizations and websites management.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [User Roles and Permissions](#user-roles-and-permissions)
- [Testing](#testing)
- [Deployment](#deployment)

## Project Overview

This project implements a RESTful API using FastAPI and PostgreSQL, focusing on user authentication, authorization, and data relationships. It provides a complete solution for managing users, organizations, and websites with role-based access control.

## Features

- **User Management**
  - User registration with email and password
  - JWT-based authentication
  - Email verification for new users
  - Profile management

- **Organization Management**
  - Automatic organization creation on user registration
  - CRUD operations for organizations
  - Role-based access control

- **Website Management**
  - CRUD operations for websites
  - Website association with organizations
  - Granular permission control

- **Security**
  - Secure password hashing
  - JWT token authentication
  - Role-based access control
  - Input validation using Pydantic

## Technology Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)
- **Testing**: Pytest (optional but recommended)
- **Email Service**: SMTP (for email verification)

## Prerequisites

- Python 3.8+
- PostgreSQL 13+
- pip (Python package manager)

## Setup and Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd try_3/blokid-backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   - Create a new PostgreSQL database
   - Update the `.env` file with your database credentials

5. **Initialize the database**
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/dbname

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (Optional, for email functionality)
SMTP_SERVER=smtp.example.com
SMTP_PORT=465
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-email-password
```

## Running the Application

1. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Project Structure

```
blokid-backend/
├── .env                    # Environment variables
├── .env.example            # Example environment variables
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application instance
│   ├── database.py         # Database connection and session management
│   ├── models/             # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py         # User model and schemas
│   │   ├── organization.py # Organization model
│   │   └── website.py      # Website model
│   ├── routers/            # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── organizations.py # Organization CRUD operations
│   │   └── websites.py      # Website management
│   └── schemas/            # Pydantic models for request/response
│       └── ...
├── tests/                  # Test files
├── alembic/                # Database migrations
├── requirements.txt        # Python dependencies
└── pyproject.toml          # Project metadata and build configuration
```

## Data Flow

1. **Authentication Flow**
   - User registers with email and password
   - System sends verification email
   - After verification, user can log in to receive JWT token
   - Token is used for subsequent authenticated requests

2. **Organization Management**
   - New organization is automatically created during user registration
   - Organization admin can invite other users
   - Role-based access control for organization resources

3. **Website Management**
   - Organization members can manage websites based on their roles
   - Website data includes domain, verification status, and metadata
   - Access control is enforced at both organization and website levels

## User Roles and Permissions

### Organization Level

**Organization Admin**
- Full access to the organization and its websites
- Can invite users to the organization with different roles
- Permissions:
  - Organization: CRUD operations
  - Websites: CRUD operations, invite website members

**Organization User**
- Limited access to the organization and its websites
- Permissions:
  - Organization: Read and update operations
  - Websites: Read, create, and update operations

### Website Level

**Website Admin**
- Full access to the specific website
- Can invite users with website-level access
- Permissions:
  - Website: CRUD operations, invite website members

**Website User**
- Limited access to the specific website
- Permissions:
  - Website: Read and update operations

## API Endpoints

### Authentication

#### Register New User
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

#### Login
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "user@example.com",
    "password": "securepassword123"
  }'
```
*Save the access token from the response for authenticated requests*

#### Get Current User Info
```bash
curl -X 'GET' \
  'http://localhost:8000/auth/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

### Users

#### Get All Users (Admin only)
```bash
curl -X 'GET' \
  'http://localhost:8000/users/?skip=0&limit=100' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

#### Get User by ID
```bash
curl -X 'GET' \
  'http://localhost:8000/users/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

#### Update User
```bash
curl -X 'PUT' \
  'http://localhost:8000/users/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "full_name": "Updated Name",
    "email": "updated@example.com"
  }'
```

### Organizations

#### Create Organization
```bash
curl -X 'POST' \
  'http://localhost:8000/organizations/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Acme Corp",
    "description": "Organization description"
  }'
```

#### List User's Organizations
```bash
curl -X 'GET' \
  'http://localhost:8000/organizations/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

#### Get Organization by ID
```bash
curl -X 'GET' \
  'http://localhost:8000/organizations/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

#### Invite User to Organization
```bash
curl -X 'POST' \
  'http://localhost:8000/organizations/1/invite' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "newmember@example.com",
    "role": "member"
  }'
```

### Websites

#### Create Website
```bash
curl -X 'POST' \
  'http://localhost:8000/websites/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "domain": "example.com",
    "organization_id": 1,
    "description": "Main company website"
  }'
```

#### List User's Websites
```bash
curl -X 'GET' \
  'http://localhost:8000/websites/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

#### Get Website by ID
```bash
curl -X 'GET' \
  'http://localhost:8000/websites/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

#### Invite User to Website
```bash
curl -X 'POST' \
  'http://localhost:8000/websites/1/invite' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "editor@example.com",
    "role": "editor"
  }'
```

#### List Organization's Websites
```bash
curl -X 'GET' \
  'http://localhost:8000/websites/organization/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

## Testing

Run tests using pytest:

```bash
pytest
```

## Running the Server

To start the development server:

```bash
uvicorn app.main:app --reload
```

For production, use Gunicorn with Uvicorn workers:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## License

[Your License Here]

## Support

For support, please contact [your-email@example.com]
