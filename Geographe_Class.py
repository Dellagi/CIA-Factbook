# --> coding: utf-8 -*-

import json, pyfiglet, os
from PyInquirer import style_from_dict, Token, prompt, Separator
from PyInquirer import Validator, ValidationError
from dbhandler import db_handler
from validators import *
from datetime import datetime
import hashlib, sys, re, math
from prettytable import PrettyTable
import numpy as np
import matplotlib.pyplot as plt

from MainClass import AdminClass


class Geo_class(AdminClass):
	def __init__(self):
		super().__init__()


if __name__ == "__main__":
	while True:
		try:
			obj_ = Geo_class()
			obj_.generate_menu(2, 1)
		except:
			obj_.generate_menu(3, 1)
