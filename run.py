from bluelink import BlueLink
import argparse
import json


def main():
    credentials = json.loads(open('config.json').read())

    blue_link = BlueLink(credentials=credentials)
    blue_link_actions = {
        'start': blue_link.start,
        'stop': blue_link.stop,
        'lock': blue_link.lock,
        'unlock': blue_link.unlock,
    }

    parser = argparse.ArgumentParser()

    parser.add_argument('--action', type=str, required=True,
                        choices=blue_link_actions.keys())
    parser.add_argument('--temp', type=int, required=False, default=70)
    parser.add_argument('--defrost', type=bool, required=False, default=False)
    args = parser.parse_args()

    blue_link.login()

    if args.action == 'start':
        blue_link_actions[args.action](args.temp, args.defrost)
    else:
        blue_link_actions[args.action]()


if __name__ == '__main__':
    main()
