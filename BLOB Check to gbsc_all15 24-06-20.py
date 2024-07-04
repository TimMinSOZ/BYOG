#GB BYOG Ver 2 29-04-23

'This is the loader program for BYOG program. Variables for two profiles "FYD" and "125" are loaded and often can be duplicates of each other but diff profile.'

'"FYD" holds the actual NEM grid SCADA information from Jan 2020 which is 3 imports (SCADA, Solar Rooftop, Interconnectors) '

import numpy as np
import copy
import dill as dill

# From working example - what triggers choice of ToolBar ?
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
import PySimpleGUI as sg
import pyautogui as pag

from gbGFuncsV2 import*
from gbGRunV2 import*
from gbBaseV2 import*
from gbGSelectV2 import*
from gbUtilsV2 import*

plt.rcParams['toolbar'] = 'toolmanager'


#print("Matplotlib plt backend: {}".format(plt.get_backend()))

# Recommended Librarires
# AEMO Data > Data Model Archive > {Select Month} > Select Report 'Public DVD Dispatch_Interconnectors' 'Trading Interconnect'
# Socratica - Tutorials - direct mechanical style but good examples and quality teaching.
# polars - a very fast data handler like pandas
# icecream - prints better debugging
# tqdm - Good for showing a progress meter
# Xarray - Handles multi dimensional data
# Seaborne - Adds more graph styles to matplotlib
# Parquet for fast data read / write pip install pyarrow or pip install fastparquet
# pip install black - Auto formatter for Pep 8 formatting (Tech with Tim)
# Memoiz - For speeding up recursive loops using a cache / cudf.pandas for Pandas is another huge speed boost
# David Osmand - CNB Wind Engineer plus ISP program at UNI and Beyond Zero Emissions
# CS Classroom - Good PySimpleGUI videos add graph to form and edit a table
# Numba Compilation for speeding up for loops with NumPy / PyPy a faster compiler for freq used code (Maybe 5 - 15x Faster) 
# / MyPyc uses Types to enable speeding up. Very easy to use as NO code change expected
# / Cython is another compiler which benefits from annotating variables
# optoma-uhd55-dlp-4k-ultra-hd-smart-home-theatre-projector
# cProfile for speed analysis
# Taipy - Full stack Web Deployment GUI
# imblearn.over_sampler import RandomOverSampler
# arjancode.com/diagnosis - 30 mins on tools for finding errors
# https://www.energydashboard.co.uk/api-info - Provides data for UK - Note 2 levels National Grid and Local Grid receive electricity from generators
# https://aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration - List of Generators and Gen Id's
# Flask is quicker and easier to use than Django for Web Development
# LLM - COPILOT from Github as best Code Assistant -  Codium AI come out as the best Test Generator and Suggests code improvements
# Import RE - Regular Expressions - Used to create match strings to use in searches - search dictionaires better - Used in Find / Replace in VS-Code ????


import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()
con_obj.autocommit = True

screenname = "gbdemgraph"

# Initiate later used variables
rfd = {}
rft = {}
rfc = {}
rfg = {}

genreg = []
genfuel = []
rfgraph = {}
gfcolor = []
colorlist = []
xaxis = []
demlinedata = []
regdemtxns = []
regfueltxns = []


