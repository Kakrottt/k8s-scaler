# generalscaler/main.py
import kopf
from . import controller


def main():
    kopf.run(standalone=True)


if __name__ == "__main__":
    main()
