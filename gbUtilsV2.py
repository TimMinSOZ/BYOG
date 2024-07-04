# gbUtilsV2

import numpy as np
from datetime import datetime
import numpy as np
import PySimpleGUI as sg
#from matplotlib.widgets import Button, Slider

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()
con_obj.autocommit = True


gui_size = 15
gb = (6,1) # Graph Button
bs = (15,1) # Button size
bf = ('Helvetica',gui_size) # Button Font & size
tf = ('Helvetica',gui_size) # Text font & size
mf = ('Helvetica',gui_size) # Menu Font and size
ts = ('Helvetica',30) # Title Size


def graph_top_buttons(rfd,rft,rfc,rfg,pfx) :
    
    button_layout = [sg.Button('STG', key ='-STG-', size = bs, button_color = 'white', mouseover_colors = ('yellow','white'))]
    
    graph_buttons = sg.window(title = 'Graph Buttons', layout = button_layout, location = (100,1000), finalize = True, keep_on_top = True, grab_anywhere = False)
    
    return graph_buttons




def add_stp_to_rfg_genfuel(rfd,rft,rfc,rfg,pfx, stp) :  #### Need to think about rfc[pfx+region+'genfuel'] - used for fuels per region. Maybe if not in rfd then not there !!!!
    fn = 'Add to Graph Genfuel '
    
    if stp not in rfg["genfuel"] :
        if "ZL1" in rfg["genfuel"] :
            position = rfg["genfuel"].index("ZL1")
            rfg["genfuel"].insert(position, stp)
        else :
            rfg['genfuel'].append(stp)



def evb_demand_shape(rfd,rft,rfc,rfg,pfx) :
    fn = 'EVB Demand Shape  '
    
    ##### This creates a demand shape for the day 8am to 4pm and a demand shape for the night and combines them into a single day starting at 00:15 
    ##### The Shape is the multiplied up for a YEAR and then split between REGIONS on POPPC which holds the percent of population
    ##### If revisited then the shape will be adjusted for the days length which we hold in sunrise to sunset database
    ##### Requires 
    
    rfc['FYD'+'evbdayshape'] = np.array([0.5,1,2,3.4,4.3,5,5.7,6.3,6.9,7.8,8.5,8.9,9,9.1,9.2,9.4,9.4,9.2,9.1,9,8.7,8.3,7.5,6.8,6.3,5.8,5.1,4.1,3.2,2.2,1.7,1]) * 2.5 * rft[pfx+'chg_day_pc'] / 100
    print(fn, len(rfc['FYD'+'evbdayshape']), rfc['FYD'+'evbdayshape'].sum())
    rfc['FYD'+'evbnightshape'] = np.array([1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5] + [8] * 36 + [7.5,7,6.5,6,5.5,5,4.5,4,3.5,3,2.5,2,1.5,1]) * 1.25 * (100-rft[pfx+'chg_day_pc']) / 100
    print(fn, len(rfc['FYD'+'evbnightshape']), rfc['FYD'+'evbnightshape'].sum())

    rfc['FYD'+'evb_demand_shape'] = np.array(list(rfc['FYD'+'evbnightshape'][32:]) + list(rfc['FYD'+'evbdayshape']) + list(rfc['FYD'+'evbnightshape'][:32]))
    print(fn, len(rfc['FYD'+'evb_demand_shape']), rfc['FYD'+'evb_demand_shape'].sum())

    rfc['FYD'+'evb_demand_shape'] = np.array(list(rfc['FYD'+'evb_demand_shape']) * 365) / 45.625 ##### The number to adjust by not derived from elsewhere #####
    print(fn, len(rfc['FYD'+'evb_demand_shape']), rfc['FYD'+'evb_demand_shape'].sum()/4) 
    
    cur_obj.execute('select genregion, qty from gbstg where genfuel = "EVB"')
    reg_evb = cur_obj.fetchall()
    for reg_qty in reg_evb :
        region = reg_qty[0]
        evb_dem_pc = float(reg_qty[1]) * rft['FYD'+'EVB_annual_KWH_demand'] / rft['FYD'+region+'DEM']
        
        print(fn, region, reg_qty[1], rft['FYD'+'EVB_annual_KWH_demand'], 'Dem percent =  ' , evb_dem_pc, 'Act Demand =   ', rft[pfx+region+'DEM'])
        
        rfd[pfx+region+'EVB'+'DEM'] = np.array(rfc['FYD'+'evb_demand_shape'] * round(rft[pfx+region+'DEM'] * evb_dem_pc / 1000, 3)).astype('float32')
        rft[pfx+region+'EVB'+'DEM'] = rfd[pfx+region+'EVB'+'DEM'].sum() / 4
        rfd[pfx+'ALL'+'EVB'+'DEM'] += rfd[pfx+region+'EVB'+'DEM']
        rft[pfx+'ALL'+'EVB'+'DEM'] += rft[pfx+region+'EVB'+'DEM']
        
        print(fn, "**********", region,"    ", (rft[pfx+region+'DEM'] * evb_dem_pc), rfd[pfx+region+'EVB'+'DEM'].sum() , rft[pfx+region+'DEM'], rft[pfx+region+'EVB'+'DEM'] )
                         
    return 


