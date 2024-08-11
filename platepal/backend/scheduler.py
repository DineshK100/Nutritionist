from pulp import *
from pymongo import MongoClient

MY_PROBLEM = LpProblem("platepal", LpMaximize)
