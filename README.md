# DRIVE X

A production-ready Google Drive clone built with SvelteKit and FastAPI.

## Tech Stack

### Frontend
- **SvelteKit**: Modern web framework.
- **TailwindCSS**: Utility-first CSS.
- **Lucide Icons**: Beautiful icons.
- **Axios**: API client.

### Backend
- **FastAPI**: High-performance Python API framework.
- **PostgreSQL**: Robust relational database.
- **SQLAlchemy**: Async ORM.
- **Alembic**: Database migrations.
- **JWT**: Secure authentication.

## Features
- **Authentication**: Secure signup and login.
- **File Management**: Upload, download, rename, and delete files.
- **Folder Management**: Create and navigate nested folders.
- **Search**: Find files quickly.
- **Starred & Recent**: Quick access to important files.
- **Trash**: Soft-delete and permanent removal.

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL

### Backend Setup
1. `cd backend`
2. `python -m venv venv`
3. `.\venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. Configure `.env`
6. `alembic upgrade head`
7. `uvicorn app.main:app --reload`

### Frontend Setup
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## License
MIT