def fuel_from_graph_pos(rfd,rft,rfc,rfg,pfx) :
    
    height = 0
    x_pos = int(float(rfc['onclick'][0][3])) ### + rfg["startpos"]
    y_height = int(rfc['onclick'][0][4])
    print(x_pos, y_height)
    
    for i, fuel in enumerate(rfg["genfuel"]) :
        height = height + rfg["rfgout"][i][x_pos] 
            
        if height > y_height :
            print(x_pos,y_height,height,rfg['genfuel'])
            break 
        
    return fuel
    
def national_fuel_targets(rfd,rft,rfc,rfg,pfx) :
    fn = " Update National Targets for a given Renewable Fuel from State Targets "
    
    rfc[pfx+'ALL'+'ALL'+'TGT'] = 0

    for region in rfc['FYD'+'genreg'] : 
        rfc[pfx+region+'ALL'+'TGT'] = 0
        for fuel in rfc['FYD'+'renfuel'] : 
            rfc[pfx+region+'ALL'+'TGT'] += int(rfc[pfx+region+fuel+'TGT'])


    for fuel in rfc['FYD'+'renfuel'] :
        fuel_gwh_tot = 0
        rfc[pfx+'ALL'+fuel+'TGT'] = 0
        for region in rfc['FYD'+'genreg'] :
            fuelpc = int(rfc[pfx+region+fuel+'TGT']) / 100 ## Coverts to decimal 
            if 'FYD'+region+'ALL' in rfd.keys() :  fuel_gwh_tot += rfd["FYD"+region+"ALL"].sum()/4 * fuelpc
            
            
        rfc[pfx+'ALL'+fuel+'TGT'] = int(fuel_gwh_tot / (rfd["FYD"+"ALL"+"ALL"].sum()/4) * 100)
        if pfx+'ALL'+'ALL'+'TGT' not in rfc : rfc[pfx+'ALL'+'ALL'+'TGT'] = rfc[pfx+'ALL'+fuel+'TGT']
        else : rfc[pfx+'ALL'+'ALL'+'TGT'] += rfc[pfx+'ALL'+fuel+'TGT']
    
    return
        
def is_a_number(number) :
    for num in number :
        if num in '-0123456789.' :
            pass
        else : return False
    return True


def key_split(key) :
    
    gcd = '' 
    pfx =  key[0:3]
    region_first_letter = key[3]  
      
    if region_first_letter == 'S' : 
        region = key[3:5]
        fuel = key[5:8]
        if len(key) > 8 : gcd = key[8:11]
        
    if region_first_letter != 'S' : 
        region = key[3:6]
        fuel = key[6:9]
        if len(key) > 9 : gcd = key[9:12]
    
    return pfx, region, fuel, gcd

def scurve(growth , periods , endamount, startamount = 0) :
    fn = "  S Curve Creater  "
    curvedata = []
    for t in range(periods):
        curvedata.append(int(startamount + ((endamount - startamount) / (1 + np.exp(-growth * (t-periods / 2))))))

    return curvedata

def estimate_renewable_adjustment(rfd, rft, rfc, rfg, pfx, region, svd_file, gwh_out) :
    fn = ' Estimate Renewable Uplift  '
    
    svd_gap = svd_file[svd_file > 0].sum()
    
    svd_file = svd_file[svd_file > 0 ] - gwh_out
    
    svd_fill = svd_gap - svd_file[svd_file > 0 ].sum()
    
    uplift = svd_fill / (rfd[pfx+region+"REN"].sum() - svd_fill)
    
    uplift_file = rfd[pfx+region+"REN"] * uplift
    
    return uplift_file


def is_valid_date(date_str, date_format='%d-%m-%y'):
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False   

