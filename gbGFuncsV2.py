# gbGFuncsV2 - Contains the non storage Functions ie Fixed, New Gas Turbines, Inter Connectors

#from gbUtilsV2 import*
from gbGFStgV2 import storage_calc_totals_remove_stp
from gbGRunV2 import *
from gbBaseV2 import *

from datetime import datetime
import numpy as np
import math
import copy

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports", autocommit = True)
cur_obj = con_obj.cursor()
con_obj.autocommit = True


def gen_destroy(rfd, rft, rfc, rfg, pfx) : # Need to consider IC requests from storage that have been met as these must be reversed. Maybe doesn't matter we have just moved excess from 1 State to another
    fn = "  Gen Destroy   "
    #print(fn, "Start Time  ", datetime.now())
    stp = rfg["stp"]
    for region in rfc["FYD"+"genreg"] :
        if pfx+region+stp in rfd.keys() : del rfd[pfx+region+stp]
        if pfx+region+stp in rft.keys() : del rft[pfx+region+stp]
        if pfx+"ALL"+stp in rfd.keys() : del rfd[pfx+"ALL"+stp]
        if pfx+"ALL"+stp in rft.keys() : del rft[pfx+"ALL"+stp]

        del_list = [key for key in rfd.keys() if key[-3:] not in ('STG','DEM') and (pfx+region+stp in key[:9] or pfx+region+stp in key[:8])]
        for key in del_list :
            del rfd[key]

    if stp in rfc['FYD'+'storage_fuel_list'] : storage_calc_totals_remove_stp(rfd,rft,rfc,rfg,pfx)

    if stp in rfg["genfuel"] :  rfg["genfuel"].remove(stp)
    
    del_list_keys = [key for key in rfc if stp in key and (key[-3:] == 'CAP' or key[-3:] == 'GWO')]
    for key in del_list_keys : del rfc[key]

    if rfc['FYD'+'autorun'] == 'N' : print(fn, "End Time  ", datetime.now())

    rfc[pfx+"ALL"+stp+"done"] = 'N'

    return


def gas_optimizer(rfd,rft,rfc,rfg, pfx) :
    fn = 'NGT and GOC optimisation'
    ''' Function will examine gapexs file to determine where Supply Gaps exceed preceeding Excess such that additional Excess is needed '''
    print(fn, "Start Time  ",  '   ',datetime.now())

    for region in rfc['FYD'+'genreg'] :

        long_gap_data = long_gap_file(rfd,rft,rfc,rfg,pfx, region)

        gap_exs_data = gap_excess_file(rfd,rft,rfc,rfg,pfx, region)

        if gap_exs_data == [] or len(gap_exs_data) <= 2 : continue

        gap_data = [gap for gap in gap_exs_data if gap[5] == 'GAP']
        exs_data = [exs for exs in gap_exs_data if exs[5] == 'EXS']

        both_data = min(len(gap_data), len(exs_data) )

        deficit_data = []

        for i in range(both_data) :
            if (exs_data[i][1] * -1) < gap_data[i][1] * 1.2  :  #### Additional 0.2 due to loss from HPU BAT EVB IHB etc etc
                deficit_data.append(copy.deepcopy(exs_data[i]))
                deficit_data[-1][5] = round(gap_data[i][1] * 1.2 - (exs_data[i][1] * -1),3)

        #print(fn, '   ',region, len(deficit_data), "  ", rfd[pfx+region+'GOC'].sum() / 4 ,)

        stg = rfc[pfx+region+'GOC'+'CAP']

        gof = rfd[pfx+region+'GOC'+'opt_file'] = np.zeros(rfc['FYD'+'elements'])

        for i, deficit in enumerate(deficit_data) :

            gwh = 0
            start = deficit[0] - 2
            length = deficit[2] + 4
            avg_req_gwh = deficit[5] / deficit[2]

            for j in range(int(length)) :

                if avg_req_gwh > stg : gwh = stg
                else : gwh = avg_req_gwh

                gof[start + j] = gwh

        rfd[pfx+region+'GOC'] += gof

        gof[:] = 0

        add_stp_to_rfg_genfuel(rfd,rft,rfc,rfg,pfx,'GOC')

        print(fn, '   ',region, len(deficit_data), "  ", deficit_data[10:15])

        print(fn, 'Extra GOC Applied  ', gof.sum()/4, rfd[pfx+region+'GOC'].sum()/4, rfd[pfx+region+'GOC'][14628:14651])

        calc_totals(rfd,rft,rfc,rfg,pfx)
        graph_display(rfd,rft,rfc,rfg,pfx)

    if rfc['FYD'+'autorun'] == 'N' : print(fn, "End Time  ", datetime.now())