rfc['FYD'+'months_in_year_num'] = [['JAN','01'], ['FEB','02'], ['MAR','03'], ['APR','04'], ['MAY','05'], ['JUN','06'], ['JUL','07'], ['AUG','08'], ['SEP','09'], ['OCT','10'], ['NOV','11'], ['DEC','12']]
rfc['FYD'+'months_in_year'] = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
rfc['FYD'+'years_in_range'] = ['2020','2021','2022','2023']
pfx = rfc["pfxinuse"] = rfc['pfx'] = "FYD"
region = "ALL"
rfc['FYD'+"graph_fuel_order"] = ["NUC","CBR", "CBL","GAS","SUT","SRT","WIN","HVI","IHB","EVB","EVG","HPU","HYD","BAT","GOC","NGT","ZL1","GAP","EXS","DL1"]
rfc['FYD'+'storage_fuel_list'] = ['BAT','IHB', 'EVB', 'EVG', 'HPU']
rfc['FYD'+'F_code_link'] = [('F1', 'BAT'),('F2','HPU'),('F3', 'HYD'),('F4', 'HVI'),('F5','GOC'),('F6','NGT'),('F7','FIX'),('F8', 'IHB'), ('F9', 'EVB')]
rfc["onclick"] = []
rfc["onkey"] =[]
rfc["zoomtrack"] = []
rfc['FYD'+"cols"] =[]
rfc['FYD'+"allfuel"] = []
rfc["zoom"] = "N"
rfc['FYD'+"ALL"+"cols"] = []
rfc['FYD'+'autorun'] = "N"
rfc['FYD'+"elements"] = 35040
rfc['FYD'+"startpos"] = 0
rfc['FYD'+"endpos"] = rfc[pfx+"elements"]
rfc['FYD'+"pfx"] = pfx
rfc['FYD'+"region"] = region
rfc['FYD'+"genreg"] = ["NSW","QLD","SA","TAS","VIC"]
rfc['FYD'+"start_year"] = 2024
rfc['FYD'+'demand_allowed_variance'] = 0.025
### EVB Parameters ####
rft['FYD'+"ALL"+"EVB_cur_sales"] = 98436 # 2023 EV Sales Figures
rft['FYD'+"ALL"+"EVB_avg_battery_kwh"] = 60 # Assumed average KW for a EV sold in Australia
rfc['FYD'+'EVB_allocate_as_battery_pc'] = 0.33 # Assumes 33% of an EV battery is allocated to grid if EV owner allows
#rfc['FYD'+'EVB_house_battery_allocation_pc'] = 0.50
rft['FYD'+'EVB_annual_KWH_demand'] = 2600 # The average KWH's used per annum by a car. Using 1KWH to 5KM's.
rft['FYD'+'chg_day_pc'] = 0.5
### IHB Parameters ###
rfc['FYD'+'ihb_avg_kwh'] = 12 
rfc['FYD'+'annual_ihb_sales'] = 0.057 # In millions SunWiz 2023 Home Battery Sales - Avg size = 11.5KW - Updated 23/04/15
rfc['FYD'+'curr_ihb_installed'] = 0.09 + rfc[pfx+'annual_ihb_sales'] # In millions ALL regions. Accurate as of 1st half 2023
rfc['FYD'+'ihb_cost'] = 12000 # AUD with installation - good price 2024
rfc['FYD'+'ihb_life'] = 10 # Years and we don't depreciate batteries but could easily as we average
rfc['FYD'+'House_Base_KWHs'] = 0.2 # Amount a house is assumed to use over night in KW's per Hour

rft["title_size"] = title_size = 23
rfc['FYD'+region+'leg_names'] = []
rfc["no"] = 1  ##### I bet this is not needed but used in line 172 rf_zoom_esc
rfc["ic_type"] = "I"
rfc['FYD'+region+"max_gap"] = 0
rfc["pie"] = "N"
for region in rfc["FYD"+"genreg"] :
    rfc['FYD'+region+'leg_names'] = []
    rfc['FYD'+region+"cols"] = []
    rfc['FYD'+region+"max_gap"] = 0
    rfd['FYD'+region+'EVB'+'DEM'] = np.full(rfc["FYD"+"elements"], 0).astype('float32')
    rft['FYD'+region+'EVB'+'DEM'] = 0
rfd['FYD'+'ALL'+'EVB'+'DEM'] = np.full(rfc["FYD"+"elements"], 0).astype('float32')
rft['FYD'+'ALL'+'EVB'+'DEM'] = 0

screen_width, screen_height = pag.size()
#plt.rcParams[keymap.help]=['f1']


degrandriver = 480 # This determines graph resolution the higher the number the higher the resolution
degran = (rfc["FYD"+"endpos"]-rfc["FYD"+"startpos"]) // degrandriver
if degran > 1 :
    if degran < 256 :
        while  degran not in [1,6,24,96,480] : # This value matters and determines resolution and data reporting compression
            degran = degran + 1
else :     # Will this else ever actually trigger ???
    if degran <  1:
        degran = 1
rfc['FYD'+"degran"] = degran


cur_obj.execute("select code, genfuel, type, ord, color from gbgenfuel where ord != 'NA' order by ord")
cols = cur_obj.fetchall()
for col in cols :
    fuel = col[0]
    color = str(col[4])
    color=color.lower()
    color = mcolors.CSS4_COLORS[color]
    rfc[pfx+fuel+"col"] = color
    rfc[pfx+fuel+"fuel_name"] = col[1]
    rfc[pfx+fuel+"type"] = col[2]
    rfc[pfx+fuel+"ord"] = col[3]
    
    if fuel not in rfc[pfx+"allfuel"] :
        rfc[pfx+"allfuel"].append(fuel)

