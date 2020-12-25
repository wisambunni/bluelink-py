from bluelink import BlueLink

def main():
    blue_link = BlueLink()
    identity = blue_link.login()
    blue_link.lock()

if __name__ == "__main__":
    main()