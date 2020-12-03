import glob
import sys
import os

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import time
import argparse

working_directory = os.getcwd()


def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '-i', '--inspect',
        action='store_true',
        help='inspect replay log')

    argparser.add_argument('log_file', nargs=1, help='LOG FILE!')

    args = argparser.parse_args()

    try:
        client = carla.Client('127.0.0.1', 2000)

        log_file = os.path.join(working_directory, args.log_file[0])

        if (args.inspect):
            print(client.show_recorder_file_info(log_file, False))
        else:
            print(client.replay_file(log_file, 0, 0, 0))

            fix_tickrate(client)

            print('playing sim!')

            while True:
                client.get_world().wait_for_tick()
    finally:
        client.reload_world()

        client.get_world().wait_for_tick()

        fix_tickrate(client)

        time.sleep(0.5)


def fix_tickrate(client):
    world = client.get_world()

    settings = world.get_settings()

    settings.fixed_delta_seconds = 0.033

    world.apply_settings(settings)

    world.wait_for_tick()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