def start_scn() :
    
    gui_size = 15
    bs = (15,1) # Button size
    bf = ('Helvetica',gui_size) # Button Font & size
    tf = ('Helvetica',gui_size) # Text font & size
    mf = ('Helvetica',gui_size) # Menu Font and size
    ts = ('Helvetica',30) # Title Size
    
    start_scn_hdr =  [[sg.Text('  Enter Start Year & Month  ', justification='center', size = gui_size, font=ts, expand_x = True, relief=sg.RELIEF_RIDGE, text_color = 'blue', background_color = 'white')]]
    start_scn_body =  [[sg.T()],[sg.T('Start Year', size=(10, 1)), sg.Combo(values = rfc['FYD'+'years_in_range'], default_value = '2023', size=(10, 1), key='-START_YEAR-', enable_events=True)], 
                       [sg.T('Start Month', size=(10, 1)), sg.Combo(values = rfc['FYD'+'months_in_year'], default_value = 'JAN', size=(10, 1), key='-START_MONTH-', enable_events=True)],[sg.T()]]
    start_scn_buttons =[[sg.Push(),sg.B('Exit', size = bs), sg.Push(), sg.B('OK', size=bs), sg.Push()]]

    start_scn_layout = [start_scn_hdr + start_scn_body + start_scn_buttons]  

    start_scn_w = sg.Window(f'Commencing Grid Build - V02.021', start_scn_layout , grab_anywhere=True, resizable=True, margins=(0,0), use_custom_titlebar=True, finalize=True, keep_on_top=True)
    
    return start_scn_w

start_scn_w = start_scn()   

while True :
    
    event, values = start_scn_w.read()
    
    if event in (None, 'Exit', '-EXIT-','esc') :
        print("[LOG] Clicked Exit!")
        start_scn_w.close()
        exit()
    
    if event == 'OK' :
        month =  values['-START_MONTH-']
        month_num = [month[1] for month in rfc['FYD'+'months_in_year_num'] if month[0] == values['-START_MONTH-']][0]
        
        rfc['FYD'+'FYDs_initial_start_date'] = values['-START_YEAR-'] + month_num + '01' + '00' + '00'
        print(rfc['FYD'+'FYDs_initial_start_date'])
        start_scn_w.close()
        break

print("SQL BLOBs start  ", datetime.now())
        
cur_obj.execute("select prefix, region, fuel, code, data from gbact_all15 where prefix = 'FYD' and region = 'NSW' and fuel = 'SUT' and code = ''")
txns = cur_obj.fetchall()
rfd_start = position_from_date_sort(rfc['FYD'+'FYDs_initial_start_date'])
rfd_end = rfd_start + rfc['FYD' + 'elements']
for txn in txns :
    pfx = txn[0]
    region= txn[1]
    fuel = txn[2]
    gcd = txn[3]
    rfd[pfx+region+fuel+gcd+'all_FYD_data'] = dill.loads(txn[4])
    rfd[pfx+region+fuel+gcd] = copy.deepcopy(rfd[pfx+region+fuel+gcd+'all_FYD_data'])
    

cur_obj.execute('select gwh, datesort from gbsc_all15 where genregion = "NSW" and genfuel = "SUT"')
gbsc_data = cur_obj.fetchall()

print(len(gbsc_data))
print(len(rfd[pfx+region+fuel+gcd]))

exit()


rfg['region'] = region
rfg['demline'] = 300
rfg['legsize'] = 10
rfg['legbold'] = 'normal'
rfg["graph_table"] = "N"
rfg["graph_table_size"] = 10
rfg['graph_analysis_table'] = 'Gap'
rfg['graph_analysis_table_size'] = 10
rfg['stg_line_width'] = 2
rfg['stg_line_bold'] = 'normal'
rfg['stg_line_color'] = 'black'

calc_totals(rfd, rft, rfc, rfg, pfx)


pfx = "125"
rfc[pfx+'pfxname'] = 'Start Profile'
rfc["pfxinuse"] = "125"
region = rfc[pfx+"region"] = "ALL"
rfc[pfx+"ALL"+"genfuel"] = ["NUC","CBR", "CBL","SUT","SRT","WIN","IHB"]
rfc[pfx+"genreg"] = rfc["FYD"+"genreg"]
rfc[pfx+"start_date"] = rfc['FYD'+'FYDs_initial_start_date']
rfc[pfx+"startpos"] = rfc["FYD"+"startpos"]
rfc[pfx+"endpos"] = rfc["FYD"+"endpos"]
rfc[pfx+"degran"] = degran
rfc[pfx+"elements"] = rfc["FYD"+"elements"]
#rfc[pfx+"lastreg"] = 1
rfc[pfx+'demline'] = 300
rfc[pfx+region+"max_gap"] = 0
#rfc[pfx+"genreg"] = ["NSW","QLD","SA","TAS","VIC"]
for region in rfc["FYD"+"genreg"] :
    rfc[pfx+region+'leg_names'] = []
    rfc[pfx+region+"cols"] = []
    rfc[pfx+region+"max_gap"] = 0
    rfc[pfx+region+'GOC'+'CAP'] = 0
    rft[pfx+region+"ALL"+"FIX"] = 0
    rfd[pfx+region+'EVB'+'DEM'] = np.full(rfc["FYD"+"elements"], 0).astype('float32')
    rft[pfx+region+'EVB'+'DEM'] = 0
