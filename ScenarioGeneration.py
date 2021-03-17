import glob
import logging
import math
import os
import random
import re
import sys
import weakref

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

class ScenarioGenerator():
    def __init__(self, world, query_string):
        """
        world is object of type World
        query string should be a list of words
        """
        self.world = world
        self.query_string = query_string
        self.generate_scenario_from_query(self.query_string)

    def generate_scenario_from_query(self, query_string):
        """destroys current world and generates with new query_string"""
        logging.info("generating scenario with query string: " + " ".join(query_string))
        pass
    
    def regenerate_scenario(self):
        """destroys current world and regenerates with same query_string"""
        self.generate_scenario_from_query(self.query_string)

    def generate_traffic_scenario(self):
        """generates a scenario with traffic on road"""
        

    