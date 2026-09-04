#!/usr/bin/env python3
"""
Hinbert CLI for FastAPI Boilerplate
Author: Hinbert Team
Created: 2026-09-04
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import click

# ASCII Art Logo
LOGO = """
╔══════════════════════════════════════════════════════════════╗
║    ██╗  ██╗██╗███╗   ██╗██████╗ ███████╗██████╗ ████████╗   ║
║    ██║  ██║██║████╗  ██║██╔══██╗██╔════╝██╔══██╗╚══██╔══╝   ║
║    ███████║██║██╔██╗ ██║██████╔╝█████╗  ██████╔╝   ██║      ║
║    ██╔══██║██║██║╚██╗██║██╔══██╗██╔══╝  ██╔══██╗   ██║      ║
║    ██║  ██║██║██║ ╚████║██████╔╝███████╗██║  ██║   ██║      ║
║    ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝      ║
║                                                              ║
║         Professional FastAPI Boilerplate Generator          ║
╚══════════════════════════════════════════════════════════════╝
"""

@click.group()
def cli():
    """Hinbert FastAPI Boilerplate CLI"""
    click.echo(LOGO)

@cli.command()
@click.argument('project_name')
@click.option('--db', default='postgresql', help='Database (postgresql/mysql/sqlite)')
@click.option('--auth', default='jwt', help='Authentication type')
def init(project_name: str, db: str, auth: str):
    """Initialize a new FastAPI project"""
    click.echo(f"\n🚀 Creating project: {project_name}")
    
    # Ask questions
    click.echo("\n⚙️  Configuration:")
    db = click.prompt("📊 Database", default=db)
    auth = click.prompt("🔐 Authentication", default=auth)
    docker = click.confirm("🐳 Include Docker?")
    k8s = click.confirm("☸️ Include Kubernetes/Helm?")
    
    click.echo("\n📦 Generating project structure...")
    
    # Create project folder
    project_path = Path(project_name)
    project_path.mkdir(exist_ok=True)
    
    # Copy template (your existing code)
    # shutil.copytree(app_dir, project_path / 'app')
    
    # Create .env
    env_file = project_path / '.env.example'
    env_file.write_text("""
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
""")
    
    # Create requirements.txt
    req_file = project_path / 'requirements.txt'
    req_file.write_text("""
fastapi==0.115.0
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
httpx==0.25.1
redis==5.0.1
pytest==7.4.3
pytest-asyncio==0.21.1
loguru==0.7.2
""")
    
    click.echo("""
    
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🎉 Project "%s" is ready!                                ║
    ║                                                              ║
    ║    Next steps:                                               ║
    ║    cd %s                                                     ║
    ║    python -m venv venv                                       ║
    ║    source venv/bin/activate                                  ║
    ║    pip install -r requirements.txt                          ║
    ║    cp .env.example .env                                      ║
    ║    alembic upgrade head                                      ║
    ║    uvicorn app.main:app --reload                            ║
    ║                                                              ║
    ║    📖 Documentation: README.md                               ║
    ╚══════════════════════════════════════════════════════════════╝
    """ % (project_name, project_name))

if __name__ == '__main__':
    cli()