def new_gas_turbines(rfd,rft,rfc,rfg, pfx) :
    fn = " Bring On New Gas Turbines  "
    #print(fn, "Start Time  ", datetime.now())

    #genreg = rfc["FYD"+"genreg"]
    stp = rfg["stp"]
    rfc[pfx+"ALL"+"NGT"+"NEW"] = []
    rfc[pfx+"selected"] = []
    rfc[pfx+"ngt_table_data"] = []

    for region in rfc["FYD"+"genreg"] :
        gap_counter = rfd[pfx+region+"GAP"][96:]
        number_of_ngt = gap_counter.max()  ##### Need to use a bottom 5% rather than lowest figure which is not reflective of reality or requirements

        just_gaps = gap_counter[gap_counter != 0]

        if number_of_ngt != 0 : lowest_95th = np.percentile(just_gaps, 95)
        #
        if number_of_ngt < 0.24999 :
            number_of_ngt = 0
        else :
            number_of_ngt = math.ceil(number_of_ngt)
        print(fn, "Maximum gap which is number of New Gas Turbines ", region,"  ", gap_counter.max(), just_gaps.sum(), 'Lowest 95th  = ', lowest_95th, "No of Gas Turbines = " , number_of_ngt)
        rfc[pfx+"selected"].append([region, stp, stp,number_of_ngt*1000,0,100,10,"S",99999999,stp,'91',25,0,"F",0,0,0,0,"N","L",0])
        rfc[pfx+"ALL"+"NGT"+"NEW"].append(["Number of New 1GW Turbines needed for ", region,"  is ", number_of_ngt, " the cost is $ ", number_of_ngt * 1.25, "bn"])
        rfc[pfx+"ngt_table_data"].append([region, stp, "New","Gas Turbine Peakers", "9999999", number_of_ngt, 0, number_of_ngt*1000, number_of_ngt * 1.25, "L", 0])
        rfc[pfx+"ngt_header"] = ['Select', 'Region', 'Type', 'Code', 'Name', 'Fuel', 'Qty x GWs','Loss %', 'Out MWHs', '$bn Cost', 'Status', 'sqlid']
        rfc[pfx+"ngt_title"] = "  New Gas Turbines to be Built to Ensure Supply   "
        rfc[pfx+"ngt_width"] = [8,8,8,8,20,8,8,8,8,8,6,6]

        cur_obj.execute('update gbstg set gwout = %s, qty = %s  where genfuel = %s and genregion = %s',[number_of_ngt*1000, number_of_ngt, stp, region])
        con_obj.commit()

    if rfc['FYD'+'autorun'] == 'N' : print(fn, "Endtime  ", datetime.now(), "NGT data to go to BO Stg   ", rfc[pfx+"selected"])
    rfc[pfx+"ALL"+stp+"done"] = "Y"
    return


