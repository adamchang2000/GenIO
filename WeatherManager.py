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
import spacy

def clamp(value, minimum=0.0, maximum=100.0):
    return max(minimum, min(value, maximum))


class Sun(object):
    def __init__(self, azimuth, altitude):
        self.azimuth = azimuth
        self.altitude = altitude
        self._t = 0.0

    def tick(self, delta_seconds):
        self._t += 0.008 * delta_seconds
        self._t %= 2.0 * math.pi
        self.azimuth += 0.25 * delta_seconds
        self.azimuth %= 360.0
        self.altitude = (70 * math.sin(self._t)) - 20

    def set_day(self):
        self._t = np.random.uniform(np.pi / 4, np.pi / 2)
    def set_night(self):
        self._t = np.random.uniform(np.pi, 2 * np.pi)
    def set_dawn(self):
        self._t = np.random.uniform(np.pi / 12, np.pi / 10)
    def set_dusk(self):
        self._t = np.random.uniform(np.pi * 9 / 10, np.pi * 11 / 12)

    

    def __str__(self):
        return 'Sun(alt: %.2f, azm: %.2f)' % (self.altitude, self.azimuth)


class WeatherConditions(object):
    def __init__(self, precipitation):
        self._t = precipitation if precipitation > 0.0 else -50.0
        self._increasing = True
        self.clouds = 0.0
        self.rain = 0.0
        self.wetness = 0.0
        self.puddles = 0.0
        self.wind = 0.0
        self.fog = 0.0

    def tick(self, delta_seconds):
        delta = (1.3 if self._increasing else -1.3) * delta_seconds
        self._t = clamp(delta + self._t, -250.0, 100.0)
        self.clouds = clamp(self._t + 40.0, 0.0, 90.0)
        self.rain = clamp(self._t, 0.0, 80.0)
        delay = -10.0 if self._increasing else 90.0
        self.puddles = clamp(self._t + delay, 0.0, 85.0)
        self.wetness = clamp(self._t * 5, 0.0, 100.0)
        self.wind = 5.0 if self.clouds <= 20 else 90 if self.clouds >= 70 else 40
        self.fog = clamp(self._t - 10, 0.0, 30.0)
        if self._t == -250.0:
            self._increasing = True
        if self._t == 100.0:
            self._increasing = False
    
    def set_sunny(self):
        self._t = -40
    def set_cloudy(self):
        self._t = -25
    def set_windy(self):
        self._t = -5
    def set_rainy(self):
        self._t = 30

    def __str__(self):
        return 'Storm(clouds=%d%%, rain=%d%%, wind=%d%%)' % (self.clouds, self.rain, self.wind)


class Weather(object):
    def __init__(self, weather):
        self.weather = weather
        self._sun = Sun(weather.sun_azimuth_angle, weather.sun_altitude_angle)
        self._weatherconditions = WeatherConditions(weather.precipitation)

    def tick(self, delta_seconds):
        self._sun.tick(delta_seconds)
        self._weatherconditions.tick(delta_seconds)
        self.weather.cloudiness = self._weatherconditions.clouds
        self.weather.precipitation = self._weatherconditions.rain
        self.weather.precipitation_deposits = self._weatherconditions.puddles
        self.weather.wind_intensity = self._weatherconditions.wind
        self.weather.fog_density = self._weatherconditions.fog
        self.weather.wetness = self._weatherconditions.wetness
        self.weather.sun_azimuth_angle = self._sun.azimuth
        self.weather.sun_altitude_angle = self._sun.altitude

    def generate_weathertype(self, weather_type):
        """
        Generate weather type
        weather_type=0, sunny
        weather_type=1, cloudy
        weather_type=2, windy
        weather_type=3, rainy
        """

        print('setting weather type', weather_type)

        if weather_type == 0:
            self._weatherconditions.set_sunny()
        elif weather_type == 1:
            self._weatherconditions.set_cloudy()
        elif weather_type == 2:
            self._weatherconditions.set_windy()
        elif weather_type == 3:
            self._weatherconditions.set_rainy()

    def generate_tod(self, tod):
        """
        tod=0, day
        tod=1, night
        tod=2, dawn
        tod=3, dusk
        """

        print('setting tod', tod)

        if tod == 0:
            self._sun.set_day()
        elif tod == 1:
            self._sun.set_night()
        elif tod == 2:
            self._sun.set_dawn()
        elif tod == 3:
            self._sun.set_dusk()

    def __str__(self):
        return '%s %s' % (self._sun, self._weatherconditions)

class WeatherManager():
    def __init__(self, world, update_freq=0.1, speed=1.0):
        """
        world is object of type carla.world
        """
        self.world = world
        self.weather_parameters = self.world.get_weather()
        self.weather = Weather(self.weather_parameters)
        self.update_freq = update_freq
        self.speed = speed
        self.elapsed_time = 0.0
        self.nlp = spacy.load('en_core_web_lg')
    
    def tick(self, carla_tick):

        timestamp = carla_tick.timestamp
        self.elapsed_time += timestamp.delta_seconds
        if self.elapsed_time > self.update_freq:
            self.weather.tick(self.speed * self.elapsed_time)
            self.elapsed_time = 0.0
            self.world.set_weather(self.weather.weather)

    def generate_weather_with_tokens(self, keywords):

        print('weather keywords', keywords)

        weather_token_hardcodes = "sun cloud wind rain day night dawn dusk"
        tokens = self.nlp(' '.join([k.text for k in keywords]) + ' ' + weather_token_hardcodes)

        #hacky time of day analysis (which one has the higher similarity sum)
        tod = [0, 0, 0, 0]

        for token in tokens[:-8]:
            for x in range(4):
                tod[x] += token.similarity(tokens[-4 + x])

        #hacky weather analysis 
        wt = [0, 0, 0, 0]
        for token in tokens[:-8]:
            for x in range(4):
                print(token.text, tokens[-8 + x].text, token.similarity(tokens[-8 + x]))
                wt[x] += token.similarity(tokens[-8 + x])

        self.weather.generate_tod(np.argmax(tod))
        self.weather.generate_weathertype(np.argmax(wt))


    