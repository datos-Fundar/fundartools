import sys
import importlib

try:
    sys.modules[__name__ + '.llms'] = importlib.import_module('fundar_llms')
except ImportError:
    raise ImportError("'fundar_llms' isn't installed. Get it from github.com/datos-Fundar/llms")