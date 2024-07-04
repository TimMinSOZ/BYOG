# gbTibhV2 - Contains all functions which can be called from the Table View and relate to IHB

import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.colors as mcolors
#from datetime import datetime
import PySimpleGUI as sg
#
from gbUtilsV2 import*
#import copy

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports", buffered = True)
cur_obj = con_obj.cursor()
con_obj.autocommit = True

def ihb_main_scn(rfd,rft,rfc,rfg,pfx, datalines) :

    stp = "IHB"
    cur_obj.execute('select pricefall, lifeinc, kwhkginc, subsidy, yrsfix, yrsred from gbgenfuel where code = "IHB"')
    ihbdrivers = cur_obj.fetchall()
    for driver in ihbdrivers : # Currently save as 6 x Enteries for each Region but do not allow that to be changed so all regions are the same.
        pricepc = int(driver[0])
        lifeinc = int(driver[1])
        kwhkginc = int(driver[2])
        subsidy = int(driver[3])
        yrsfix = int(driver[4])
        yrsred = int(driver[5])

    def ihb_entry_scn (pricepc, lifeinc, kwhkginc, subsidy, yrsfix, yrsred) :

        title1 = "Enter The House Battery Uptake Drivers"

        layihb = [[sg.T(" Enter Key Predictions for 15 years for House Batteries ", font = ("Helvetica", 26), justification = "center", text_color = 'blue', background_color = 'white')],
                [sg.T()],
                [sg.T()],
                [[sg.Frame('Entry Section',
                [[sg.T(' Enter Annual Price Fall %age                   '), sg.P(), sg.I(size = (2,1), default_text = pricepc, key = '-PFPC-', enable_events = True, justification = 'right')],
                [sg.T(' Enter Annual Life Increase %age              '), sg.P(), sg.I( size = (2,1), default_text = lifeinc,  key = '-ALPC-', enable_events = True, justification = 'right')],
                [sg.T(' Enter Annual KWH / KG Increase  %age  '), sg.P(), sg.I( size = (2,1), default_text = kwhkginc,  key = '-KKPC-', enable_events = True, justification = 'right')],
                [sg.T('')]], title_location = 'n', title_color = 'blue', vertical_alignment ='c')]],
                [sg.T()],
                [sg.T('Use Slider for Gov Subsidies')],
                [sg.Slider(range=(0,5000),default_value=subsidy,resolution = 100, key = '-SUBSIDY-', enable_events = True, size=(40,25),orientation='horizontal',font=('Helvetica', 20))],
                [sg.T(' Years Subsidy Fixed ? ')],
                [sg.I(size = (2,1), default_text = yrsfix,  key = '-YRSFIX-', enable_events = True, justification = 'right')],
                [sg.T(' Years Subsidy Reducing ? ')],
                [sg.I(size = (2,1), default_text = yrsred,  key = '-YRSRED-', enable_events = True, justification = 'right')],
                [sg.T()],
                [sg.T()],
                [sg.Push(), sg.B("    CANCEL    ", key = '-CANCEL-'), sg.B("   DETAILS   ", key = '-DETAIL-'), sg.B("    UPDATE    ", key = "-UPDATEGF-"), sg.Push()]]

        window_ihb = sg.Window(title1, layihb, resizable=True, finalize=True, element_justification = 'center', keep_on_top=True)

        while True:

            event, values = window_ihb.read()

            if event == sg.WIN_CLOSED or event == '-CANCEL-':
                break

            if event == "-UPDATEGF-" and stp == "IHB" :

                pricepc = int(values['-PFPC-'])
                lifeinc = int(values['-ALPC-'])
                kwhkginc = int(values['-KKPC-'])
                subsidy = int(values['-SUBSIDY-'])
                yrsfix = int(values['-YRSFIX-'])
                yrsred = int(values['-YRSRED-'])

                update_ihb_drivers(pricepc, lifeinc, kwhkginc, subsidy, yrsfix, yrsred) # We are calling inside the definition ??????

                nbtitle = "    Home Battery Takeup Over 15 Years    "
                nbheader = ['   Year    ', ' Bat Cost $ ', '  Life (Yrs)  ', '  New (Mill) ', ' Installed (Mill)','  GWHs  ', 'Subsidy $m', ' %  Mkt']
                nbwidths = [8,10,8,10,12,8,10,8]
                nbwindow = nbtable(nbtitle, rfc[pfx+"ALL"+"newihb"], nbheader, nbwidths)

                while True:

                    event, values = nbwindow.read()

                    if event == sg.WIN_CLOSED or event == '-OK-':
                        nbwindow.close()
                        break
                break

        window_ihb.close()


    def nbtable (nbtitle, nblines, nbheader, nbwidths ) :

        nbtable = [[sg.Table(values = nblines, headings=nbheader,  max_col_width=25, auto_size_columns=False, col_widths=nbwidths,
                            display_row_numbers=True,  justification= 'center', num_rows=20, key='-TABLE-', selected_row_colors='black on white',
                            expand_x=False, expand_y=True, vertical_scroll_only=False, enable_click_events=True )],
                [sg.Push(), sg.B('   OK   ', key = '-OK-'), sg.Push()]]

        nbwindow = sg.Window(nbtitle, nbtable, resizable=True, finalize=True, keep_on_top=True)

        return nbwindow


    def update_ihb_drivers(pricepc, lifeinc, kwhkginc, subsidy, yrsfix, yrsred) :
        fn = " Update IHB Drivers   "

        ##### WRITE SCREEN VALUES TO THE DATABASE #####
        sqlwparams = [pricepc, lifeinc, kwhkginc, subsidy, yrsfix, yrsred, stp]
        cur_obj.execute('update gbgenfuel set pricefall = %s, lifeinc = %s , kwhkginc = %s, subsidy = %s , yrsfix = %s, yrsred = %s where code = %s', sqlwparams)
        con_obj.commit()

        ##### CALCULATE THE GWH STORAGE IN TOTAL AFTER 15 YEARS  ######

        growth = (pricepc^2 + lifeinc*2 + kwhkginc+40) / 200 # THIS IS MADE UP AS A METHOD FOR GROWTH
        bat_sales = rfc['FYD'+'annual_ihb_sales'] 
        cur_ihb_installed = rfc['FYD'+'curr_ihb_installed']  # See notes in GBBYOGV2 as set up there
        bat_cost = rfc['FYD'+'ihb_cost']
        autobuy = 3000  # At this price every household will buy a battery over 10 years
        bat_life = rfc['FYD'+'ihb_life']
        subsidy_profile = [subsidy]*yrsfix+[subsidy - subsidy / (yrsred+1) * i for i in range(yrsred)]+[0]*(15-yrsfix-yrsred)  # Gives a list of subsidy by year
        cost_profile = []
        ihb_life_profile = []

        for i in range(75) :
            bat_cost = bat_cost * (100-pricepc)/100
            bat_life = bat_life * (100+lifeinc)/100
            cost_profile.append(round(bat_cost))
            ihb_life_profile.append(round(bat_life,1))
        year = 5 # At reaching autobuy add 5 years to mop up market
        if cost_profile[74] < autobuy :
            while cost_profile[year-5] > autobuy : year += 1
        else :  year = 74

        #for region in rfc["FYD"+"genreg"] : ##### WHY DO THIS BY REGION WITH TOTALING - BETTER TO DO NATIONAL AND THEN SPLIT AT END #####

        rfc[pfx+'ALL'+"newihb"] = []

        cur_obj.execute('select fuel, round(sum(srt_mkt),3) from gbrentgt where fuel = "SRT" group by fuel')
        ibh_mkt = cur_obj.fetchone()

        cur_obj.execute('select round(sum(mktsize),3) from gbstg where genfuel = "IHB" group by mktsize with rollup')
        stg_data = cur_obj.fetchall()

        mkt_size = round(float(stg_data[-1][0]),3)
        ibh_stg = rfc['FYD'+'ihb_avg_kwh']
        #ibh_mkt_pc = round(float(ibh_mkt[1])/mkt_size,3) # pc = percent but done as a fraction

        ###### USE AN 'S' CURVE TO DETERMINE NEW BATTERIES PURCHASED #####
 
        cum_sales = scurve(growth , year , mkt_size * 1000000, cur_ihb_installed) #### Create an 'S' Curve of sales and then fit current sales to 'S' Curve
        act_sales = np.array([round((cum_sales[i+1] - cum_sales[i]) / 1000000 + bat_sales,3) for i in range(len(cum_sales)-1)])
        sub_cost_profile = list(np.array(cost_profile[:15]) - np.array(subsidy_profile))

        ##### Locate value in cost_profile and update act_sales ie At Cost X then Sales are Y and we use subs to change cost X and move sales for given cost to match cost after subs ie Sales in that year are derived from cost in that year.

        for j, sub in enumerate(sub_cost_profile) :
            for i, value in enumerate(cost_profile) :
                if sub < value : continue
                else : break
            act_sales[j] = act_sales[i]

        cum_sales = [round(cur_ihb_installed + act_sales[:i].sum(),4) for i in range(len(act_sales))]

        sub_cost = np.round(np.cumsum(np.array(subsidy_profile) * cum_sales[:15]),3)
        
        ## formatted_numbers = [f"{num:.3f}" for num in numbers] ### Need to apply 
        
        ## formatted_number = f'{number:,}' to add ',000's

        for i in range(15) : ##### ONLY DISPLAY 15 YEARS OF RESULTS #####

            rfc[pfx+"ALL"+"newihb"].append([i + rfc['FYD'+'start_year'], f'{round(sub_cost_profile[i]):,}', f'{round(ihb_life_profile[i],1):.1f}', f'{round(act_sales[i],3):.3f}', f'{round(cum_sales[i],3):.3f}' , f'{round(cum_sales[i] * ibh_stg,3):.1f}', f'{round(sub_cost[i]):,}', str(round(cum_sales[i]/mkt_size*100,1))+"%"]) 

        for region in rfc['FYD'+'genreg'] :
            
            region_split_pc = rft["FYD"+region+'pop_pc']
            ihb_qty = round(float(rfc[pfx+'ALL'+"newihb"][14][4]) *  region_split_pc,3)
            
            print(region, ihb_qty)
                    
            cur_obj.execute('update gbstg set qty = %s where genregion = %s and genfuel = "IHB"',[ihb_qty , region])
            con_obj.commit()
            
            for line in datalines :
                if line[1] == region :
                    line[9] = ihb_qty

    ihb_entry_scn(pricepc, lifeinc, kwhkginc, subsidy, yrsfix, yrsred)


    return datalines




