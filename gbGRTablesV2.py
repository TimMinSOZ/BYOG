# gbGRTablesV2

# gbgraphrunV2 # move all the functions running the graph to here ie display, legend, tables, create_xtick_s

import numpy as np
#import sys
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
#from matplotlib.widgets import Button
from datetime import datetime

from gbUtilsV2 import*
from gbGRButV2 import *


def build_table_append_to_graph(rfd, rft, rfc, rfg, pfx, tot_table_data, row_labels, col_labels) :
    
    rf_table = rfc["plt"].table(cellText=tot_table_data,   #  tot_table_data,
                                rowLabels=row_labels,
                                rowColours=["Lightgreen"] * len(row_labels),
                                colColours=["Lightgreen"] * len(col_labels),
                                cellColours=[["white"] * len(col_labels)] * len(row_labels),
                                colLabels=col_labels,
                                colWidths = np.full(len(col_labels), round(rfg["graph_table_size"] * 0.006,3)),
                                cellLoc = 'right',
                                loc='upper center', zorder = 9)
    rf_table.scale(1, round(rfg['rf_cost_table_size'] / 9,1))
    rf_table.auto_set_font_size(False)
    rf_table.set_fontsize(rfg['rf_cost_table_size'])
    for cell in rf_table._cells:
        rf_table._cells[cell].set_alpha(0.8)  
        rf_table._cells[cell].set_text_props(fontproperties = font_manager.FontProperties(weight = rfg['graph_table_bold'], style = 'normal', size = rfg['rf_cost_table_size']))  

    print(' Graph Table Built and Returned')
    return rf_table

def reg_fuel_supply_table(rfd, rft, rfc, rfg, pfx) :
    fn = "  Create Graph Region by Fuel Table  "
    # Creates a output rf_table containing the data to create the table when called by plt.table() 
    # Table is region by fuel with GWS and Totals at the bottom
    #print(fn,'Start  ', datetime.now())
    tot_fuels = []
    tot_table_data = []
    row_labels = []
    for region in rfc[pfx+"genreg"] :
        col_labels = []
        table_row = []
        tot_fuels = []
        for fuel in rfc[pfx+"ALL"+"genfuel"][:-4] :
            col_labels.append(fuel)
            if pfx+region+fuel in rfd : table_row.append(f"{round(rfd[pfx+region+fuel].sum() / 4) :,d}")
            else : table_row.append("0")
            if pfx+'ALL'+fuel in rfd : tot_fuels.append(f"{round(rfd[pfx+'ALL'+fuel].sum() / 4) :,d}")
            else: tot_fuels.append("0")
        table_row.append(f"{round(rfd[pfx+region+'ALL'].sum() / 4) : ,d}")
        col_labels.append("Supply")
        table_row.append(f"{round(rfd[pfx+region+'DEM'].sum() / 4) :,d}")
        col_labels.append("Demand")
        table_row.append(f'{round((rfd[pfx+region+"ALL"].sum() / 4) / (rfd[pfx+region+"DEM"].sum() / 4) * 100)}% ')
        col_labels.append("Sup / Dem")
        row_labels.append(region)
        tot_table_data.append(table_row)
        
    if pfx+'ALL'+'ALL' in rfd : tot_fuels.append(f"{round(rfd[pfx+'ALL'+'ALL'].sum() / 4) :,d}")
    else: tot_fuels.append("0")
    if pfx+'ALL'+'DEM' in rfd : tot_fuels.append(f"{round(rfd[pfx+'ALL'+'DEM'].sum() / 4) :,d}")
    else : tot_fuels.append("0")
    tot_fuels.append(f"{round(round(rfd[pfx+'ALL'+'ALL'].sum() / 4) / round(rfd[pfx+'ALL'+'DEM'].sum() / 4) * 100)}%")
    tot_table_data.append(tot_fuels)
    row_labels.append("Totals")
    if rfg["graph_table"] == "Y" :
        rf_table = build_table_append_to_graph(rfd, rft, rfc, rfg, pfx, tot_table_data, row_labels, col_labels)
    
    return

