# generalscaler/main.py
import kopf
import logging
from . import controller


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    # logging.basicConfig(level=logging.INFO)
    # kopf.run(standalone=True)


if __name__ == "__main__":
    main()