def gap_excess_file(rfd,rft,rfc,rfg,pfx, region, svd_file = 'NA') :
    fn =' gap_excess_file  '
    #print(fn, region, "Start Time  ", datetime.now())

    gap_start = gap_end = exs_start  = exs_end = gap_gwh = exs_gwh = 0
    ger_data = [] #### ger stands for gap / excess / region - data 
    if svd_file == 'NA' : svd_file = np.array(rfd[pfx+region+"SVD"])
    
    for i in range(len(svd_file)) :
           
        if i == 0 :
            if svd_file[i] <= 0 : 
                exs_start = i
                gap_start = -1
            if svd_file[i] > 0 : 
                gap_start = i
                exs_start = -1
         
        if svd_file[i] > 0 : ### This is a GAP
            if gap_start == -1 :
                if exs_end == -1 : continue
                if exs_start == i - 1 : continue ### DO NOT RECORD SINGLE 15MIN SWINGS IN GAP's AND EXS's
                exs_end = i
                gap_start = i
                    
                ger_data.append([exs_start, round(exs_gwh/4,2), int(exs_end + 1 - exs_start), exs_end, 'EXS'])
                
                exs_start = -1
                exs_end = exs_gwh = 0
            gap_gwh += svd_file[i]
            
        elif svd_file[i] < 0 : ### This is a EXS
            if exs_start == -1 :
                if gap_end == -1 : continue
                if gap_start == i - 1 : continue ### DO NOT RECORD SINGLE 15MIN SWINGS IN GAP's AND EXS's
                gap_end = i
                exs_start = i
                    
                ger_data.append([gap_start, round(gap_gwh/4,2), int(gap_end + 1 - gap_start), gap_end, 'GAP'])
                
                gap_start = -1
                gap_end = gap_gwh = 0
            exs_gwh += svd_file[i]
            
    
    #print(fn, region, 'No. of ZERO entries in svd_file =  ', len([svd for svd in svd_file if svd == 0]), "Finish Time  ", datetime.now())
    
    return ger_data

def long_gap_file(rfd,rft,rfc,rfg,pfx, region) :
    fn =' long gap file  '
    print(fn, region, "Start Time  ", datetime.now())

    gap_start = gap_end = exs_start  = exs_end = gap_gwh = exs_gwh = 0
    ger_data = [] #### ger stands for gap / excess / region - data 
    svd_file = np.array(rfd[pfx+region+"SVD"])
    rev_run_gwh = 0
        
    for i, gwh in enumerate(reversed(svd_file)) :
                
        if i == 0 :
            if gwh == 0 : continue
            if gwh < 0 : 
                exs_start = i
                gap_start = -1
            if gwh > 0 : 
                gap_start = i
                exs_start = -1
                
        rev_run_gwh += gwh 
        
        if rev_run_gwh < 0 : ### Is cycling through excess not gaps
            if exs_start == -1 :
                gap_start = 35039 - i
                gap_size = round(np.array([gap for gap in svd_file[gap_start : gap_end] if gap > 0]).sum() / 4, 3)
                ger_data.insert(0, [gap_start, gap_size, int(gap_end + 1 - gap_start), gap_end, 'Long_gap'])
                gap_start = -1
                gap_end = rev_run_gwh = exs_start = 0
            rev_run_gwh = 0 

             
        if rev_run_gwh > 0 : ### Is start of a gap
            
            if gap_start == -1 :
                gap_end = 35039 - i
                exs_start = -1
                gap_start = 0
    
    print(fn, region,  "Finish Time  ", datetime.now())
    
    return ger_data

def fuelsort(rfd, rft, rfc, rfg, pfx, fuellist) :
    sortfuel = []
    if rfg['region'] == 'TAS' :
        tas_fuel_list = ['GAS','GOC','HYD','SRT','SUT','WIN','BAT','HVI','IHB','EVB','EVG','HPU','BAT','NGT','ZL1','GAP','EXS','DL1']
        for fuel in tas_fuel_list :
            if fuel in fuellist :
                sortfuel.append(fuel)
    else :       
        for fuel in rfc["FYD"+"graph_fuel_order"] :
            if fuel in fuellist :
                if fuel != "GAS" :
                    sortfuel.append(fuel)
                else :
                    if "GOC" in fuellist :
                        fuellist.remove("GOC")
                        sortfuel.append("GAS")
                        sortfuel.append("GOC")
                    else :
                        sortfuel.append(fuel)
    return sortfuel



def date_obj_from_position(startpos, ipstart_date = "202001010015") :
    fn = "  Date From Position  "
    "Currently we use the default start date as 01-02-2022 but this allows change later"
    # can have this format where it returns those values %d%b%Y%H%M%S %d = day %b = day %Y = year %H = hour %M = minute %S = seconds
    from datetime import datetime, timedelta
    sql_date_format = '%Y%m%d%H%M'
    start_pos_sec = int(startpos * (15*60))
    ipstart_date = datetime.strptime(ipstart_date, sql_date_format)
    new_ipstart_date =  ipstart_date + timedelta(seconds=start_pos_sec) # , microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        
    return new_ipstart_date

def position_from_date_sort(date_sort, ipstart_date = "202001010015") :
    fn = "  Position From Date  "
    from datetime import datetime, timedelta
    sql_date_format = '%Y%m%d%H%M'
    init_date = datetime.strptime(ipstart_date, sql_date_format)
    calc_date = datetime.strptime(date_sort, sql_date_format)
    
    diff = calc_date - init_date
    position = int(diff.total_seconds() / (15*60))
    
    return position

def get_current_pfx_list(rfd) :
    fn = ' Get the Current Available PFXs'
    
    curr_pfx_list = []
    
    for key in rfd.keys() :
        if key[:3] not in curr_pfx_list : curr_pfx_list.append(key[:3])
    
    return curr_pfx_list
    