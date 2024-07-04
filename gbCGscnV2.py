# gbCGscnV2

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


def main_graph_control(rfd,rft,rfc,rfg,pfx) :

    demslide =  [[sg.Frame("Adjust Black Demand Line's Thickness", 
                [[sg.Slider(range=(0,600),default_value = 600 -rfg['demline'], resolution = 10, key = '-DEMSLIDE-', enable_events = True, size=(40,25),background_color ='white', text_color = 'blue', orientation='horizontal', font=('Helvetica', 20), relief = sg.RELIEF_RAISED, trough_color = 'lightblue')]],
                title_location = sg.TITLE_LOCATION_TOP,  title_color = 'white')],
                [sg.T()]]
    legchange = [[sg.Frame("Adjust Legend Size and Font Type ", 
                [[sg.Slider(range=(0,40), default_value = rfg['legsize'], resolution = 1, key = '-LEGSLIDE-', enable_events = True, size=(40,25), background_color ='white', text_color = 'blue', orientation='horizontal', font=('Helvetica', 20), relief = sg.RELIEF_RAISED, trough_color = 'lightblue')],
                [sg.P(), sg.T('Legend Normal or Bold   '), sg.Combo(['normal','bold'], default_value = rfg['legbold'], key = '-LEGFONT-', auto_size_text = True, text_color = 'blue', background_color = 'lightblue', enable_events = True), sg.P()]],
                    title_location = sg.TITLE_LOCATION_TOP, title_color = 'white')],
                    [sg.T()]]
    graph_table =  [[sg.Frame("Adjust Graph Table Size", 
                [[sg.Slider(range=(0,40), default_value = rfg['graph_table_size'],resolution = 1, key = '-TBLSLIDE-', enable_events = True, size=(40,25), background_color ='white', text_color = 'blue', orientation='horizontal', font=('Helvetica', 20), relief = sg.RELIEF_RAISED, trough_color = 'lightblue')],
                [sg.P(), sg.T('Show Graph Table Y / N   '), sg.Combo(['Y','N'], default_value = rfg['graph_table'], key = '-TBLSHOW-', auto_size_text = True, text_color = 'blue', background_color = 'lightblue', enable_events = True), sg.P()]],
                    title_location = sg.TITLE_LOCATION_TOP, title_color = 'white')],
                [sg.T()]]
    anatable =  [[sg.Frame("Adjust Gap / Excess Analysis Table Size", 
                [[sg.Slider(range=(0,40), default_value = rfg['graph_analysis_table_size'],resolution = 1, key = '-ANASLIDE-', enable_events = True, size=(40,25), background_color ='white', text_color = 'blue', orientation='horizontal', font=('Helvetica', 20), relief = sg.RELIEF_RAISED, trough_color = 'lightblue')],
                [sg.P(), sg.T('Show Gap or Excess Analysis Table Y / N   '), sg.Combo(['Gap','Excess','Hide Both'], default_value = rfg['graph_analysis_table'], key = '-ANAGAPEXS-', auto_size_text = True, text_color = 'blue', background_color = 'lightblue', enable_events = True), sg.P()]],
                    title_location = sg.TITLE_LOCATION_TOP, title_color = 'white')],
                [sg.T()]]
    showstg =   [[sg.Frame("Show Battery Storage Levels",
                [[sg.Slider(range=(0,5), default_value = rfg['stg_line_width'], resolution = 1, key = '-STGSLIDE-', enable_events = True, size=(40,25), background_color ='white', text_color = 'blue', orientation='horizontal', font=('Helvetica', 20), relief = sg.RELIEF_RAISED, trough_color = 'lightblue')],                           
                [sg.P(), sg.T('Show Battery Storage Y / N  '), sg.Combo(['Y','N'], default_value = rfc[pfx+'show_battery'], key = '-SHOWSTG-', auto_size_text = True, text_color = 'blue', background_color = 'lightblue', enable_events = True), sg.P(), sg.T('Line Colour '), sg.Combo(['black', 'blue', 'green', 'red', 'yellow', 'white'], default_value = rfg['stg_line_color'], key = '-SHOWCOL-', auto_size_text = True, text_color = 'blue', background_color = 'lightblue', enable_events = True),sg.P()]], 
                title_location = sg.TITLE_LOCATION_TOP, title_color = 'white')],
                [sg.T()]]
    okbutton =  [[sg.T()],
                [sg.P(), sg.B("OK", key = '-DSOK-', font = bf ), sg.P()]]
    
    graphctl = sg.Window("Graph Control Parameters", demslide + legchange + graph_table + anatable + showstg + okbutton, keep_on_top=True, disable_close = True, disable_minimize = True, resizable=False)
    
    
    while True :
        
        event, values = graphctl.read()
        print(event, values)
        
        if event in (None, 'Exit', '-EXIT-') :
            print("[LOG] Clicked Exit!")
            graphctl.close()
            break
        
        if event == '-DSOK-' :
            rfg['demline'] = int(600 - values['-DEMSLIDE-'])
            rfg['legsize'] = int(values['-LEGSLIDE-'])
            rfg['legbold'] = str(values['-LEGFONT-'])
            rfg['graph_table'] = str(values['-TBLSHOW-'])
            rfg['graph_table_size'] = int(values['-TBLSLIDE-'])
            rfg['graph_analysis_table_size'] = int(values['-ANASLIDE-'])
            rfg['graph_analysis_table'] = str(values['-ANAGAPEXS-'])
            rfg['stg_line_width'] = int(values['-STGSLIDE-'])
            rfc[pfx+'show_battery'] = str(values['-SHOWSTG-'])
            rfg['stg_line_color'] = str(values['-SHOWCOL-'])    
            
            graphctl.close()
            break
    return