def interconnect_runner(rfd, rft, rfc, rfg, pfx) :
    fn = " Bring On IC Lines  "
    # Goes through each state and when a gap asks other states to send energy - The IC lines are held in gbic and ordered by nearest neighbour with biggest IC connection
    #print("Start  Interconnectors ", datetime.now())
    con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
    cur_obj = con_obj.cursor()

    ic_type = rfc["ic_type"] # Currently either I, B, S or T
    cur_obj.execute("SELECT region, oth_reg, ic_code, ic_gwh, loss, legs, status, ic_name, cap_cost, route, sqlid  FROM gbic where status = 'L' order by status, legs, region")
    ic_order = cur_obj.fetchall()

    for regic in ic_order :

        if regic[3] == 0 : continue
        region = regic[0]
        oth_reg = regic[1]
        ic_code = regic[2]
        ic_gwh = round(int(regic[3])/1000,3)
        loss = int(regic[4])
        maxcap = np.full(rfc["FYD"+"elements"], ic_gwh)

        rfd[pfx+region+ic_code[:2]+ic_type] = np.zeros(rfc["FYD"+"elements"])

        if ic_type == "B" : tfr_req = np.minimum(rfd[pfx+oth_reg+"EXS"]*-1, np.array(rfd[pfx+region+rfg["stp"]+"REQ"])) # tfr_req is the transfer request
        else : tfr_req = np.minimum(rfd[pfx+oth_reg+"EXS"]*-1, rfd[pfx+region+"GAP"]) # tfr_req is the transfer request and is +ve numbers

        # Book the transfer onto the Interconnector can be multiple and need to check capcity else tfr reduced
        if regic[5] == 1 :
            ic_cap_taken = copy.deepcopy(rfd[pfx+region+ic_code[:2]+ic_type])
            ic_cap_taken[ic_cap_taken < 0] = ic_gwh # If a negative then I cannot book on to line hence capacity set to max which = taken.
            ic_cap_avail = np.array(maxcap - ic_cap_taken)
            tfr_bkd = np.minimum(ic_cap_avail, tfr_req) # gives a +ve - Note - new = np.minimum(x, np.maximum(y,0)) will manage -ve numbers so a zero is returned as the minimum

            # Add tfr_bkd to line for later availability and update GAP and EXS
            rfd[pfx+region+ic_code[:2]+ic_type] = np.array(rfd[pfx+region+ic_code[:2]+ic_type]) + tfr_bkd*(100-loss)/100 # Wrong place for loss should be applied at end to the HVI line when added
            rfd[pfx+region+"availicexs"] = np.minimum(rfd[pfx+oth_reg+"EXS"]*-1, maxcap) - tfr_bkd
            rfd[pfx+region+"GAP"] = rfd[pfx+region+"GAP"] - tfr_bkd*(100-loss)/100
            rfd[pfx+oth_reg+"EXS"] += tfr_bkd

            # switch code to dispatching line and book dispatch onto their line
            opp_ic_code = ic_code[1]+ic_code[0]
            if pfx+oth_reg+opp_ic_code[:2]+ic_type not in rfd.keys() : rfd[pfx+oth_reg+opp_ic_code[:2]+ic_type] = np.zeros(rfc["FYD"+"elements"])
            rfd[pfx+oth_reg+opp_ic_code[:2]+ic_type] = rfd[pfx+oth_reg+opp_ic_code[:2]+ic_type] - tfr_bkd

            # add the line to a totals in the region for inc. in calc_totals and gapexs calcs
            if pfx+region+"HVI" not in rfd.keys() : rfd[pfx+region+"HVI"] = rfd[pfx+region+ic_code[:2]+ic_type]
            else : rfd[pfx+region+"HVI"] = rfd[pfx+region+"HVI"] + tfr_bkd

            if pfx+oth_reg+"HVI" not in rfd.keys() : rfd[pfx+oth_reg+"HVI"] = rfd[pfx+oth_reg+opp_ic_code[:2]+ic_type]
            else :  rfd[pfx+oth_reg+"HVI"] = rfd[pfx+oth_reg+"HVI"] - tfr_bkd

    add_stp_to_rfg_genfuel(rfd,rft,rfc,rfg,pfx, 'HVI')

    rfc[pfx+"ALL"+"HVI"+"done"] = "Y" # Set flag to show Interconnectors are on

    if rfc['FYD'+'autorun'] == 'N' : print("End  Interconnectors ", datetime.now())

    return


