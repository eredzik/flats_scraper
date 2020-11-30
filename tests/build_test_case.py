import requests
import sys


def build_test_case(http_path, path):
    response = requests.get(http_path)
    with open(path, mode='wb') as f:
        f.write(response.content)


if __name__ == "__main__":
    build_test_case(sys.argv[1], sys.argv[2])