rfd[pfx+'ALL'+'EVB'+'DEM'] = np.full(rfc["FYD"+"elements"], 0).astype('float32')
rft[pfx+'ALL'+'EVB'+'DEM'] = 0
region = rfc[pfx+"region"]
rfc[pfx+"ALL"+"BAT"+"done"] = "N"
rfc[pfx+"ALL"+"HVI"+"done"] = "N"
rfc[pfx+"ALL"+"HPU"+"done"] = "N"
rfc[pfx+"ALL"+"HYD"+"done"] = "N"
rfc[pfx+"ALL"+"IHB"+"done"] = "N"
rfc[pfx+"ALL"+"EVB"+"done"] = "N"
rfc[pfx+"ALL"+"EVG"+"done"] = "N"
rfc[pfx+"ALL"+"GOC"+"done"] = "N"
rfc[pfx+"ALL"+"NGT"+"done"] = "N"
rfc[pfx+"ALL"+"FIX"+"done"] = "N"
rfc[pfx+"ALL"+'leg_names'] = []
rfc[pfx+"ALL"+"cols"] = []
rfc[pfx+'tabletog'] = 'N'
rft[pfx+'chg_day_pc'] = 50
rfc[pfx+'show_battery'] = 'N'
rfc[pfx+'show_battery_legend'] = 'Y' # Not used or planned to be yet

get_fuel_tgt_fix_stg_ic(rfd, rft, rfc, rfg, pfx)

renewable_target_allocation(rfd, rft, rfc, rfg, pfx)

calc_totals(rfd, rft, rfc, rfg, pfx)

pfx="FYD"
colors=[]
rfgout = []
for fuel in rfc[pfx+region+"genfuel"] :
    colors.append(rfc["FYD"+fuel+"col"])
    rfc[pfx+region+'leg_names'].append(rfc["FYD"+fuel+"fuel_name"])
    if rfc["zoom"] == "N" :
        rfgout.append(np.array(rfd[pfx+region+fuel]).reshape(-1,rfc[pfx+"degran"]).mean(axis=1))
    else :
        rfgout.append(np.array(rfd[pfx+region+fuel][int(rfc[pfx+"startpos"]):int(rfc[pfx+"endpos"])]))


rfg["pfx"] = pfx
rfg["region"] = region
rfg["genfuel"] = copy.deepcopy(rfc[pfx+region+"genfuel"])
rfg["degran"] = degran
rfg["startpos"] = rfc[pfx+"startpos"]
rfg["endpos"] = rfc[pfx+"endpos"]
rfg["gencode"] = ""
rfg["rfgout"] = rfgout


xaxis = list(np.arange(0, len(rfgout[0]), 1).astype(int)) # That is how we are going to handle Xaxis - calculate it from the length of first member.

xtickvals, xticklabels = create_xticks(rfd, rft, rfc, rfg, pfx)

fig, ax = plt.subplots(figsize=(23,12))
plt.subplots_adjust(top=0.925, bottom=0.1, left=0.025, right=0.99, hspace=0.2, wspace=0.2)
DPI = fig.get_dpi()
ax.set_title(f'{rfc[pfx+"genreg"]} - {rfc[pfx+"start_date"][:4]} Actual Data - Using AEMO SCADA Data Feed', fontweight ="bold", size=title_size)
ax.set_ylim(0,32)
ax.set_xticks(xtickvals)
ax.set_xticklabels(xticklabels)
ax.stackplot(xaxis, rfgout, colors = colors , alpha=0.9)
ax.grid(False)
ax.margins(0.01)

rfc["ax"] = ax
rfc["fig"] = fig
rfc["plt"] = plt

add_TB_buttons(rfd, rft, rfc, rfg, pfx)

print(' Show Flag - Battery Storage in Graph    ', rfc['125'+'show_battery'])

create_legend(rfd, rft, rfc, rfg, pfx)

reg_fuel_supply_table(rfd, rft, rfc, rfg, pfx)

exs_gap_analyser(rfd, rft, rfc, rfg, pfx)

# cursor = Cursor(ax, useblit=True, color='red', linewidth=2) produces a cross hairs cursor in red and switches off other event functions

rfc['keyoc'] = fig.canvas.mpl_connect('button_press_event', lambda event: on_click(event, rfd, rft, rfc, rfg, pfx))

#rfc['keyop'] = fig.canvas.mpl_connect('pick_event', lambda event: on_pick(event, rfd, rft, rfc, rfg, pfx))

rfc['keyok'] = fig.canvas.mpl_connect('key_press_event', lambda event: on_key(event, rfd, rft, rfc, rfg, pfx ))

#mplcursors.cursor()

plt.show()

