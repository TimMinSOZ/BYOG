# gbXXtestfile

import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import matplotlib.colors as mcolors
import matplotlib.font_manager as font_manager
from matplotlib.widgets import Button
from datetime import datetime
import copy
import dill as dill
import PySimpleGUI as sg
from gbUtilsV2 import*

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()
con_obj.autocommit = True

