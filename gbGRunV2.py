# gbgraphrunV2 # move all the functions running the graph to here ie display, legend, tables, create_xtick_s

import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
#from matplotlib.widgets import Button
from datetime import datetime

from gbUtilsV2 import*
from gbGRButV2 import *
from gbGRTablesV2 import *

def create_legend(rfd, rft, rfc, rfg, pfx) :
    # Creates the Graph legend including info on gaps, exs, Sup & Dem Totals legstats and legtitle are used in ax.legend 
    # graphleglist and leganme are used in changing colors on the Legend ie ax.legend must be done first"
    fn = " Create Graph Legend   "
    #print(fn,'Start  ', datetime.now())
    legstats = []
    region = rfg["region"]
    gcd = rfg["gencode"]
    leg_length = len(rfg["genfuel"])
    if rfg["startpos"] == 0 : rfg["startpos"] = 1
    
    for fuel in rfg["genfuel"] :
        if pfx+region+fuel+gcd in rfd.keys() :
            if fuel == "GAP" or fuel == "EXS" : legsign = -1
            else : legsign = 1
            legname = rfc["FYD"+fuel+"fuel_name"]
            if fuel == "ZL1" : fuel = "ALL"
            if fuel == "DL1" : fuel = "DEM"
                
            genvalue = round(np.array(rfd[pfx+region+fuel+gcd][rfg["startpos"] : rfg["endpos"]]).sum()/4) ## Removed * legsign 1/12/23
            legname = legname.ljust(15," ")
            prodout = (f"{int(genvalue) :,d}")
            prodout = prodout.rjust(7," ")
            if np.array(rfd[pfx+region+"ALL"][rfg["startpos"] : rfg["endpos"]]).sum()/4 != 0 :
                spercent = str(round(genvalue / (np.array(rfd[pfx+region+"ALL"][rfg["startpos"] : rfg["endpos"]]).sum()/4) * 100 * legsign))
                spercent = spercent.rjust(5," ")
            else : spercent = 100
            if np.array(rfd[pfx+region+"DEM"][rfg["startpos"] : rfg["endpos"]]).sum()/4 != 0 :
                dpercent = str(round(genvalue / (np.array(rfd[pfx+region+"DEM"][rfg["startpos"] : rfg["endpos"]]).sum()/4) * 100 * legsign))
                dpercent = dpercent.rjust(5," ")
            else : dpercent = 100
            legstats.append(legname+prodout+" GWH's"+str(spercent)+"%"+str(dpercent)+"%")
            #leg_length += 1
    legtitle = "            Generator Type         GWH's              Sup     Dem  "
    if rfg['legsize'] !=0 :
        leg = rfc["ax"].legend(legstats, ncols=1, loc='upper left', title = legtitle, title_fontsize = rfg['legsize'], prop = font_manager.FontProperties(family = 'monospace', weight = rfg['legbold'], style = 'normal', size = rfg['legsize']))
        count = 0
        for text in leg.get_texts():
            count = count + 1
            if count == leg_length - 2 : text.set_color("red")
            if count == leg_length - 1 : text.set_color("green")
            if np.array(rfd[pfx+region+"ALL"][rfg["startpos"] : rfg["endpos"]]).sum()/4 != 0 and count == leg_length and round(np.array(rfd[pfx+region+fuel][rfg["startpos"] : rfg["endpos"]]).sum()/4 / (np.array(rfd[pfx+region+"ALL"][rfg["startpos"] : rfg["endpos"]]).sum()/4) * 100) > 100 : text.set_color("red")
            
    #print(fn,'Finish  ', datetime.now())
    return