def grid_build_and_run_costs(rfd, rft, rfc, rfg, pfx, region, fuel, request) :
        
    GWH_output = rfd[pfx+region+fuel].sum()/4
    GW_capacity = 0
    GWH_storage = 0  
    
    cur_obj.execute('select cap_kwh, oam_fix, oam_mwh, fuel_mwh, lcoe_L, lcoe_C, util_pc, CO2_kg, C_cap from gbgenfuel where code = %s ', [fuel])
    rf_costset = cur_obj.fetchone() 
    cap_kwh = rf_costset[0]
    oam_fix = rf_costset[1]
    oam_mwh = rf_costset[2]
    fuel_mwh = rf_costset[3]
    lcoe_l = rf_costset[4]
    lcoe_c = rf_costset[5]
    util_pc = rf_costset[6]
    co2_kg = rf_costset[7]  
    C_cap = rf_costset[8]
    
    if util_pc == 100 : 
        if request == 'total' : return  0
        if request == 'sub_total' :  return  0, 0, 0, 0, 0, 0, 0, 0
        if request in ('L_lcoe', 'C_lcoe') : return  0
        if request == 'compare' : return 0, 0, 0, 0, 0, 0
        
#######     We now have p+r+f+g+'CAP' to get rf storage from  ***** BAT - IHB - EVB - EVG ****** HVI -> cancel at start not zeroes, HYD OK, HPU by site + running costs  ######

    if fuel in rfc['FYD'+'renfuel'] : GW_capacity = round(GWH_output / (365 * 24 * util_pc / 100),1)
    elif pfx+region+fuel+'GWO' in rfc : GW_capacity = rfc[pfx+region+fuel+'GWO']
            
    
    if fuel in rfc['FYD'+'storage_fuel_list'] and pfx+region+fuel+'CAP' in rfc :  GWH_storage = rfc[pfx+region+fuel+'CAP']
    
    if fuel == 'HPU' : 
        cur_obj.execute('select round(sum(gwcost)), round(sum(storage)/1000) from gbstg where genfuel = "HPU" and status = "L" group by genfuel')
        HPU_info = cur_obj.fetchone()
        HPU_cost = HPU_info[0]
        GWH_storage = HPU_info[1]
        C_cap = HPU_cost /  GWH_storage
            
    build_cost = round(GW_capacity * cap_kwh) #### $ Millions - built from cap_kwh which need a single source of data and labelling
    oam_fix_kw = round(GW_capacity * oam_fix) #### $ Millions
    oam_var_mwh = round(GWH_output * oam_mwh / 1000) ### $ Millions
    fuel_cost = round(GWH_output * fuel_mwh / 1000) ### $ millions
    carbon_cost =  round(GWH_output /1000000 * co2_kg * rfc[pfx+'carbon_cost']) ### $Millions
    L_lcoe = round(GWH_output * lcoe_l / 1000)  ###### $ Millions - Lazards is an all in cost per MWH - so cost to produce GWH_output
    if fuel in rfc['FYD'+'storage_fuel_list'] : C_cap_cost = round(GWH_storage * C_cap)  ##### $Millions CSIRO - This cost is the capital cost in Australia
    else : C_cap_cost = round(GW_capacity * C_cap)
    C_lcoe =  round(GWH_output * lcoe_c / 1000)  #####  CSIRO - This cost is the LCOE in Australia - so more relevant than Lazards
    annual_cost = round(oam_fix_kw + oam_var_mwh + fuel_cost + carbon_cost) ### + carbon_cost

    if request == 'total' : return  C_cap_cost
    if request == 'sub_total' : return  GWH_storage, GW_capacity, C_cap_cost, oam_fix_kw, oam_var_mwh, fuel_cost, carbon_cost, annual_cost
    if request == 'L_lcoe' : return  L_lcoe
    if request == 'C_lcoe' : return C_lcoe
    if request == 'compare' : return  round(GWH_storage), round(GW_capacity,1), C_cap_cost, annual_cost, L_lcoe, C_lcoe

