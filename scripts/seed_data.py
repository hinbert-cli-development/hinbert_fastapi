"""Idempotent demo-data entry point for non-production environments."""


def main() -> None:
    """Provide the seed command hook; never run demo seeding in production."""
    raise NotImplementedError("Add environment-gated seed records for your product")


if __name__ == "__main__":
    main()
