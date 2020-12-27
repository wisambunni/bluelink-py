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
    elif action == 'start-winter':
        blue_link.start('winter')
    elif action == 'start-winter2':
        blue_link.start('winter2')
    elif action == 'start-summer':
        blue_link.start('summer')
    elif action == 'stop':
        blue_link.stop()
    elif action == 'find':
        blue_link.find()


if __name__ == "__main__":
    main()