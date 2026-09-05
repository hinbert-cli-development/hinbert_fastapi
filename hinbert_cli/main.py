#!/usr/bin/env python3
import ast
import os
import re
import shutil
import sys
from pathlib import Path

import click

# ============================================================
# FIX 1: Windows Unicode Support
# ============================================================
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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

DATABASES = {
    "postgresql": {
        "url": "postgresql+asyncpg://user:password@localhost:5432/{name}",
        "alembic_url": "postgresql+asyncpg://user:password@localhost:5432/{name}",
        "driver": "asyncpg>=0.29,<1.0",
        "env_url": "postgresql+asyncpg://user:password@localhost:5432/{name}",
    },
    "mysql": {
        "url": "mysql+aiomysql://user:password@localhost:3306/{name}",
        "alembic_url": "mysql+aiomysql://user:password@localhost:3306/{name}",
        "driver": "aiomysql>=0.2,<1.0",
        "env_url": "mysql+aiomysql://user:password@localhost:3306/{name}",
    },
    "sqlite": {
        "url": "sqlite+aiosqlite:///./{name}.db",
        "alembic_url": "sqlite+aiosqlite:///./{name}.db",
        "driver": "aiosqlite>=0.20,<1.0",
        "env_url": "sqlite+aiosqlite:///./{name}.db",
    },
}


def remove_paths(project_path, relative_paths):
    """Remove optional generated files without affecting unrelated files."""
    for relative_path in relative_paths:
        path = project_path / relative_path
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink()


def remove_pycache(project_path):
    """Remove all __pycache__ directories from generated project."""
    for root, dirs, files in os.walk(project_path):
        if "__pycache__" in dirs:
            cache_dir = Path(root) / "__pycache__"
            shutil.rmtree(cache_dir, ignore_errors=True)


def remove_empty_dirs(path):
    """Remove empty directories after file deletions."""
    if not path.exists():
        return
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_dirs(item)
    try:
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    except OSError:
        pass


# ============================================================
# IMPORT CLEANUP FUNCTIONS
# ============================================================
def cleanup_imports(project_path, removed_modules):
    """Remove imports and decorators that reference deleted optional modules."""
    app_path = project_path / "app"
    removed_modules = {f"app.{module.replace('/', '.')}" for module in removed_modules}

    for python_file in app_path.rglob("*.py"):
        source = python_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(python_file))
        except SyntaxError:
            continue

        lines = source.splitlines(keepends=True)
        remove_lines = set()
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.ImportFrom):
                module = node.module if not node.level else None
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in removed_modules:
                        remove_lines.add(node.lineno - 1)
                continue
            if module in removed_modules or any(module and module.startswith(f"{removed}.") for removed in removed_modules):
                remove_lines.add(node.lineno - 1)

        cleaned = "".join(line for index, line in enumerate(lines) if index not in remove_lines)

        if "app.core.middleware.rate_limit" in removed_modules:
            cleaned = re.sub(r"^.*@limiter\.limit\([^\n]*\)\n", "", cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r"^.*from slowapi\.middleware import SlowAPIMiddleware\n", "", cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r"^.*application\.state\.limiter.*\n", "", cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r"^.*application\.add_middleware\(SlowAPIMiddleware\)\n", "", cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r"^.*register_rate_limit\(application\)\n", "", cleaned, flags=re.MULTILINE)

        if "app.utils.logger" in removed_modules:
            cleaned = re.sub(r"^.*from app\.core\.middleware\.logging import RequestLoggingMiddleware\n", "", cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r"^.*application\.add_middleware\(RequestLoggingMiddleware\)\n", "", cleaned, flags=re.MULTILINE)

        if cleaned != source:
            python_file.write_text(cleaned, encoding="utf-8")