def fixed_fuel_runner (rfd, rft, rfc, rfg, pfx) :
    fn = "Fixed Asset Generation   "
    # This will use gbfix to read fixed assets and will then bring them on a mininimum output. After calculating gaps with them at minimum they are reviewed again for max output and
    # response times. They are processed first by Ord then default to resptime (quickest first). After each Fixed Asset responds the gaps are NOT recalculated before the next one responds.
    if rfc['FYD'+'autorun'] == 'N' : print(fn, "   start  ", datetime.now())
    cur_obj.execute('select genfuel from gbfix where status = "L" group by genfuel')
    fixlist = list(cur_obj.fetchall())
    rfc[pfx+"fixlist"] = []
    for fix in fixlist :
        rfc[pfx+"fixlist"].append(fix[0])

    #helpline = "                  0        1         2       3       4        5       6         7       8      9       10      11  "
    cur_obj.execute(" select genregion, genfuel, gencode, genname, respmin, respmax, respup, respdown, gwhout, gwcost, status, sqlid from gbfix where status = 'L' and gwhout != 0 order by genregion, genfuel, ord, gencode")
    fixedgens = cur_obj.fetchall()
    if fixedgens == [] :
        return
    resp_steps = np.zeros(rfc["FYD"+"elements"])

    for fuel in rfc[pfx+"fixlist"] : 
        for region in rfc["FYD"+"genreg"] :
            for gen in fixedgens :
                if region != gen[0] or fuel != gen[1] :
                    continue
                
                if pfx+region+fuel+'GWO' not in rfc : rfc[pfx+region+fuel+'GWO'] = 0
                if pfx+'ALL'+fuel+'GWO' not in rfc : rfc[pfx+'ALL'+fuel+'GWO'] = 0

                resp_inc = 0
                ger_data = []
                gcd = gen[2]
                minout = round(float(gen[4]) / 100 * float(gen[8])/1000,3)
                maxout = rfc[pfx+region+fuel+gcd+'GWO'] = round(float(gen[5]) / 100 * float(gen[8])/1000,3)
                rfc[pfx+region+fuel+'GWO'] += rfc[pfx+region+fuel+gcd+'GWO']  #### Storing Gen GW Capacity for use in costing
                rfc[pfx+'ALL'+fuel+'GWO'] += rfc[pfx+region+fuel+gcd+'GWO']
                resp_count = math.ceil(int(gen[6]) /15) # Dont hard code 15 should derive from elements - gives nos of elements to respond
                if resp_count < 1 : resp_count = 1
                resp_gwh = round((maxout - minout) / resp_count,6)
                fuel = gen[1]
                gen_min = np.full(rfc["FYD"+"elements"], minout)
                svd_file = np.array(rfd[pfx+region+"SVD"]) - gen_min
                #new_svd = svd_file - gen_min

                # Created is a gaps file which is now processed for base load responses Up / Stay Up / Down / Stay Down
                ger_data = gap_excess_file(rfd,rft,rfc,rfg,pfx, region, svd_file = svd_file)
                

                for i, ger in enumerate(ger_data) :
                    if ger[1] > 0 :
                        if ger[1] > rft[pfx+"ALL"+fuel] : # WHAT DOES THIS LINE DO ? WAS "ALL" NOT REGION B4. The "ALL" determines that the response is to National gaps not region gaps ???? Needs thinking cos of Inter Connectors
                            if ger[0] > resp_count :
                                resp_inc = resp_gwh
                                if resp_steps[ger[0] - resp_count] !=0 :
                                    resp_inc = resp_steps[ger[0] - resp_count]
                                for i in range(resp_count) :
                                    if resp_steps[ger[0] - resp_count + i] == 0 :
                                        resp_steps[ger[0] - resp_count + i] = resp_inc
                                        if resp_inc < maxout - minout :
                                            resp_inc += resp_gwh
                                    elif  resp_inc + resp_gwh >= maxout - minout :
                                        resp_steps[ger[0] - resp_count + i] = maxout - minout
                                        resp_inc = maxout - minout
                                    else :
                                        resp_steps[ger[0] - resp_count + i] = resp_inc + resp_gwh
                                        resp_inc = resp_inc + resp_gwh
                                for i in range(ger[2]) :
                                        resp_steps[ger[0]+i] = maxout - minout
                                        resp_inc = maxout - minout
                                for i in range(resp_count) :
                                    if i + ger[3] < rfc["FYD"+"elements"] :
                                        resp_inc = resp_inc - resp_gwh
                                        resp_steps[ger[3] + i] = resp_inc
                                resp_inc = 0
                #svd_file = new_svd - resp_steps
                rfd[pfx+region+"SVD"] = copy.deepcopy(svd_file - resp_steps)

                rfd[pfx+region+fuel+gcd] = gen_min + resp_steps
                rft[pfx+region+"ALL"+"FIX"] += rfd[pfx+region+fuel+gcd].sum()/4
                if pfx+region+fuel in rfd.keys() : rfd[pfx+region+fuel] += rfd[pfx+region+fuel+gcd]
                else : rfd[pfx+region+fuel] = rfd[pfx+region+fuel+gcd]
                
                resp_steps[:len(resp_steps)] = 0

                add_stp_to_rfg_genfuel(rfd,rft,rfc,rfg,pfx, fuel)
                
                # if fuel not in rfc[pfx+region+"genfuel"] :
                #     rfc[pfx+region+"genfuel"].insert(0,fuel)
                # if pfx+"region" in rfc.keys() :
                #     if region == rfc[pfx+"region"] and fuel not in rfg["genfuel"] :
                #         rfg["genfuel"].insert(0, fuel)
                #     if rfc[pfx+"region"] == "ALL" :
                #         if fuel not in rfg["genfuel"] :
                #             rfg["genfuel"].insert(0, fuel)

        calc_totals(rfd, rft,  rfc, rfg, pfx) # These are here to recalculate gaps between Coal then Gas

        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)  #### READ ABOVE BEFORE REMOVING  #####

    rfc[pfx+"ALL"+"FIX"+"done"] = "Y"
    if rfc['FYD'+'autorun'] == 'N' : print("End Fixed", datetime.now())

    # for key in rfc :
    #     if key[-3:] == 'CAP' :
    #         print (key, '     ', rfc[key])
    
    return



