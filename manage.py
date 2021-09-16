#!/usr/bin/env python3
import argparse
import os

from loguru import logger

import adeptum.config as cnf
from adeptum import create_app

logger.add(
    os.path.join(os.path.dirname(cnf.basedir), "logs", "adeptum.log"),
    level="DEBUG" if cnf.DEBUG else "ERROR",
    retention="3 days",
)

app = create_app()


def local_server():
    parser = argparse.ArgumentParser(description="Parse args in script")
    parser.add_argument(
        "-db",
        dest="db",
        default="up",
        help="Options [up, down]",
    )
    args = parser.parse_args()

    if args.db and args.db in ("up", "down"):
        os.system(
            "docker-compose -f docker-compose.yml %s %s"
            % (args.db, "-d" if args.db == "up" else "")
        )

    # cli.load_dotenv()
    # os.system("flask db upgrade")  # upgrade database
    os.system("flask run -p 5555 --reload")


def local_db_down():
    os.system("docker-compose -f docker-compose.yml down")


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
