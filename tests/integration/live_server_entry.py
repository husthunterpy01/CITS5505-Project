
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    os.chdir(root)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    port = int(sys.argv[1])
    db_path = Path(sys.argv[2]).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"

    from app import app
    from app.seed import seed_database

    with app.app_context():
        seed_database(force_reset=True)

    app.run(host="127.0.0.1", port=port, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
