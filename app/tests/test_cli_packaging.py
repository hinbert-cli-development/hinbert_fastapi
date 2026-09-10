from pathlib import Path

from click.testing import CliRunner

from hinbert_cli.main import __version__, cli


def test_cli_template_assets_are_included_in_source_distribution():
    project_root = Path(__file__).resolve().parents[2]
    manifest = project_root / "MANIFEST.in"

    assert manifest.exists(), "MANIFEST.in should be present for template assets"
    contents = manifest.read_text(encoding="utf-8")
    assert "recursive-include docker" in contents


def test_cli_module_has_version_and_command_registration():
    assert isinstance(__version__, str)
    assert __version__
    assert cli is not None


def test_cli_requires_force_for_existing_directory():
    runner = CliRunner()
    with runner.isolated_filesystem():
        project_dir = Path("existing-project")
        project_dir.mkdir()
        (project_dir / "placeholder.txt").write_text("keep me", encoding="utf-8")

        result = runner.invoke(
            cli,
            ["init", "existing-project", "--yes", "--db", "sqlite", "--auth", "none", "--no-2fa", "--no-email", "--no-rate-limit", "--no-docker", "--logging", "none"],
        )

        assert result.exit_code != 0
        assert "--force" in result.output.lower()


def test_cli_generates_project_with_selected_options():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["init", "demo-app", "--yes", "--db", "sqlite", "--auth", "none", "--no-2fa", "--no-email", "--no-rate-limit", "--no-docker", "--logging", "none"],
        )

        assert result.exit_code == 0, result.output
        assert (Path("demo-app") / "app").is_dir()
        assert (Path("demo-app") / "requirements.txt").exists()
        assert not (Path("demo-app") / "docker").exists()
