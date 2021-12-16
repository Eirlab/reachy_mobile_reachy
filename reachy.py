from reachy_sdk import ReachySDK

def main():
    reachy = ReachySDK(host='localhost')
    reachy.turn_on('head')


if __name__ == '__main__':
    main()