import sys

from maintenance_metadata import load_maintenance_metadata


def main():
    try:
        load_maintenance_metadata()
    except Exception as error:
        print(f"maintenance metadata invalid: {error}", file=sys.stderr)
        raise SystemExit(1)

    print("maintenance metadata valid")


if __name__ == "__main__":
    main()
