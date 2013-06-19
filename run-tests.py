# TODO: I need to fix up the package structure so that this can be run from the base directory
import sys, os
#sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.getcwd())
import unittest
from testsuite import *
unittest.main()