def reg_fuel_cost_table(rfd, rft, rfc, rfg, pfx) :
    fn = " Builds a Region by Fuel - New Build / Annual running costs / lcoe_l, lcoe_C Table  "
    # Creates a Region x Fuel table with Totals containing the GWH and called by plt.table() 
        
    tot_table_data = []
    temp_fuel_totals = []
    row_labels = []
    col_labels = []
    rf_temp = {}
    tot_region_cost = 0
    tot_region_fuel_cost = 0
    
    if rfg['table_request'] in ('total','L_lcoe', 'C_lcoe') :
    
        for region in rfc[pfx+"genreg"] :
            table_row = []
            tot_region_cost = 0
            for fuel in rfg['genfuel'][:-4] :
                if fuel == 'HVI' : continue
                if 'total_cost'+fuel not in rf_temp : rf_temp['total_cost'+fuel] = 0
                
                if pfx+region+fuel in rfd :
                    #print('  RF Total  ', grid_build_and_run_costs(region, fuel, request = rfg['table_request']))
                    rf_total = int(grid_build_and_run_costs(rfd, rft, rfc, rfg, pfx, region, fuel, request = rfg['table_request']))
                    table_row.append(f'{rf_total :,d}')
                else : 
                    rf_total = 0
                    table_row.append(f'{rf_total :,d}')
                
                tot_region_cost += rf_total
                rf_temp['total_cost'+fuel] += rf_total
                
            table_row.append(f'{tot_region_cost :,d}')
                
            row_labels.append(region)
            tot_table_data.append(table_row)
            
        row_labels.append("Totals")
        
        ###### Add column totals ######
        for fuel in rfg['genfuel'][:-4] :
            if fuel == 'HVI' : continue
            col_labels.append(f'{fuel}')
            temp_fuel_totals.append(f'{int(rf_temp["total_cost"+fuel]) :,d}')
            tot_region_fuel_cost += rf_temp["total_cost"+fuel]
            
        col_labels.append(f'Total $m')
        temp_fuel_totals.append(f'{int(tot_region_fuel_cost) :,d}')
        tot_table_data.append(temp_fuel_totals)
        
    if rfg['table_request'] == 'sub_total' :  #### Can turn this into a per region response and should do this #####
        
        table_col = []
        row_labels = ['GWH_storage', 'GW_capacity', 'build_cost', 'oam_fix_kw', 'oam_var_mwh', 'fuel_cost', 'carbon_cost', 'Annual_Cost']
        
        for fuel in rfg['genfuel'][:-4] :
            if fuel == 'HVI' : continue
            col_labels.append(f'{fuel}')
            
            if pfx+'ALL'+fuel in rfd :
                print('  Break Down Return =   ', grid_build_and_run_costs(rfd, rft, rfc, rfg, pfx, 'ALL', fuel, request = rfg['table_request']))
                table_col.append(list(grid_build_and_run_costs(rfd, rft, rfc, rfg, pfx, 'ALL', fuel,  request = rfg['table_request'])))
            else : 
                table_col.append([0] * len(row_labels))
             
        
        #### Add the totals column at the last row
        
        table_col.append([0] * len(row_labels))  #### Added as place marker for Total column
        print(table_col) 
        temp_table_data = np.transpose(table_col)
        print(temp_table_data)
        for i, row in enumerate(temp_table_data) :
            row_total = 0  
            for number in row : 
                row_total += int(number)
            temp_table_data[i][-1] = row_total
            tot_table_data.append([f'{cell :.1f}' for cell in temp_table_data[0]] if i == 0 else [f'{int(cell) :,d}' for cell in row])
                              
        col_labels.append(' Total  $mil ')
        #for label in row_label_list : row_labels.append(label)
        print(tot_table_data) 
        print(len(col_labels),  len(row_labels)) 
        
    rfg['rf_table'] = build_table_append_to_graph(rfd, rft, rfc, rfg, pfx, tot_table_data, row_labels, col_labels)
    
    return rfg['rf_table']