def remove_functions(file_path, function_names):
    """Remove named functions and their decorators from a generated module."""
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    lines = source.splitlines(keepends=True)
    remove_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in function_names:
            start = min((decorator.lineno for decorator in node.decorator_list), default=node.lineno) - 1
            remove_lines.update(range(start, node.end_lineno))
    file_path.write_text(
        "".join(line for index, line in enumerate(lines) if index not in remove_lines),
        encoding="utf-8",
    )


def remove_imports_from_file(file_path, removed_modules):
    """Remove imports for deleted modules from one generated Python file."""
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    modules = {f"app.{module.replace('/', '.')}" for module in removed_modules}
    lines = source.splitlines(keepends=True)
    remove_lines = set()
    for node in ast.walk(tree):
        module = node.module if isinstance(node, ast.ImportFrom) and not node.level else None
        if module in modules:
            remove_lines.add(node.lineno - 1)
    file_path.write_text(
        "".join(line for index, line in enumerate(lines) if index not in remove_lines),
        encoding="utf-8",
    )


def remove_class_attributes(file_path, class_name, attribute_names):
    """Remove selected annotated attributes from a generated model class."""
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    lines = source.splitlines(keepends=True)
    remove_lines = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name) and child.target.id in attribute_names:
                        remove_lines.update(range(child.lineno - 1, child.end_lineno))
    file_path.write_text(
        "".join(line for index, line in enumerate(lines) if index not in remove_lines),
        encoding="utf-8",
    )


def write_none_auth_modules(project_path):
    """Provide auth helpers outside security/ before removing that package."""
    utils_dir = project_path / "app" / "utils"
    (utils_dir / "password.py").write_text(
        '"""Password hashing helpers for projects without a security package."""\n\n'
        "from passlib.context import CryptContext\n\n"
        "pwd_context = CryptContext(schemes=[\"bcrypt\"], deprecated=\"auto\")\n\n"
        "def hash_password(password: str) -> str:\n    return pwd_context.hash(password)\n\n"
        "def verify_password(password: str, hashed_password: str) -> bool:\n    return pwd_context.verify(password, hashed_password)\n",
        encoding="utf-8",
    )
    (utils_dir / "auth.py").write_text(
        '"""Minimal token helpers for projects without external authentication."""\n\n'
        "def create_token(subject, token_type, expires_delta) -> str:\n    return str(subject)\n\n"
        "def decode_token(token: str, expected_type: str = \"access\") -> dict[str, str]:\n"
        "    if not token:\n        raise ValueError(\"Invalid token\")\n"
        "    return {\"sub\": token, \"type\": expected_type}\n",
        encoding="utf-8",
    )


def configure_none_auth(project_path):
    """Redirect generated consumers before deleting app/core/security."""
    for python_file in project_path.rglob("*.py"):
        content = python_file.read_text(encoding="utf-8")
        content = content.replace("app.core.security.password", "app.utils.password")
        content = content.replace("app.core.security.auth", "app.utils.auth")
        content = content.replace("app.core.security.jwt", "app.utils.auth")
        python_file.write_text(content, encoding="utf-8")


def snapshot_tree(path):
    """Capture existing files so current-directory generation can be restored."""
    if not path.exists():
        return {}
    return {
        item.relative_to(path): item.read_bytes()
        for item in path.rglob("*")
        if item.is_file()
    }


