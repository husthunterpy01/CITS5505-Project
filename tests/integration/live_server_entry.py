from __future__ import annotations
import sys

from app import app
from app.seed import seed_database


def main() -> None:
    port = int(sys.argv[1])
    with app.app_context():
        seed_database(force_reset=True)

    app.run(host="127.0.0.1", port=port, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