def grid_cost_compare_table(rfd, rft, rfc, rfg, pfx) :  #### What should be shared and how via functions ????  ####
    fn = 'Grid Cost Compare Table'
    if rfg['pfx'] == '' : return
    pfx1 = rfg['pfx1']
    pfx2 = rfg['pfx2']
    
    #### Combine the two fuel lists and eliminate duplicates and sort via fuelsort and remove last 4 NON fuels at the end  ####
    compare_fuel_list = fuelsort(rfd, rft, rfc, rfg, pfx, rfc[pfx1+'ALL'+'genfuel'] + list(set(rfc[pfx2+"ALL"+"genfuel"]) - set(rfc[pfx1+"ALL"+"genfuel"])))[:-4]
            
    #print(fn, 'Combined List = ' , compare_fuel_list, rfc[pfx1+"ALL"+"genfuel"], rfc[pfx2+"ALL"+"genfuel"])
    
    row_labels = []
    compare_table = []
    compare_table_row = []

    for fuel in compare_fuel_list :
        row_labels.append(f'{fuel} - {rfc["FYD"+fuel+"fuel_name"]}')
        
        for pfx in [pfx1, pfx2] :
        
            GWH_output = round(rfd[pfx+'ALL'+fuel].sum()/4)
            
            GWH_storage, GW_capacity, C_cap_cost, annual_cost, L_lcoe, C_lcoe = grid_build_and_run_costs(rfd, rft, rfc, rfg, pfx, 'ALL', fuel, rfg['rf_table_request'])
            
            print('from compare function  ', fuel, GWH_storage, GW_capacity,'    ', C_cap_cost, annual_cost, L_lcoe, C_lcoe, '    ',GWH_output, pfx1, pfx2)
            
            if rfg['rf_compare_request'] == len(rfg['rf_compare_options']) -1 : compare_value = 0
            if rfg['rf_compare_request'] == 0 : compare_value = C_cap_cost
            if rfg['rf_compare_request'] == 1 : compare_value = annual_cost
            if rfg['rf_compare_request'] == 2 : compare_value = L_lcoe
            if rfg['rf_compare_request'] == 3 : compare_value = C_lcoe
            if rfg['rf_compare_request'] == 4 : x = 0 # How to do a set of 4 totals without re-writing it all
            
            compare_table_row += [GW_capacity, compare_value]
        
        compare_table_row += [round(compare_table_row[0] - compare_table_row[2],1), round(compare_table_row[1] - compare_table_row[3])]
        
        if compare_table_row[3] != 0 : compare_pc = round((compare_table_row[1] - compare_table_row[3]) / compare_table_row[3] * 100)
        else : compare_pc = 0
        compare_table_row += [compare_pc]
        compare_table.append(compare_table_row)
        compare_table_row = []
    
    ##### Last Section is for totals at the base of the table  
    col_total = 0
    for i in range(len(compare_table[0])) : ### Cols
        for j in range(len(compare_table)) :  ### Rows 
            col_total += compare_table[j][i]
        compare_table_row += [col_total]
        col_total = 0
    
    ###### Final Corner where %age cannot be totalled so re-worked from Totaled Costs  ####
    if compare_table_row[3] != 0 : col_total = round((compare_table_row[1]- compare_table_row[3]) / compare_table_row[3] * 100)
    else : col_total = 0
    compare_table_row[-1] = col_total 
    compare_table.append(compare_table_row)
    row_labels.append(f'{pfx1} vs {pfx2} Totals')
    
    #### Run a formatter through the columns getting them tidied up ####
    for row in compare_table:
        for i in range(len(row)):
            if i == 0 or i == 2 or i == 4 : row[i] = f'{row[i] :.1f}'
            elif i == len(row) - 1 : row[i] = f'{row[i] :.0f}%'
            else : row[i] = f'{row[i] :,d}'
            
        print(row)
    
    col_labels = ['GWs', 'Cost', 'GWs', 'Cost', 'GW Diff ', 'Cost Diff ', 'Diff %']
    if rfg['rf_table_totals'] == [] : rfg['rf_table_totals'].append(col_labels)
    rfg['rf_table_totals'].append(compare_table[-1])
    
    if rfg['rf_table_request'] != 'compare_totals' : rfg['rf_table'] = build_table_append_to_graph(rfd, rft, rfc, rfg, pfx, compare_table, row_labels, col_labels)
    if rfg['rf_compare_request'] == len(rfg['rf_compare_options']) - 1 : rf_table.remove()  ### User selected to Exit  ###

    print(fn, compare_table)
    print(fn, 'Finish  ', datetime.now())
    
    return rfg['rf_table']