def restore_tree(path, snapshot):
    """Restore overwritten files and remove files created during generation."""
    current_files = {item for item in path.rglob("*") if item.is_file()}
    for item in current_files:
        if item.relative_to(path) not in snapshot:
            item.unlink()
    for relative, content in snapshot.items():
        destination = path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    for directory in sorted((item for item in path.rglob("*") if item.is_dir()), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass


def write_structlog_logger(logger_file):
    logger_file.write_text(
        '''"""Central structlog configuration."""\n\nimport structlog\n\nlogger = structlog.get_logger()\n''',
        encoding="utf-8",
    )


def write_auth_files(project_path, auth):
    """Write the token boundary used by generated authentication dependencies."""
    security_dir = project_path / "app" / "core" / "security"
    auth_file = security_dir / "auth.py"
    password_import = "from app.core.security.password import verify_password"
    password_function = "\n\ndef authenticate_password(password: str, password_hash: str) -> bool:\n    return verify_password(password, password_hash)\n"

    if auth == "jwt":
        auth_file.write_text(
            '"""Authentication boundary for JWT projects."""\n\n'
            "from app.core.security.jwt import decode_token\n"
            f"{password_import}\n"
            f"{password_function}",
            encoding="utf-8",
        )
        return

    if auth == "oauth2":
        auth_file.write_text(
            '"""Authentication boundary for OAuth2 projects."""\n\n'
            "from datetime import UTC, datetime, timedelta\n"
            "from typing import Any\n"
            "from jose import JWTError, jwt\n"
            "from app.core.config.settings import get_settings\n"
            f"{password_import}\n"
            "\n\ndef create_token(subject, token_type: str, expires_delta: timedelta) -> str:\n"
            "    now = datetime.now(UTC)\n"
            "    payload: dict[str, Any] = {'sub': str(subject), 'type': token_type, 'iat': now, 'exp': now + expires_delta}\n"
            "    settings = get_settings()\n"
            "    return jwt.encode(payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)\n"
            "\n\ndef decode_token(token: str, expected_type: str = 'access') -> dict[str, Any]:\n"
            "    settings = get_settings()\n"
            "    try:\n"
            "        payload = jwt.decode(token, settings.jwt_secret_key.get_secret_value(), algorithms=[settings.jwt_algorithm])\n"
            "    except JWTError as exc:\n"
            "        raise ValueError('Invalid or expired token') from exc\n"
            "    if payload.get('type') != expected_type or not payload.get('sub'):\n"
            "        raise ValueError('Invalid token type')\n"
            "    return payload\n"
            f"{password_function}",
            encoding="utf-8",
        )
        return

    auth_file.write_text(
        '"""Authentication boundary for projects without external auth."""\n\n'
        f"{password_import}\n"
        "\n\ndef create_token(subject, token_type: str, expires_delta) -> str:\n"
        "    return str(subject)\n"
        "\n\ndef decode_token(token: str, expected_type: str = 'access') -> dict[str, str]:\n"
        "    if not token:\n"
        "        raise ValueError('Invalid token')\n"
        "    return {'sub': token, 'type': expected_type}\n"
        f"{password_function}",
        encoding="utf-8",
    )


def configure_auth_imports(project_path, auth):
    """Point generated consumers at the selected authentication boundary."""
    if auth == "jwt":
        return
    for relative_path in ["app/api/deps/auth.py", "app/services/auth_service.py"]:
        path = project_path / relative_path
        content = path.read_text(encoding="utf-8")
        content = content.replace("from app.core.security.jwt import", "from app.core.security.auth import")
        path.write_text(content, encoding="utf-8")


@click.group()
def cli():
    """Hinbert FastAPI CLI."""


@cli.command()
@click.argument("project_name", required=False)
@click.option(
    "--db",
    type=click.Choice(
        ["postgresql", "mysql", "sqlite"],
        case_sensitive=False,
    ),
    help="Database type.",
)
@click.option(
    "--auth",
    type=click.Choice(
        ["jwt", "oauth2", "none"],
        case_sensitive=False,
    ),
    help="Authentication type.",
)
@click.option(
    "--no-2fa",
    is_flag=True,
    help="Skip two-factor authentication.",
)
@click.option(
    "--no-email",
    is_flag=True,
    help="Skip email verification.",
)
@click.option(
    "--no-rate-limit",
    is_flag=True,
    help="Skip rate limiting.",
)
@click.option(
    "--no-docker",
    is_flag=True,
    help="Skip Docker configuration.",
)
@click.option(
    "--k8s",
    is_flag=True,
    help="Include Kubernetes/Helm configuration.",
)
@click.option(
    "--logging",
    "logging_library",
    type=click.Choice(
        ["loguru", "structlog", "none"],
        case_sensitive=False,
    ),
    help="Logging library.",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt.",
)
def init(
    project_name,
    db,
    auth,
    no_2fa,
    no_email,
    no_rate_limit,
    no_docker,
    k8s,
    logging_library,
    yes,
):
    """
    Initialize a new professional FastAPI project.

    \b
    Examples:
        hinbert init my_app              # Interactive mode
        hinbert init my_app --yes        # Non-interactive (defaults)
        hinbert init . --db sqlite       # Generate in current directory
        hinbert init my_api --auth none --no-2fa --no-docker
    """

    click.echo(LOGO)
    click.echo("\n🚀 Welcome to Hinbert FastAPI Generator!\n")

    # ============================================================
    # PROJECT PATH
    # ============================================================

    if not project_name:
        project_name = "my_project" if yes else click.prompt(
            "📁 Project name",
            default="my_project",
        )

    if project_name == ".":
        project_path = Path.cwd()
        display_name = "current directory"
        database_name = project_path.name
    else:
        project_path = Path.cwd() / project_name
        display_name = project_name
        database_name = project_name

        if project_path.exists():
            raise click.ClickException(f"Folder '{project_name}' already exists!")

    # ============================================================
    # DATABASE
    # ============================================================

    if yes and not db:
        db = "postgresql"
    elif not db:
        db = click.prompt(
            "🗄️  Database",
            type=click.Choice(
                ["postgresql", "mysql", "sqlite"],
                case_sensitive=False,
            ),
            default="postgresql",
        )

    db = db.lower()
    database = DATABASES[db]

    # ============================================================
    # AUTHENTICATION
    # ============================================================

    if yes and not auth:
        auth = "jwt"
    elif not auth:
        auth = click.prompt(
            "🔐 Authentication",
            type=click.Choice(
                ["jwt", "oauth2", "none"],
                case_sensitive=False,
            ),
            default="jwt",
        )

    auth = auth.lower()

    # ============================================================
    # TWO FACTOR AUTHENTICATION
    # ============================================================

    if yes:
        two_factor = not no_2fa
    elif not no_2fa:
        two_factor = click.confirm(
            "🔑 Include 2FA (TOTP)?",
            default=True,
        )
    else:
        two_factor = False

    # ============================================================
    # EMAIL VERIFICATION
    # ============================================================

    if yes:
        email_verification = not no_email
    elif not no_email:
        email_verification = click.confirm(
            "📧 Include Email Verification?",
            default=True,
        )
    else:
        email_verification = False

    # ============================================================
    # RATE LIMITING
    # ============================================================

    if yes:
        rate_limiting = not no_rate_limit
    elif not no_rate_limit:
        rate_limiting = click.confirm(
            "🚦 Include Rate Limiting?",
            default=True,
        )
    else:
        rate_limiting = False

    # ============================================================
    # DOCKER
    # ============================================================

    if yes:
        docker = not no_docker
    elif not no_docker:
        docker = click.confirm(
            "🐳 Include Docker?",
            default=True,
        )
    else:
        docker = False

    # ============================================================
    # KUBERNETES
    # ============================================================

    if yes:
        kubernetes = bool(k8s and docker)
    elif k8s:
        kubernetes = True
    else:
        kubernetes = click.confirm(
            "☸️  Include Kubernetes/Helm?",
            default=False,
        )

    # ============================================================
    # LOGGING
    # ============================================================

    if yes and not logging_library:
        logging_library = "loguru"
    elif not logging_library:
        logging_library = click.prompt(
            "📊 Logging Library",
            type=click.Choice(
                ["loguru", "structlog", "none"],
                case_sensitive=False,
            ),
            default="loguru",
        )

    logging_library = logging_library.lower()

    # ============================================================
    # CONFIGURATION SUMMARY
    # ============================================================

    click.echo("\n" + "=" * 60)
    click.echo("📋 Project Configuration Summary")
    click.echo("=" * 60)

    click.echo(f"  📁 Project Name    : {display_name}")
    click.echo(f"  🗄️  Database       : {db}")
    click.echo(f"  🔐 Authentication  : {auth}")
    click.echo(
        f"  🔑 2FA             : "
        f"{'✅ Yes' if two_factor else '❌ No'}"
    )
    click.echo(
        f"  📧 Email Verify    : "
        f"{'✅ Yes' if email_verification else '❌ No'}"
    )
    click.echo(
        f"  🚦 Rate Limiting   : "
        f"{'✅ Yes' if rate_limiting else '❌ No'}"
    )
    click.echo(
        f"  🐳 Docker          : "
        f"{'✅ Yes' if docker else '❌ No'}"
    )
    click.echo(
        f"  ☸️  Kubernetes      : "
        f"{'✅ Yes' if kubernetes else '❌ No'}"
    )
    click.echo(f"  📊 Logging         : {logging_library}")

    click.echo("=" * 60)

    # ============================================================
    # CONFIRMATION
    # ============================================================
    if not yes and not click.confirm(
        "\n✅ Proceed with these settings?",
        default=True,
    ):
        click.echo("❌ Cancelled.")
        return

    # ============================================================
    # TEMPLATE PATHS
    # ============================================================

    click.echo(
        f"\n📦 Generating project: {display_name}..."
    )

    package_root = Path(__file__).resolve().parent.parent

    app_template = package_root / "app"

    if not app_template.exists():
        raise click.ClickException(f"Template folder not found: {app_template}")

    # ============================================================
    # GENERATION
    # ============================================================

    existing_snapshot = snapshot_tree(project_path) if project_name == "." else None

    try:

        # --------------------------------------------------------
        # APP
        # --------------------------------------------------------

        project_path.mkdir(parents=True, exist_ok=True)
        shutil.copytree(app_template, project_path / "app", dirs_exist_ok=True)

        # --------------------------------------------------------
        # SCRIPTS
        # --------------------------------------------------------

        scripts_template = package_root / "scripts"

        if scripts_template.exists():
            shutil.copytree(scripts_template, project_path / "scripts", dirs_exist_ok=True)

        # --------------------------------------------------------
        # DOCKER / KUBERNETES
        # --------------------------------------------------------

        docker_template = package_root / "docker"

        docker_path = project_path / "docker"

        if docker and docker_template.exists():
            shutil.copytree(
                docker_template,
                docker_path,
                dirs_exist_ok=True,
            )

            kubernetes_template = docker_template / "kubernetes"
            kubernetes_path = docker_path / "kubernetes"
            if kubernetes and kubernetes_template.exists():
                shutil.copytree(
                    kubernetes_template,
                    kubernetes_path,
                    dirs_exist_ok=True,
                )
            elif kubernetes_path.exists():
                shutil.rmtree(kubernetes_path)
        elif docker_path.exists():
            shutil.rmtree(docker_path)

        # --------------------------------------------------------
        # ALEMBIC
        # --------------------------------------------------------

        migrations_src = (
            app_template
            / "db"
            / "migrations"
        )

        if migrations_src.exists():
            shutil.copytree(
                migrations_src,
                project_path / "alembic",
            )
        else:
            (
                project_path
                / "alembic"
                / "versions"
            ).mkdir(
                parents=True,
                exist_ok=True,
            )

        # --------------------------------------------------------
        # TESTS
        # --------------------------------------------------------

        (
            project_path / "tests"
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------------
        # ENVIRONMENT FILE
        # --------------------------------------------------------

        env_file = project_path / ".env.example"

        env_file.write_text(
            f"""# ============================================================
# Database
# ============================================================

DATABASE_URL={database['url'].format(name=database_name)}


# ============================================================
# JWT
# ============================================================

SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7


# ============================================================
# OAuth
# ============================================================

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret


# ============================================================
# CORS
# ============================================================

BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
""",
            encoding="utf-8",
        )

        if email_verification:
            with env_file.open("a", encoding="utf-8") as stream:
                stream.write(
                    "\n# ============================================================\n"
                    "# Email (SMTP)\n"
                    "# ============================================================\n\n"
                    "SMTP_HOST=smtp.gmail.com\n"
                    "SMTP_PORT=587\n"
                    "SMTP_USER=your-email@gmail.com\n"
                    "SMTP_PASSWORD=your-password\n"
                )

        # --------------------------------------------------------
        # REQUIREMENTS
        # --------------------------------------------------------

        req_lines = [
            "fastapi>=0.115,<1.0",
            "uvicorn[standard]>=0.24,<1.0",
            "sqlalchemy>=2.0,<3.0",
            "alembic>=1.12,<2.0",
            "pydantic>=2.5,<3.0",
            "pydantic-settings>=2.1,<3.0",
            "python-multipart>=0.0.6,<1.0",
            "python-dotenv>=1.0,<2.0",
            "httpx>=0.25,<1.0",
            "redis>=5.0,<6.0",
            "passlib[bcrypt]>=1.7,<2.0",
            "bcrypt>=4.0,<5.0",
            "email-validator>=2.1,<3.0",
            database["driver"],
        ]

        if auth == "jwt":
            req_lines.extend(
                [
                    "python-jose[cryptography]>=3.3,<4.0",
                ]
            )
        elif auth == "oauth2":
            req_lines.append(
                "python-jose[cryptography]>=3.3,<4.0"
            )

        # ✅ 2FA is INDEPENDENT of auth - add if enabled
        if two_factor:
            req_lines.append(
                "pyotp>=2.9,<3.0"
            )

        if rate_limiting:
            req_lines.append(
                "slowapi>=0.1.9,<1.0"
            )

        if logging_library == "loguru":
            req_lines.append(
                "loguru>=0.7,<1.0"
            )
        elif logging_library == "structlog":
            req_lines.append(
                "structlog>=24.0,<25.0"
            )

        req_lines = list(dict.fromkeys(req_lines))

        req_file = (
            project_path / "requirements.txt"
        )

        req_file.write_text(
            "\n".join(req_lines),
            encoding="utf-8",
        )

        # --------------------------------------------------------
        # ALEMBIC CONFIG
        # --------------------------------------------------------

        alembic_file = (
            project_path / "alembic.ini"
        )

        alembic_file.write_text(
            f"""[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

sqlalchemy.url = {database['alembic_url'].format(name=database_name)}

[post_write_hooks]
hooks = black

black.type = console_scripts
black.entrypoint = black
""",
            encoding="utf-8",
        )

        # --------------------------------------------------------
        # TRACK REMOVED MODULES FOR IMPORT CLEANUP
        # --------------------------------------------------------
        removed_modules = []

        # --------------------------------------------------------
        # ✅ FIX: AUTHENTICATION CLEANUP (Keep totp.py for 2FA)
        # --------------------------------------------------------

        if auth == "oauth2":
            remove_paths(project_path, ["app/core/security/jwt.py"])
            removed_modules.append("core/security/jwt")
            write_auth_files(project_path, auth)
            configure_auth_imports(project_path, auth)
        elif auth == "none":
            # ✅ Only delete JWT/OAuth/Password, keep TOTP if 2FA enabled
            security_dir = project_path / "app" / "core" / "security"
            if security_dir.exists():
                # Delete only auth-specific files
                for file in ["jwt.py", "oauth.py", "password.py"]:
                    (security_dir / file).unlink(missing_ok=True)
                # Keep auth.py (basic auth) and totp.py (if 2FA)
                # If only __init__.py remains, keep it
            removed_modules.append("core/security")
            write_auth_files(project_path, auth)
            configure_auth_imports(project_path, auth)
        else:
            write_auth_files(project_path, auth)

        # --------------------------------------------------------
        # ✅ FIX: 2FA CLEANUP (Only if 2FA is disabled)
        # --------------------------------------------------------
        if not two_factor:
            remove_paths(project_path, ["app/core/security/totp.py", "app/services/totp_service.py"])
            removed_modules.extend(["core/security/totp", "services/totp_service"])
            auth_endpoint = project_path / "app/api/v1/endpoints/auth.py"
            remove_functions(auth_endpoint, {"setup_totp", "verify_totp"})
            remove_imports_from_file(auth_endpoint, [
                "models/domain/totp_secret",
                "models/schemas/totp",
            ])
        # ✅ If 2FA is enabled, keep totp.py - no action needed!

        # --------------------------------------------------------
        # EMAIL VERIFICATION CLEANUP
        # --------------------------------------------------------

        if not email_verification:
            remove_paths(
                project_path,
                [
                    "app/models/domain/email_verification.py",
                    "app/models/domain/password_reset.py",
                    "app/repositories/email_verification_repository.py",
                    "app/repositories/password_reset_repository.py",
                    "app/services/email_service.py",
                ],
            )
            removed_modules.extend([
                "models/domain/email_verification",
                "models/domain/password_reset",
                "repositories/email_verification_repository",
                "repositories/password_reset_repository",
                "services/email_service",
            ])
            remove_class_attributes(
                project_path / "app/models/domain/user.py",
                "User",
                {"email_verifications", "password_resets"},
            )
            remove_functions(
                project_path / "app/api/v1/endpoints/auth.py",
                {"verify_email", "forgot_password", "reset_password"},
            )

        # --------------------------------------------------------
        # RATE LIMITING CLEANUP
        # --------------------------------------------------------

        if not rate_limiting:
            remove_paths(project_path, ["app/core/middleware/rate_limit.py"])
            removed_modules.append("core/middleware/rate_limit")

        # --------------------------------------------------------
        # LOGGING CLEANUP
        # --------------------------------------------------------

        if logging_library == "none":
            remove_paths(project_path, ["app/utils/logger.py"])
            removed_modules.append("utils/logger")
        elif logging_library == "structlog":
            write_structlog_logger(project_path / "app" / "utils" / "logger.py")

        # --------------------------------------------------------
        # CLEANUP IMPORTS
        # --------------------------------------------------------
        if removed_modules:
            cleanup_imports(project_path, removed_modules)

        # --------------------------------------------------------
        # REMOVE __PYCACHE__
        # --------------------------------------------------------
        remove_pycache(project_path)

        # --------------------------------------------------------
        # REMOVE EMPTY DIRECTORIES
        # --------------------------------------------------------
        remove_empty_dirs(project_path / "app")

        # --------------------------------------------------------
        # INIT FILES
        # --------------------------------------------------------

        for root, dirs, files in os.walk(
            project_path
        ):
            root_path = Path(root)

            init_path = (
                root_path / "__init__.py"
            )

            if not init_path.exists():
                init_path.touch()

        # ========================================================
        # SUCCESS
        # ========================================================

        click.echo(
            f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🎉 Project "{display_name}" is ready!                    ║
║                                                              ║
║    Next steps:                                               ║
║                                                              ║
║    cd {project_name if project_name != "." else "."}         ║
║    python -m venv .venv                                      ║
║    .venv\\Scripts\\activate                                   ║
║    pip install -r requirements.txt                           ║
║    cp .env.example .env                                      ║
║    alembic upgrade head                                      ║
║    uvicorn app.main:app --reload                             ║
║                                                              ║
║    📖 Swagger: http://localhost:8000/docs                    ║
╚══════════════════════════════════════════════════════════════╝
"""
        )

    except Exception as exc:

        click.echo(
            f"❌ Error while generating project: {exc}"
        )

        if project_name != ".":
            shutil.rmtree(
                project_path,
                ignore_errors=True,
            )
        elif existing_snapshot is not None:
            restore_tree(project_path, existing_snapshot)

        raise click.ClickException(
            "Project generation failed."
        ) from exc


if __name__ == "__main__":
    cli()