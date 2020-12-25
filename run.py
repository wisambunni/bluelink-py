from bluelink import BlueLink
import json
import sys


def main():
    if len(sys.argv) < 2:
        print('ERR: Must provide remote action')
        exit()

    credentials = json.loads(open('config.json').read())
    blue_link = BlueLink(credentials)
    identity = blue_link.login()

    action = sys.argv[1]
    if action == 'lock':
        blue_link.lock()
    elif action == 'unlock':
        blue_link.unlock()


if __name__ == "__main__":
    main()