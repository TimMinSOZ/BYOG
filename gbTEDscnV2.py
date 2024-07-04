#gbTEDV2

from gbGFuncsV2 import*
from gbGRunV2 import*
from gbBaseV2 import*
from gbFfuncsV2 import*
from gbCGscnV2 import*
from gbCPscnV2 import*
import numpy as np
import PySimpleGUI as sg

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()
con_obj.autocommit = True

gui_size = 15
bs = (15,1) # Button size
bf = ('Helvetica',gui_size) # Button Font & size
tf = ('Helvetica',gui_size) # Text font & size
mf = ('Helvetica',gui_size) # Menu Font and size
ts = ('Helvetica',30) # Title Size


def evb_demand_scn(rfd, rft, rfc, rfg, pfx) :
    fn = ' EVB Demand Screen   '

    cur_obj.execute('select chg_day_pc, chg_srt_pc, hse_bat_pc, grid_bat_pc from gbstg where genfuel = "EVB" and genregion = "NSW"')
    evb_usage_pc = cur_obj.fetchone()
    print(evb_usage_pc)
    if evb_usage_pc != [] :
    
        ctd = rft[pfx+'chg_day_pc'] = int(evb_usage_pc[0])
        csd = rft[pfx+'evb_srt_chg_pc'] = int(evb_usage_pc[1])
        hbd = rft[pfx+'EVB_house_bat_pc'] = int(evb_usage_pc[2])
        gbd = rft[pfx+'EVB_grid_bat_pc'] = int(evb_usage_pc[3])

    def evb_demand_scn() :
        
        chg_day_pc = [[sg.Frame("Percent of EV Owners Who Charge During the Day - 8am to 4pm", 
                [[sg.Slider(range=(0,100),default_value = ctd , resolution = 1, key = '-CHGTIME-', enable_events = True, size=(40,25),background_color ='white', text_color = 'blue', orientation='horizontal', font=('Helvetica', 20), relief = sg.RELIEF_RAISED, trough_color = 'lightblue')]],
                title_location = sg.TITLE_LOCATION_TOP,  title_color = 'white')],
                [sg.T()]]
        evb_srt_chg_pc = [[sg.Frame("Percent of EV Owners Charging Mainly with Home Solar ", 
                    [[sg.Slider(range=(0,100), default_value = csd, resolution = 1, key = '-CHGSOLAR-', enable_events = True, size=(40,25),background_color ='white', text_color = 'blue', orientation='horizontal', font=('Helvetica', 20), relief = sg.RELIEF_RAISED, trough_color = 'lightblue')]],
                        title_location = sg.TITLE_LOCATION_TOP, title_color = 'white')],
                    [sg.T()]]
        EVB_house_bat_pc = [[sg.Frame("Percent of EV Owners Using EVB as House Battery ", 
                    [[sg.Slider(range=(0,100), default_value = hbd,resolution = 1, key = '-HSEBAT-', enable_events = True, size=(40,25),background_color ='white', text_color = 'blue', orientation='horizontal', font=('Helvetica', 20), relief = sg.RELIEF_RAISED, trough_color = 'lightblue')]],
                        title_location = sg.TITLE_LOCATION_TOP, title_color = 'white')],
                    [sg.T()]]
        EVB_grid_bat_pc =  [[sg.Frame("Percent of EV Owners Using EVB as a Grid Battery", 
                    [[sg.Slider(range=(0,100), default_value = gbd,resolution = 1, key = '-GRIDBAT-', enable_events = True, size=(40,25),background_color ='white', text_color = 'blue', orientation='horizontal', font=('Helvetica', 20), relief = sg.RELIEF_RAISED, trough_color = 'lightblue')]],
                        title_location = sg.TITLE_LOCATION_TOP, title_color = 'white')],
                    [sg.T()]]
        chgbut = [[sg.T()],
                    [sg.P(), sg.B("OK", key = '-CHGBUT-', font = bf ), sg.P()]]
        
        evb_chg_w = sg.Window("EVB Charge Parameters", chg_day_pc + evb_srt_chg_pc + EVB_house_bat_pc + EVB_grid_bat_pc + chgbut, keep_on_top=True, disable_close = True, disable_minimize = True, resizable=False)
        
        return evb_chg_w
    
    evb_chg_w = evb_demand_scn()
    
    while True :
        
        c_event, c_values = evb_chg_w.read()
        
        if c_event in ['Exit', sg.WIN_CLOSED, 'escape'] :
            
            evb_chg_w.close()
            break
            
        if c_event == '-CHGBUT-' :
            
            rft[pfx+'chg_day_pc'] = c_values['-CHGTIME-']
            rft[pfx+'evb_srt_chg_pc'] = c_values['-CHGSOLAR-']
            rft[pfx+'EVB_house_bat_pc'] = c_values['-HSEBAT-']
            rft[pfx+'EVB_grid_bat_pc'] = c_values['-GRIDBAT-']
            
            cur_obj.execute('update gbstg set chg_day_pc = %s, chg_srt_pc = %s, hse_bat_pc = %s, grid_bat_pc = %s where genfuel = "EVB"',[c_values['-CHGTIME-'], c_values['-CHGSOLAR-'], c_values['-HSEBAT-'], c_values['-GRIDBAT-']])
            con_obj.commit()

            evb_chg_w.close()
            break
    
    return()

        
        