#gbTevbV2

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Button, Slider

from datetime import datetime
#from gbfuncsV2 import*
from gbGFuncsV2 import*
from gbGRunV2 import*
#from gbctlscnV2 import*
from gbBaseV2 import*
#from gbGctlV2 import*
from gbGSelectV2 import*
import PySimpleGUI as sg
import copy
#import time
import pyautogui as pag

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()
con_obj.autocommit = True



def evb_main_scn(rfd,rft,rfc,rfg,pfx, datalines) :

    rft[pfx+"evb15yr"] = 0
    ax = rfc['ax']
    fig = rfc['fig']
    plt = rfc['plt']
    startamount = 1534
    endamount = 1000000
    growth = .1#
    periods = 64
    yholder = [0 for i in range(periods)]
    #norway = np.array([733,2243,4700,10636,23408,39632,50875,71737,86290,88443,113588,167949,166000]) * 5.9 # Figures since 2010 to 2022
    australia = np.array([0.02,0.12,0.15,0.12,0.19,0.3,0.6,0.78,2.4,5.1,8.7]) * 10000 # 2023 Best guess from 2013 to 2023
    norway = np.array([0.2,0.4,1.9,2.7,6.1,13.8,22.4,29.1,39.2,49.1,55.9,74.7,86.2,87.8, 90.4]) * 10000 # Figures 2013 to inc Q1-3 2023 - 2012 Made up ie half 2013
    sweden = np.array([0.35,0.71,1.53,2.62,3.5,5.2,8.2,14.4,30.2,43.3,56.1]) * 10000
    china = np.array([0.04,0.08,0.23,0.84,1.31,2.1,4.2,4.9,5.4,15,30,38,43]) * 10000 # inc Q1-3 23
    uk = np.array([0.08,0.16,0.59,1.07,1.37,1.86,2.53,2.9,10.7,18.6,22.9,25.2]) * 10000 # inc Q1-3 23
    usa = np.array([0.3,0.6,0.72,0.66,0.9,1.1,2.1,1.9,2.2,4.7,7.7,11.2,13.7]) * 10000 # inc Q3 23 (Need Totals inc All Electric)
    canada = np.array([0.09,0.18,0.28,0.35,0.58,0.92,2.2,3,3.5,6.6,9.4,12.3]) * 10000 # inc Q2 2023
    romania = np.array([0.17,0.34,0.28,0.5,1.03,2.11,2.8,7.12,15.5,21.7]) * 10000
    iceland = np.array([0.65,1.3,2.1,3.6,5.6,11.7,17.2,22.6,45,54.7,56.1,60.5]) * 10000
    germany = np.array([0.12,0.25,0.43,0.73,1.1,1.58,1.9,3.0,13.5,26,31.4,37]) * 10000 # inc Aug 2023
    japan = np.array([0.91,1.06,0.68,0.59,1.1,1,0.9,0.6,1,3,4.3]) * 10000
    
    evbcntrys = ['australia','norway','sweden','china','uk','usa','canada','romania','iceland','germany','japan']
    evbsales = [australia, norway, sweden, china, uk, usa, canada, romania, iceland, germany, japan]
    evbgdata = list(zip(evbcntrys, evbsales))
    print(evbgdata)

    def dbl(country) :
        last = 0
        newcountry = []
        for i, yeartot in enumerate(country) :
            newcountry.append((yeartot + last) / 2)
            newcountry.append(yeartot)
            last = yeartot
        return newcountry

    xticks = [x for x in range(0,periods,8)]
    xlabels = [0 + int(i/2) for i in range(0,periods,8)]


    def writegraph(ax, growth, periods) :
        ax.clear()
        ax.plot(scurve(growth , periods , endamount, startamount), lw=2, label = 'Australia', color = 'b')
        ax.plot(yholder, color = 'k')
        ax.plot(dbl(norway),label = "Norway", color ='g')
        ax.plot(dbl(sweden),label = "Sweden", color ='y')
        ax.plot(dbl(china),label = "China", color ='m')
        ax.plot(dbl(uk),label = "UK", color ='c')
        ax.plot(dbl(romania),label = "Romania", color ='k')
        ax.plot(dbl(germany),label = "Germany", color ='y')
        ax.plot(dbl(usa),label = "USA", color ='c')
        ax.plot(dbl(canada),label = "Canada", color ='r')
        ax.plot(dbl(iceland), label = 'Iceland', color = 'm')
        ax.plot(dbl(japan), label = 'Japan', color = 'k') 
        for gd in evbgdata :
            if gd[0] == 'australia' : continue
            ax.text(len(gd[1])*2, gd[1][-1], str(gd[0][0]).upper() + gd[0][1:3], color='k', fontsize = 13, weight = 'bold')      
        ax.margins(0,0)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels)
        ax.set_xlim(0, periods)
        ax.set_ylim(0,1050000)
        ax.legend(loc = 'upper left', title = ' EV Rate of Sales Growth', ncol = 2, title_fontproperties = {'weight':'bold', 'size' : 19}, fontsize = 15, prop = font_manager.FontProperties(family = 'monospace', weight = 'bold', style = 'normal', size = 15))
        ax.set_xlabel('Time (Years)')
        ax.set_ylabel(' Growth Rate ')
        ax.set_title(" ---  E V    U P T A K E  --- \n Will Australia be as fast as Norway (Top Green) or as slow as Japan (Bottom Black) \n  Click The TWO Bottom Sliders To Alter Australia's Blue 'S' Curve \n To approximate what you think our EV growth could look like", fontweight ="bold", size=25)

        return


    writegraph(ax, growth, periods)
    # adjust the main plot to make room for the sliders
    fig.subplots_adjust(left=0.1, bottom=0.25, top=0.85)

    # Make a horizontal slider to control the frequency.
    years_slider = Slider(ax=fig.add_axes([0.25, 0.11, 0.65, 0.05]), label='Shorter = Faster', valstep = 0.1, valmin=1, valmax=periods*2, valinit=periods, orientation="horizontal")
    years_slider.valtext.set_visible(False)

    # Make a vertically oriented slider to control the amplitude
    growth_slider = Slider(ax=fig.add_axes([0.25, 0.16, 0.65, 0.05]), label="Higher = Faster", valmin=0.01, valmax=growth*3, valinit=growth, orientation="horizontal")
    growth_slider.valtext.set_visible(False)
    # [0.1, 0.25, 0.0325, 0.63]

    # The function to be called anytime a slider's value changes
    def update(val):
        fn = " Update For Slider Changes "
        growth = growth_slider.val
        periods = round(years_slider.val)
        ax.clear()
        writegraph(ax, growth, periods)
        fig.canvas.draw()
        fig.canvas.flush_events()
        return

    # register the update function with each slider
    years_slider.on_changed(update)
    growth_slider.on_changed(update)

    def writeevbdata():
        fn = " Write EVB Data to rft[pfx+'evb15yr'] as a total  "
        
        growth = growth_slider.val
        periods = int(years_slider.val)
        #print("growth = ", growth, " periods  =  ", periods)

        evbdata = scurve(growth , periods , endamount, startamount)
            
        evbdata = [evbdata[i] for i in range(0, len(evbdata), 2) if rft["FYD"+"ALL"+"EVB_cur_sales"] <= evbdata[i]] # 6month to 1 year 

        evbdata.insert(0, rft["FYD"+"ALL"+"EVB_cur_sales"] )
        
        #print("evbdata after select and insert", evbdata)
        while len (evbdata) < 15 : # The renewable grid is assumed to be 15 years .
            evbdata.append(round(evbdata[-1]*1.01))
            
        evbdata = np.round(np.array(evbdata[:15]) / 1000000, 3)
        #print("evbdata after cut to 14 and make decimal", evbdata)
        
        evbcdata = np.round(np.cumsum(evbdata),3)
        
        evb_data_pc = [str(int(evbc / 15 * 100)) + "%" for evbc in evbcdata]
        
        evb_gwh = np.round(evbcdata * rft["FYD"+"ALL"+"EVB_avg_battery_kwh"],1)
        
        evb_gwh_pc = [str(int(evb / rft["FYD"+"ALL"+"ALL"] * 100 * 365)) + "%" for evb in evb_gwh]
        
        evb_gwh_dem = [np.round(dem * rft["FYD"+'EVB_annual_KWH_demand']) for dem in evbcdata]
        
        evb_gwh_dem_pc = [str(int(gwh / rft["FYD"+"ALL"+"ALL"] * 100))+"%" for gwh in evb_gwhdem]
        
        years = [rfc['FYD'+'start_year'] + i for i in range(15)]
        
        evb15yr = [list(l) for l in zip(years, evbdata, evbcdata, evb_data_pc, evb_gwh, evb_gwh_pc, evb_gwh_dem, evb_gwh_dem_pc)]

        rfc[pfx+"evb15yr"] = copy.deepcopy(evb15yr[14])
        rft[pfx+"evb15yr"] = rfc[pfx+"evb15yr"][2]
        #print(fn,"Final 15 Year EVB Sales  ", rfc[pfx+"evb15yr"], "  Total = " , rft[pfx+"evb15yr"], "  Length = ", len(rfc[pfx+"evb15yr"]))

        for region in rfc["FYD"+"genreg"]  :
            rft[pfx+region+'evb'] = round((rft[pfx+"evb15yr"]) * (rft["FYD"+region+"pop_pc"] ),3)
            #print( " This is the Calc which writes to SQL : ", round(rft[pfx+"evb15yr"] * (rft["FYD"+region+"pop"] / rft["FYD"+"ALL"+"pop"] ),3), region)
            cur_obj.execute(' update gbstg set qty = %s where genregion = %s and gencode = "EVB"',[rft[pfx+region+'evb'],region])
            con_obj.commit()
            for line in datalines :
                if line[1] == region :
                    line[9] = rft[pfx+region+"evb"]
        
        return evb15yr

    fig.canvas.draw()
    fig.canvas.flush_events()
    fig.show()

    gui_size = 15
    bs = (15,1) # Button size
    bf = ('Helvetica',gui_size) # Button Font & size
    tf = ('Helvetica',gui_size) # Text font & size
    mf = ('Helvetica',gui_size) # Menu Font and size
    ts = ('Helvetica',30) # Title Size

    screen_width, screen_height = pag.size()
    print("Screen Resolution: {} x {}".format(screen_width, screen_height))


    gbutton = [[sg.B('ACCEPT', size = bs , font = bf, button_color= 'white on light blue' ,  mouseover_colors = 'blue on white', key = '-ACCEPT-', border_width = 7, enable_events = True)]]

    gbutwin = sg.Window('Press [ACCEPT] To Continue', gbutton ,  grab_anywhere=True, no_titlebar = True, disable_close = True, disable_minimize = True, resizable=False, location = (int(screen_width /2),int(screen_height*0.917)), margins=(0,0), element_justification = "center",  finalize=True, keep_on_top=True)

    while True :
        event, values = gbutwin.read()

        def evtable (evtitle, evlines, evheader, evwidths ) :

            evtable = [[sg.Table(values = evlines, headings=evheader,  max_col_width=25, auto_size_columns=False, col_widths=evwidths,
                    display_row_numbers=True,  justification= 'center', num_rows=15, key='-TABLE-', selected_row_colors='black on white',
                    expand_x=False, expand_y=True, vertical_scroll_only=False, enable_click_events=True )],
                    [sg.Push(), sg.B('   OK   ', key = '-OK-'), sg.Push()]]

            evwindow = sg.Window(evtitle, evtable, resizable=True, finalize=True)

            return evwindow

        if event == '-ACCEPT-' :

            gbutwin.close()
            evb15yr = writeevbdata()
            evwindow = evtable("EV Sales per Year and Total On Road and GWH's", evb15yr,["Year", "Sales (Mil)", "On Road (Mil)", "Of On Road", " Stg GWH's "," Of Grid", "GWH Extra", "Of Demand"],[10,12,12,8,12,8,12,10])

            while True :

                event, values = evwindow.read()

                if event == sg.WIN_CLOSED or event == '-OK-':
                    
                    ###### Write Here the Data of EVB quantaties away  ######
                    
                    evwindow.close()
                    for i, axe in enumerate(fig.axes) :
                        if i == 0 : continue
                        rfc['plt'].delaxes(fig.gca())
                    rfc['plt'].subplots_adjust(top=0.925, bottom=0.1, left=0.025, right=0.99, hspace=0.2, wspace=0.2)
                    break
        break
                
    return datalines
        
        