def totals_summary_table(rfd, rft, rfc, rfg, pfx) :
    fn = " Totals Summary Table  "
    "Create a summary table of the totals for the selected region is a future"
    #print(fn, 'Start  ', datetime.now())
    
    rfg['rf_table_totals'] = []
    for i in range(len(rfg['rf_compare_options']) - 1) :
        
        rfg['rf_table_request'] = 'compare'
        rfg['rf_compare_request'] = i
        grid_cost_compare_table(rfd, rft, rfc, rfg, pfx)
        
    col_labels = rfg['rf_table_totals'][0]
    
    compare_table = rfg['rf_table_totals'][1:]
    
    row_labels = []
    for i in range(len(compare_table)) :
        row_labels.append(rfg['rf_compare_options'][i])
        
    rfg['rf_table_summary'] = build_table_append_to_graph(rfd, rft, rfc, rfg, pfx, compare_table, row_labels, col_labels)
    
    print(rfg['rf_table_totals'])
    
    return rfg['rf_table_summary']





def exs_gap_analyser(rfd, rft, rfc, rfg, pfx) :
    fn = " exs_gap_analyser  "
    "Analyse Exs and Gap Data for Deepest, Longest, Largest then  Average for Depth Length GWH"
    #print("Start exs_gap_analyser  ", datetime.now())
    graphgap = []
    graphexs = []
    if np.array(rfd[pfx+rfg["region"]+"SVD"]).sum() != 0 :
        gap_gwh = gap_time = gap_depth = exs_gwh = exs_time = exs_depth = 0
        max_gap_gwh = max_gap_depth = max_gap_time = max_exs_gwh = max_exs_depth = max_exs_time = 0
        tot_gap_gwh = tot_gap_depth = tot_gap_time = tot_exs_gwh = tot_exs_depth = tot_exs_time = 0
        gap_count = exs_count = -1
        gap_start = exsstart = -1
        exscont = "Closed"
        gapcont = "Closed"
        if rfg["startpos"] > rfg["endpos"] :
            print("exs_gap_analyser wierd figures in rfg[startpos] and rfg [endpos]" , rfg["startpos"], rfg["endpos"], rfg["region"])
        for i in range(rfg["startpos"] + 1, rfg["endpos"]) : 
            txn_gwh = round(float(rfd[pfx+rfg["region"]+"SVD"][i]),3)
            if txn_gwh > 0 :
                if exscont == "Open" :
                    exs_gwh = exs_gwh * - 1 # Make positive figure before closing
                    exs_depth = exs_depth * -1 
                    if exs_gwh > max_exs_gwh :
                        max_exs_gwh = exs_gwh 
                        max_exs_gwhrec = [exsstart, exs_time, round(exs_depth,1), round(exs_gwh)]
                    if exs_time > max_exs_time :
                        max_exs_time = exs_time
                        max_exs_timerec = [exsstart, exs_time, round(exs_depth,1), round(exs_gwh)]
                    if exs_depth > max_exs_depth :
                        max_exs_depth = exs_depth
                        max_exs_depthrec = [exsstart, exs_time, round(exs_depth,1), round(exs_gwh)]
                    exs_time=exs_gwh=exs_depth= 0
                    exsstart = -1
                    exscont = "Closed"
                gap_gwh = gap_gwh + txn_gwh/4
                gap_time = gap_time + 0.25 # Shouldn't hard code so will update later
                if txn_gwh > gap_depth :
                    gap_depth = txn_gwh
                if gap_start == -1 :
                    gap_start = i
                    gap_count = gap_count + 1
                    gapcont = "Open"
                tot_gap_gwh = tot_gap_gwh + txn_gwh/4
                tot_gap_depth = tot_gap_depth + txn_gwh/4
                tot_gap_time = tot_gap_time + 0.25
                    
            if txn_gwh < 0 :
                if gapcont == "Open" :
                    datefp = date_obj_from_position(gap_start+1) # Should do this at the end as faster
                    #gap_start = (datefp.day)+"/"+(datefp.month)+"  "+(datefp.hour)+":"+(datefp.minute)
                    gap_start = f'{datefp.day}/{datefp.month}  {datefp.hour}:{datefp.minute}'
                if gap_gwh > max_gap_gwh :
                    max_gap_gwh = gap_gwh
                    max_gap_gwhrec = [gap_start, gap_time, round(gap_depth,1), round(gap_gwh)]
                if gap_time > max_gap_time :
                    max_gap_time = gap_time
                    max_gap_timerec = [gap_start, gap_time, round(gap_depth,1), round(gap_gwh)]
                if gap_depth > max_gap_depth :
                    max_gap_depth = gap_depth
                    max_gap_depthrec = [gap_start, gap_time, round(gap_depth,1), round(gap_gwh)]
                gap_time=gap_gwh=gap_depth= 0
                gap_start = -1
                gapcont = "Closed"
                exs_gwh = exs_gwh + txn_gwh/4
                exs_time = exs_time + 0.25
                if txn_gwh < exs_depth :
                    exs_depth = txn_gwh
                if exsstart == -1 :
                    exsstart = i
                    exs_count = exs_count + 1  
                    exscont = "Open"
                tot_exs_gwh = tot_exs_gwh + txn_gwh/4
                tot_exs_depth = tot_exs_depth + txn_gwh/4
                tot_exs_time = tot_exs_time + 0.25

        #print("gap_count   ", gap_count,"   ", exs_count, "tot_gap_ time  " , tot_gap_time,"    ", tot_exs_time, "+++++++++++++++++++++++++++++++++++++++++++++++")
        if gap_count != 0 and tot_gap_time != 0 :   
            avggap_gwh = round(float(tot_gap_gwh/gap_count))
            avggap_time = round(float(tot_gap_time/gap_count),1) 
            avggap_depth = round(float(tot_gap_depth/(tot_gap_time)),1)

            graphgap.append(max_gap_gwhrec)
            graphgap.append(max_gap_depthrec)
            graphgap.append(max_gap_timerec)
            graphgap.append([str(gap_count)+" Gaps",avggap_time, avggap_depth, avggap_gwh])
            #print ("Tots prior to average", tot_gap_gwh," depth  " ,tot_gap_depth," time   ", tot_gap_time)
            
        if exs_count != 0 and tot_exs_time != 0 :
            avg_exs_gwh = round(float(tot_exs_gwh/exs_count*-1))
            avg_exs_time = round(float(tot_exs_time/exs_count),1)
            avg_exs_depth = round(float(tot_exs_depth/tot_exs_time*-1),1)

            graphexs.append(max_exs_gwhrec)
            graphexs.append(max_exs_depthrec)
            graphexs.append(max_exs_timerec)
            graphexs.append([str(exs_count)+" Excess",avg_exs_time, avg_exs_depth, avg_exs_gwh])
        
        #print(fn," Anything in EXS file   ", graphexs,"   or anything in graphGAP   ", graphgap) 
        
        colwidths = [rfg['graph_analysis_table_size']*0.005] + [rfg['graph_analysis_table_size']*0.004 for i in range(3)]

        if len(graphgap) != 0 and rfg['graph_analysis_table'] == "Gap" : 
            gap_table = plt.table(cellText=graphgap,
                                    rowLabels=['Largest', 'Deepest','Longest','Average'],
                                    rowColours=["tomato"]*4,
                                    colLabels=('Date & Time','Hours', 'Depth', 'GWHs'),
                                    cellColours = [["w","w","w","r"],["w","w","r","w"],["w","r","w","w"],["w","w","w","w"]],
                                    colWidths = colwidths,
                                    cellLoc = 'right',
                                    loc='upper right', zorder = 9)
            gap_table.scale(1, round(rfg['graph_analysis_table_size'] / 9,2))
            gap_table.auto_set_font_size(False)
            gap_table.set_fontsize(rfg['graph_analysis_table_size'])
            for cell in gap_table._cells:
                gap_table._cells[cell].set_alpha(0.8)            

        elif len(graphexs) != 0 and rfg['graph_analysis_table'] == "Excess" :
            
            exs_table = plt.table(cellText=graphexs,
                                    rowLabels=['Largest', 'Highest','Longest','Average'],
                                    rowColours=["lightgreen"]*4,
                                    colLabels=['Date & Time','Hours', 'Height', 'GWHs'],
                                    cellColours = [["w","w","w","g"],["w","w","g","w"],["w","g","w","w"],["w","w","w","w"]],
                                    colWidths = colwidths,
                                    cellLoc = 'right',
                                    loc='upper right', zorder = 9)
            exs_table.scale(1, round(rfg['graph_analysis_table_size'] / 9,2))
            exs_table.auto_set_font_size(False)
            exs_table.set_fontsize(rfg['graph_analysis_table_size'])
            for cell in exs_table._cells:
                exs_table._cells[cell].set_alpha(0.8)            

#colWidths = [0.05,0.04,0.04,0.04]
    
    #print("End exs_gap_analyser  ", datetime.now())
    return