def create_xticks(rfd, rft, rfc, rfg, pfx) : # Start and end there but no change to use them
    # Determine How to Manage X Ticks and numbering
    fn = " Create Ticks Function   "
    from datetime import datetime
    from datetime import timedelta
    #print(fn, 'Start ', datetime.now())
    start_date = date_obj_from_position(rfg["startpos"], ipstart_date = rfc['FYD'+"start_date"])
    begin_day = start_date.weekday()
    begin_hour = start_date.hour
    months_in_year =["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    days_in_week = ["W","T","F","S","S","M","T"]
    xtick_vals=[]
    xtick_labels =[]
    xtick_mth_last = ""
    reads_in_day = int(96/rfg["degran"])
    graph_days = int((rfg["endpos"] - rfg["startpos"]) / 96) # 24-03-31 Changed '96' to reads_in_day and back again as caused 3 sec slowness in graph set xtick_s
    if graph_days == 0 :  graph_days = 1
    #print ("from create ticks function - days are  ", graph_days, reads_in_day, rfg["degran"] )
    xtick_cnt = 0
    if graph_days < 7 :
        for days in range(graph_days+1) :
            nextday = date_obj_from_position(rfg["startpos"] + (days * 96))
            for i in range(0, 24, int(graph_days)) :
                if i < int(begin_hour) and days < 1 : continue
                xtick_vals.append(int(xtick_cnt * graph_days * 4))
                
                if i/24 == 0 : xtick_labels.append(str(nextday.day)+"/"+str(nextday.month))
                else :  xtick_labels.append(str(i) + '.00')
                
                xtick_cnt = xtick_cnt + 1

    if graph_days in range(7,32) :
        for i in range(graph_days+1) :
            xtick_vals.append(int(i * 96 / rfg["degran"]))
            rem = (i + begin_day + 6) % 7 # Returns the remainder
            
            if xtick_cnt == 0 :
                xtick_date = str(start_date + timedelta(days=i))
                xtick_mth = xtick_date[5:7]
                xtick_day = xtick_date[8:10]
                xtick_date = xtick_day+"/"+xtick_mth
                xtick_labels.append(str(xtick_date))
            else :
                xtick_labels.append(str(days_in_week[rem]))
            xtick_cnt = xtick_cnt + 1
            if xtick_cnt == 7 : xtick_cnt = 0
                
        
    # Place a DD/MM date and month when month changes
    if graph_days in range(32,71) :
        steps = int(graph_days/12)
        for i in range(0, graph_days + 1, steps) :
            xtick_vals.append(int(i * reads_in_day))
            xtick_date = start_date + timedelta(days = xtick_cnt * steps)
            xtick_date = str(xtick_date)
            xtick_mth = xtick_date[5:7]
            xtick_mth_name = months_in_year[int(xtick_mth) - 1]
            xtick_day = xtick_date[8:10]
            xtick_date = xtick_day+"/"+xtick_mth
            if xtick_mth != xtick_mth_last :
                xtick_labels.append(str(xtick_mth_name))
                xtick_mth_last = xtick_mth
            else :
                xtick_labels.append(str(xtick_date))
            xtick_cnt = xtick_cnt + 1
    #print(graph_days,xtick_vals, xtick_labels)

    if graph_days > 70 :
        xtick_day = start_date.day*reads_in_day
        xtick_month = start_date.month    
        xtick_mth_name = start_date.strftime('%b')      
        for i in range(int(graph_days / 30 + 1)) :
            if xtick_day < 3 * reads_in_day :
                xtick_vals.append(0)
                xtick_labels.append(xtick_mth_name)
                xtick_day = (30 - xtick_day / reads_in_day) * reads_in_day
            xtick_month = xtick_month + 1
            xtick_month = xtick_month % 12
            xtick_mth_name = months_in_year[xtick_month - 1]
            xtick_vals.append(xtick_day)
            xtick_labels.append(xtick_mth_name)
            xtick_day = xtick_day + 30*reads_in_day + 1
            
    #print(fn, 'Finish ', datetime.now())
    return xtick_vals, xtick_labels


def graph_display(rfd, rft, rfc, rfg, pfx) :
    fn = " Graph Display  "
    print("Doing   ", fn, "for fuel list  ", rfg["genfuel"],'  Start  ', datetime.now())
    # Get the graph colors and fuel names from rfc[pfx+fuel]
    # rfg is a dictionary carrying the key graph params = pfx, region, genfuel, gencode, degran, startpos, endpos + multiple display options
    colors = []
    rfgout = []
    rfg_plot = []
    pfx = rfg["pfx"]
    region = rfg["region"]
    gcd = rfg["gencode"]
    title_size = rft["title_size"]
    if sys._getframe(1).f_code.co_name != 'move_graph_order' : 
        if "ZL1" in rfg["genfuel"] : rfg["genfuel"] = fuelsort(rfd,rft,rfc,rfg,pfx,rfg["genfuel"])
        
    for fuel in  rfg["genfuel"] :
        colors.append(rfc["FYD"+fuel+"col"])
        # if fuel == 'GAP' and pfx+region+fuel+'ADJ' in rfd : rfd[pfx+region+fuel] -= rfd[pfx+region+fuel+'ADJ']
        # if fuel == 'EXS' and pfx+region+fuel+'ADJ' in rfd : rfd[pfx+region+fuel] += rfd[pfx+region+fuel+'ADJ']
        # if fuel == 'DEM' and pfx+region+fuel+'ADJ' in rfd : rfd[pfx+region+fuel] += rfd[pfx+region+fuel+'ADJ']

        
        if sys._getframe(1).f_code.co_name != 'show_gen_drilldown' :   #### From show_gen_drilldown is a new graph showing the generator only     
            if pfx+region+fuel in rfd.keys() :
                if rfc["zoom"] == "N" : rfgout.append(rfd[pfx+region+fuel+gcd].reshape(-1,rfg["degran"]).mean(axis=1))
                else : rfgout.append(np.array(rfd[pfx+region+fuel+gcd][int(rfg["startpos"]):int(rfg["endpos"])]))
        elif pfx+region+fuel+gcd in rfd.keys() : 
            rfgout.append(np.array(rfd[pfx+region+fuel+gcd][int(rfg["startpos"]):int(rfg["endpos"])]) / 4)
        elif pfx+region+fuel in rfd.keys() : #### Have actually failed to find the gcd in the drill down #### This skips the problem
            rfgout.append(np.array(rfd[pfx+region+fuel][int(rfg["startpos"]):int(rfg["endpos"])]) / 4)
            
        # if fuel == 'GAP' and pfx+region+fuel+'ADJ' in rfd : rfd[pfx+region+fuel] += rfd[pfx+region+fuel+'ADJ'] ### Reverse to True GAP

         
    rfc[pfx+"rfgout"] = rfgout
    rfg["rfgout"] = rfgout
    
    xaxis = np.arange(0, len(rfgout[0]), 1).astype(int)
    xtick_vals, xtick_labels = create_xticks(rfd, rft, rfc, rfg, pfx)
    
    if pfx == "FYD" : gtitle = f'FYD - {rfg["region"]} - {rfc[pfx+"start_date"][:4]} Actual Data - Using AEMO SCADA Data Feed'
    else : gtitle = f'{rfg["pfx"]} - Supply Gaps {rfg["region"]}     Init Gap : {round(rfc[pfx+region+"max_gap"] / 1000 ,1)} twh   Curr Gap : {(round(rft[pfx+region+"GAP"] / 1000 ,1))} twh'
    
    rfc["ax"].clear()
    rfc["ax"].set_title(gtitle, fontweight = "bold",size = title_size + 10)
    rfc["ax"].set_xticks(xtick_vals)
    rfc["ax"].set_xticklabels(xtick_labels)
    rfc["ax"].margins(0.01)
    rfc["ax"].stackplot(xaxis, rfgout, colors = colors , alpha = 0.9)
    ###### This line ensure the same color used for less than zero and greater than zero ie Batteries when at bottom of graph - its display only ####
    if rfg['genfuel'][0] in rfc['FYD'+'storage_fuel_list'] or rfg['genfuel'][0] == 'HVI' : rfc['ax'].stackplot(xaxis, np.where(rfgout[0] < 0, rfgout[0], 0), colors = [rfc['FYD'+rfg['genfuel'][0]+"col"]] )

    ####### Storage Levels Are Shown for ALL+ALL and region+ALL and region+fuel based on graph display storage_fuel_listare the valid stp's #######
    
    if pfx != 'FYD' and rfc[pfx+'show_battery'] == "Y" :
        
        ylim = rfc['ax'].get_ylim()  ###### This determines the correct height to keep line low - Use axes.get_ylim() Is axes my ax ? 
        
        print(fn,' This is Y lim returned from ax  ', ylim, 'Region = ', region)
        
        if rfg['genfuel'][0] in rfc['FYD'+'storage_fuel_list'] : 
            if rfg['genfuel'][0] == 'EVG' : stg_selected = 'EVG' #### Should this be 'EVB' ????
            else : stg_selected = rfg['genfuel'][0]
        else : stg_selected = 'ALL'
            
        if pfx+region+stg_selected+'STG' in rfd :
            if rfc["zoom"] == "N" : rfg_plot.append(rfd[pfx+region+stg_selected+'STG'].reshape(-1,rfg["degran"]).mean(axis=1))
            else : rfg_plot.append(rfd[pfx+region+stg_selected+'STG'][int(rfg["startpos"]):int(rfg["endpos"])])
            
            if rfg_plot != [] : rfc['ax'].plot(xaxis, rfg_plot[0], color = rfg['stg_line_color'], linewidth = rfg['stg_line_width'])
    
    #rfc["ax"].spines['left'].set_bounds(0, 40) # Sets them but does not force them ie keep the y axis still and not moving while changing the graph
    
    #rfc['ax'].set_ylim(0, 35) - ACTUALLY HOLDS AND LOCKS THE Y AXIS and ax.ylim() will set to Default
    
    create_legend(rfd, rft, rfc, rfg, pfx)

    exs_gap_analyser(rfd, rft, rfc, rfg, pfx)

    if rfg['graph_table'] == 'Y' : reg_fuel_supply_table(rfd, rft, rfc, rfg, pfx)
    
    if  rfg['rf_cost_table'] == 'Y' : reg_fuel_cost_table(rfd, rft, rfc, rfg, pfx)
    
    if rfg['rf_compare_table'] == 'Y' : grid_cost_compare_table(rfd, rft, rfc, rfg, pfx)
    
    if rfg['rf_compare_totals'] == 'Y' : totals_summary_table(rfd, rft, rfc, rfg, pfx)
    
    rfc["fig"].canvas.draw()
    rfc["fig"].canvas.flush_events()
    rfc["fig"].show()
    
    print(fn,'  Finish Actual Graph  ', datetime.now())
    return






def piedisplay(rfd, rft, rfc, rfg, pfx) :
    fn = " Pie Graph Display  "
    # Get the graph colors and fuel names from rfc[pfx+fuel]
    # Any exceptions like graphsmoother ?
    # rfg is a dictionary carrying the key graph params = pfx, region, genfuel, degran, startpos, endpos
    colors = []
    rfgout = []
    rfc["pie"] = "Y"
    pfx = rfg["pfx"] 
    region = rfg["region"]
    rfc[pfx+region+'leg_names'] = []
    for fuel in  rfg["genfuel"] :
        colors.append(rfc["FYD"+fuel+"col"])
        rfc[pfx+region+'leg_names'].append(rfc["FYD"+fuel+"fuel_name"])
        if pfx+region+fuel in rfd.keys() :
                if np.array(rfd[pfx+region+fuel][int(rfg["startpos"]):int(rfg["endpos"])]).sum() < 0 :
                    rfgout.append(np.array(rfd[pfx+region+fuel][int(rfg["startpos"]):int(rfg["endpos"])]).sum()*-1)
                else :
                    rfgout.append(np.array(rfd[pfx+region+fuel][int(rfg["startpos"]):int(rfg["endpos"])]).sum())
    
    rfc["ax"].clear()
    rfc["ax"].set_title(f'Supply Gaps '+rfg["region"]+'      Init Gap : '+(round(rfc[pfx+region+"max_gap_"]/1000,2))+' twh    Curr Gap : '+ (round(rft[pfx+region+"GAP"]/1000,2))+' twh', fontweight ="bold",size=30)
    rfc["ax"].margins(0.01)
    rfc["ax"].pie(rfgout, colors = colors, labels = rfc[pfx+region+'leg_names'],  autopct='%1.1f%%')
    
    create_legend(rfd, rft, rfc, rfg, pfx)
    
    rfc["fig"].canvas.draw()
    rfc["fig"].canvas.flush_events()
    rfc["fig"].show()

    #rfc["plt"].clf()

    return


def gregdisplay(rfd, rft, rfc, rfg, pfx) :
    fn = " Greg Display  "
    # Get the graph colors and fuel names from rfc[pfx+fuel]
    # Any exceptions like graphsmoother ?
    # rfg is a dictionary carrying the key graph params = pfx, region, genfuel, degran, startpos, endpos
    colors = []
    rfgout = []
    # rfg["startpos"] =13158
    # rfg["endpos"] = 13164
    print("INSIDE GREG DISPLAY")
    pfx = rfg["pfx"]
    region = rfg["region"]
    rfc[pfx+region+'leg_names'] = []
    rfc["ax"].clear()
    xaxis = np.arange(0,rfc['FYD'+'elements'],1)
    for fuel in  rfg["genfuel"] :
        colors.append(rfc["FYD"+fuel+"col"])
        rfc[pfx+region+'leg_names'].append(rfc["FYD"+fuel+"fuel_name"])
        #print("graph_display    ", rfg["pfx"], rfg["region"] , rfg["genfuel"], rfg["degran"]  )
        if pfx+region+fuel in rfd.keys() :
            print(fn, "Doing Greg Display Loop Now")
            #graphline = np.cumsum(rfd[pfx+region+fuel])
            rfc["ax"].plot(xaxis,np.cumsum(rfd[pfx+region+fuel]),color = rfc["FYD"+fuel+"col"], label = fuel)
            if rfc["zoom"] == "N" :
                rfgout.append(rfd[pfx+region+fuel].reshape(-1,rfg["degran"]).mean(axis=1))
            else :
                rfgout.append(np.array(rfd[pfx+region+fuel][int(rfg["startpos"]):int(rfg["endpos"])]))
    rfc[pfx+"rfgout"] = rfgout
    rfg["rfgout"] = rfgout
        
    xaxis = np.arange(0, len(rfgout[0]), 1).astype(int)
    
    xtick_vals, xtick_labels = create_xticks(rfd, rft, rfc, rfg, pfx)
    
    rfc["ax"].set_title(f'Supply Gaps '+rfg["region"]+'      Init Gap : '+(round(rfc[pfx+region+"max_gap_"]/1000,2))+' twh    Curr Gap : '+ (round(rft[pfx+region+"GAP"]/1000,2))+' twh', fontweight ="bold",size=30)
    rfc["ax"].set_xticks(xtick_vals)
    rfc["ax"].set_xticklabels(xtick_labels)
    rfc["ax"].margins(0.01)
    rfc["ax"].plot(xaxis,np.cumsum(rfd[pfx+region+"WIN"]),color = rfc["FYD"+"WIN"+"col"])

    #rfc["ax"].stackplot(xaxis,rfgout,colors = colors , alpha=0.9)
    
    create_legend(rfd, rft, rfc, rfg, pfx)

    exs_gap_analyser(rfd, rft, rfc, rfg, pfx)

    reg_fuel_supply_table(rfd, rft, rfc, rfg, pfx)
    
    rfc["fig"].canvas.draw()
    rfc["fig"].canvas.flush_events()
    rfc["fig"].show()

    return


def graphrolling(rfd, rft, rfc, rfg, pfx) :
    # Get the graph colors and fuel names from rfc[pfx+fuel]
    # Any exceptions like graphsmoother ?
    # rfg is a dictionary carrying the key graph params = pfx, region, genfuel, degran, startpos, endpos
    colors = []
    rfgprev = rfg["rfgout]"]
    stuffing = np.array(rfc['FYD'+'elements'],0)
    rfgout = []
    pfx = rfg["pfx"]
    region = rfg["region"]
    rfc[pfx+region+'leg_names'] = []
    for fuel in  rfg["genfuel"] :
        colors.append(rfc["FYD"+fuel+"col"])
        rfc[pfx+region+'leg_names'].append(rfc["FYD"+fuel+"fuel_name"])
        #print("graph_display    ", rfg["pfx"], rfg["region"] , rfg["genfuel"], rfg["degran"]  )
        if pfx+region+fuel in rfd.keys() :
            if rfc["zoom"] == "N" :
                rfgout.append(rfd[pfx+region+fuel].reshape(-1,rfg["degran"]).mean(axis=1))
            else :
                rfgout.append(np.array(rfd[pfx+region+fuel][int(rfg["startpos"]):int(rfg["endpos"])]))
    rfc[pfx+"rfgout"] = rfgout
    rfg["rfgout"] = rfgout
    xaxis = np.arange(0, len(rfgout[0]), 1).astype(int)
    
    xtick_vals, xtick_labels = create_xticks(rfd, rft, rfc, rfg, pfx)
    
    while  len(rfgout) > len(rfgprev) :
        rfgprev.insert(-4, stuffing)
        if len(rfgprev) > 20 :
            return
    
    for fuelline in rfgout :
        pass
    
    rfc["ax"].clear()
    rfc["ax"].set_title('Supply Gap Reporting  '+ rfg["region"], fontweight ="bold",size=11)
    rfc["ax"].set_xticks(xtick_vals)
    rfc["ax"].set_xticklabels(xtick_labels)
    rfc["ax"].margins(0.01)
    rfc["ax"].stackplot(xaxis,rfgout,colors = colors , alpha=0.9)
    
    create_legend(rfd, rft, rfc, rfg, pfx)

    exs_gap_analyser(rfd, rft, rfc, rfg, pfx)

    reg_fuel_supply_table(rfd, rft, rfc, rfg, pfx)
    
    rfc["fig"].canvas.draw()
    rfc["fig"].canvas.flush_events()
    rfc["fig"].show()

    return
