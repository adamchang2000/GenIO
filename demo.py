import argparse
import glob
import logging
import math
import os
import random
import re
import sys
import weakref

# try:
#     import pygame
#     from pygame.locals import KMOD_CTRL
#     from pygame.locals import K_ESCAPE
#     from pygame.locals import K_q
# except ImportError:
#     raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError(
        'cannot import numpy, make sure numpy package is installed')

# ==============================================================================
# -- Find CARLA module ---------------------------------------------------------
# ==============================================================================
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# ==============================================================================
# -- Add PythonAPI for release mode --------------------------------------------
# ==============================================================================
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/carla')
except IndexError:
    pass

import carla
from carla import ColorConverter as cc

from WorldManager import World
from ScenarioGeneration import ScenarioGenerator

def sim_loop(args):
    world = None
    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(4.0)
        world = World(client.get_world(), args)
        scene_gen = ScenarioGenerator(world, args.query)

        #main loop
        while True:
            world.wait_for_tick(10)
            world.tick()

    finally:
        if world is not None:
            world.destroy()
        pass

# ==============================================================================
# -- main() --------------------------------------------------------------
# ==============================================================================


def main():
    """Main method"""

    argparser = argparse.ArgumentParser(
        description='Query to scene demo')

    argparser.add_argument('query', metavar='str', nargs='+',
                    help='query string')
    
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='Print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-s', '--seed',
        help='Set seed for repeating executions (default: None)',
        default=None,
        type=int)

    args = argparser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    sim_loop(args)


if __name__ == '__main__':
    main()