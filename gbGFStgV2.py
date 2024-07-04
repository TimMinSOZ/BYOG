#gbGFStgV2 Contains all the Graph Functions which are Storage Based

import numpy as np
from numba import jit
import copy
from datetime import datetime

from gbUtilsV2 import*
from gbBaseV2 import*
#from gbGFuncsV2 import gen_destroy

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports", autocommit = True)
cur_obj = con_obj.cursor()
con_obj.autocommit = True


def load_inflow_up(max_stg,  stg, stg_view, inflow_view, bat_stg_view) :
    ### Inflow will one day be a annual np.array of the average ie 35040 pts. It won't be a single figure as it is now so we process as if a np.array """"
    
    for i in  range(len(inflow_view)) :
        
        if max_stg - stg > inflow_view[i]  :
            stg_view[i] = -inflow_view[i]
            stg += inflow_view[i] / 4
            bat_stg_view[i] = stg
        
        else : 
            stg_view[i] = (max_stg - stg)
            stg = max_stg
            bat_stg_view[i] = stg

            return stg
    
    return stg

def load_stg_up(max_stg, stg, gwi, loss, svd_view, stg_view, loss_view, bat_stg_view) :   #### Takes from Excess in svd_view amd gives to stg_view
    fn = ' Load Stg_up   '
    if svd_view.sum() == 0 : 
        print(fn,'  Gapfile is ZERO and no excess in it  ', svd_view, 'why empty ' )
        return stg
    
    for i, excess in enumerate(svd_view) :
        excess = excess * -1  #### Excess is always negative so make positive
        
        stg_empty = max_stg - stg
        if stg_empty <= 0 :
            stg = max_stg
            bat_stg_view[i] = stg
            return stg
        
        if stg_empty > gwi :
        
            if excess <= gwi : 
                stg_view[i] = -excess  #### leaves an amount of EXS equal to loss ie 15-25% 
                svd_view[i] += excess
                loss_view[i] = ((1 - loss) * - excess)
                stg += excess / 4 * loss
                bat_stg_view[i] = stg
            else : 
                stg_view[i] = -gwi  ### stg_view should be true and stg has loss so can't book so much out. However we use the same file to show battery graph.
                svd_view[i] += gwi
                loss_view[i] = ((1 - loss) * - gwi)
                stg += gwi / 4 * loss
                bat_stg_view[i] = stg
                
        elif excess <= stg_empty : 
                stg_view[i] = -excess
                svd_view[i] += excess
                loss_view[i] = ((1 - loss)* - excess)
                stg += excess / 4 * loss
                bat_stg_view[i] = stg
        else : 
                stg_view[i] = -stg_empty
                svd_view[i] += stg_empty
                loss_view[i] = ((1 - loss) * - stg_empty)
                stg += stg_empty / 4 * loss
                bat_stg_view[i] = stg
        
        #stg_view = stg_view * -1 #### The battery is loading which is negative on graph
    
    return  stg
    
def stg_above_gap(carf, stg, gwo, svd_view, stg_view, inflow_view, bat_stg_view) :
    # "Battery Storage capacity is greater than the supply gap so discharges at the higher of gwo (GW out) or gap depth (GW's) as battery cannot run flat"
            
    for i, gap in enumerate(svd_view) : # Gapfile is a slice of rfd[pfx+region+"SVD"] which is array of  float of gap depths every 15mins
        
        if gap <= gwo : 
            stg_view[i] = gap
            svd_view[i] = -gap ### Its minus the gap which will give zero
            stg -= gap / 4
            bat_stg_view[i] = stg
        else : 
            stg_view[i] = gwo
            svd_view[i] = -gwo
            stg -= gwo / 4
            bat_stg_view[i] = stg
        if stg <= 0 : stg = 0
        
        if carf == 'A' : 
            stg_view[i] += inflow_view[i]
            stg += inflow_view[i] / 4
            bat_stg_view[i] = stg
    
    return  stg

def stg_below_gap(carf, max_stg, stg, gwo, svd_view, stg_view, inflow_view, bat_stg_view) :
    # ' When storage is less than the gap requires then either max out or gap size determines the GW's out and at some point storage = zero'
    hold_used = []
    less_than_gwo = gwo / 6 ### Use 1/4 to fill biggest gap update with 1/4 then do again. Larger number = slower but smoother graph of storage used in gap.
    loop_count = i = 0
    start_stg = stg
    
    while stg > 0 and svd_view.sum() > 0 :
        
        max_gap_index = int(np.argmax(svd_view)) #### Find index of largest gap
        
        if svd_view[max_gap_index] >= less_than_gwo :
            if stg > less_than_gwo :
                stg_view[max_gap_index] += less_than_gwo 
                svd_view[max_gap_index] -= less_than_gwo
                stg -= less_than_gwo / 4 
            else :
                stg_view[max_gap_index] += stg
                svd_view[max_gap_index] -= stg
                stg -= stg / 4
                if stg < 0.005 * max_stg : stg = 0  ##### Crap code which fixes the recursive problem by throwing last < 1/2% away
                
        elif svd_view[max_gap_index] < less_than_gwo :
            if stg > svd_view[max_gap_index] :
                stg_view[max_gap_index] += svd_view[max_gap_index]
                svd_view[max_gap_index] -= svd_view[max_gap_index]
                stg -= svd_view[max_gap_index] / 4
            else :
                stg_view[max_gap_index] += stg
                svd_view[max_gap_index] -= stg
                stg -= stg / 4
                if stg < 0.005 * max_stg : stg = 0  ##### Crap code which fixes the recursive problem by throwing last < 1/4% away
        
        if carf == 'A' and i != len(stg_view): 
            stg_view[i] += inflow_view[i]
            stg += inflow_view[i] / 4
            i += 1
                     
        if hold_used.count(max_gap_index) >= 6 : svd_view[max_gap_index] = 0  ##### We get away with this cos we run 1 per Region will fail with multi.
        else : hold_used.append(max_gap_index)       
        loop_count += 1
    
    stg_temp_holder = np.round(np.cumsum(stg_view * -1) / 4, 3) + start_stg   
    for i in range(len(bat_stg_view)) : bat_stg_view[i] += stg_temp_holder[i]
    
    bat_stg_view = np.round(np.cumsum(stg_view * -1) / 4 + start_stg, 3)

    #print(' Are these the same ? ', stg_temp_holder.sum(), bat_stg_view.sum())

    return stg

def storage_calc_totals_add_stp(rfd, rft, rfc, rfg, pfx, stp) :
    fn = ' Storage Calc on STG addition  '
    ##### All additions are added here and done by adding and subtracting NOT retotalling for all
    #stp = rfg['stp']
    
    if stp not in rfc['FYD'+'storage_fuel_list'] : return  #### ['BAT','IHB', 'EVB', 'EVG', 'HPU'] #### Should HYD be in there now - I think so ?????
    
    rfd_storage_keys = [key for key in rfd.keys() if key[:3] == pfx and key[-6:-3] == stp and ('ALL' or 'DEM' or 'STG' or 'LOSS' or 'CAP' or 'GWO') not in key]  #### This is dubious code and needs to be re thought ie locate storage files smarter.
    
    for key in rfd_storage_keys :
        
        pfx, region, stp, gcd = key_split(key)
        
        if gcd == 'STG' : gcd = ''
        
        if pfx+region+stp+gcd+'STG' not in rfd : rfd[pfx+region+stp+gcd+'STG'] = copy.deepcopy(rfd[pfx+region+stp+gcd]) ### - rfd[pfx+region+stp+gcd+'LOSS']) (lazy way to remove error)
       
        rfd[pfx+region+stp+gcd+'STG'][0] = rfc[pfx+region+stp+gcd+'init_storage']  
              
        if pfx+region+stp+'STG' not in rfd : rfd[pfx+region+stp+'STG'] = copy.deepcopy(rfd[pfx+region+stp+gcd+'STG'])
        else : rfd[pfx+region+stp+'STG'] += rfd[pfx+region+stp+gcd+'STG']
        
        if pfx+region+'ALL'+'STG' not in rfd : rfd[pfx+region+'ALL'+'STG'] = copy.deepcopy(rfd[pfx+region+stp+gcd+'STG'])
        else : rfd[pfx+region+'ALL'+'STG'] += rfd[pfx+region+stp+gcd+'STG']
        
        if pfx+'ALL'+stp+'ALL'+'STG' not in rfd : rfd[pfx+'ALL'+stp+'ALL'+'STG'] = copy.deepcopy(rfd[pfx+region+stp+gcd+'STG'])
        else : rfd[pfx+'ALL'+stp+'ALL'+'STG'] += rfd[pfx+region+stp+gcd+'STG']
        
        if pfx+'ALL'+'ALL'+'STG' not in rfd : rfd[pfx+'ALL'+'ALL'+'STG'] = copy.deepcopy(rfd[pfx+region+stp+gcd+'STG'])
        else : rfd[pfx+'ALL'+'ALL'+'STG'] += rfd[pfx+region+stp+gcd+'STG']
    
    return    
    
def storage_calc_totals_remove_stp(rfd,rft,rfc,rfg,pfx) :
    fn = 'Recalcs the total on STG removal  '
    #print(fn, 'Start  ', datetime.now())
    stp = rfg["stp"]
    
    if stp not in rfc['FYD'+'storage_fuel_list'] : return
    
    remove_keys = [key for key in rfd.keys() if key[:3] == pfx and key[-3:] == 'STG' and stp in key[-9:-6] and 'ALL' not in key]
      
    for key in remove_keys :  
        
        pfx, region, stp, gcd = key_split(key)
        
        if pfx+region+stp+'STG' in rfd : rfd[pfx+region+stp+'STG'] -= rfd[pfx+region+stp+gcd+'STG']

        if pfx+region+'ALL'+'STG' in rfd : rfd[pfx+region+'ALL'+'STG'] -= rfd[pfx+region+stp+gcd+'STG']
        
        if pfx+'ALL'+stp+'ALL'+'STG'  in rfd : rfd[pfx+'ALL'+stp+'ALL'+'STG'] -= rfd[pfx+region+stp+gcd+'STG']

        if pfx+'ALL'+'ALL'+'STG' in rfd : rfd[pfx+'ALL'+'ALL'+'STG'] -= rfd[pfx+region+stp+gcd+'STG']
        
        del rfd[pfx+region+stp+gcd+'STG']

    if rfc['FYD'+'autorun'] == 'N' : print(fn, 'Finish  ', datetime.now())
            
def load_GWO_and_CAP(rfc, pfx, region, stp, gcd, gwo, cap) :
    
    rfc[pfx+region+stp+gcd+'CAP'] = cap
    if cap != 0 : 
        if pfx+region+stp+'CAP' not in rfc : rfc[pfx+region+stp+'CAP'] = cap
        else : rfc[pfx+region+stp+'CAP'] += cap
        if pfx+'ALL'+stp+'CAP' not in rfc : rfc[pfx+'ALL'+stp+'CAP'] = cap
        else : rfc[pfx+'ALL'+stp+'CAP'] += cap
    
    rfc[pfx+region+stp+gcd+'GWO'] = gwo
    if gwo != 0 :
        if pfx+region+stp+'GWO' not in rfc :  rfc[pfx+region+stp+'GWO'] = gwo
        else : rfc[pfx+region+stp+'GWO'] += gwo
        if pfx+'ALL'+stp+'GWO' not in rfc :  rfc[pfx+'ALL'+stp+'GWO'] = gwo
        else : rfc[pfx+'ALL'+stp+'GWO'] += gwo

    
    
def storage_runner(rfd,rft,rfc,rfg,pfx) : ###### Used for BAT, HPU, GOC, NGT, EVG 
    fn = ' Storage Runner  '
    if rfc['FYD'+'autorun'] == 'N' : print(fn, 'Start Stg File Time  ',rfg["stp"], datetime.now())
    
    stp = rfg["stp"]
    gcd = ''
    
    cur_obj.execute("select CAF from gbgenfuel where code = %s", [stp])
    caf = cur_obj.fetchone()
    carf = str(caf[0])  ###### 'C' is Charge from Excess - 'A' is Automatic ie Inflow - 'R' is Charge from Rooftop Solar - 'F' is Charge from Fuel ie Unlimited

    def sql_read_for_stg(stp, region) : ##### Take out EVB later 

        cur_obj.execute("select genregion, genfuel, sum(storage), sum(inflow), avg(inloss), sum(gwout), sum(qty), count(*) from gbstg where genregion = %s and genfuel = %s and status = 'L' group by genregion, genfuel, ord order by genregion, genfuel, ord", [region, stp]) # Ord dictates summary done here
        storage = cur_obj.fetchall()
                
        return storage

    for region in rfc['FYD'+'genreg'] :
        
        stp = rfg['stp'] ### Repeated as we change STP with EVB / EVG going through
        
        region_svd = np.array(rfd[pfx+region+"SVD"])   ##### Why not write to SVD file live ie region_svd is a pointer ?????

        #if region == 'TAS' and rfc[pfx+"ALL"+"HYD"+"done"] == 'N' : continue #### when HYDRO was running this func.
        
        ger_data = gap_excess_file(rfd,rft,rfc,rfg,pfx, region)
                      
        storage = sql_read_for_stg(stp, region)
        
        if storage == [] : 
            print(fn," There is no ", pfx+region+stp," for this region" )
            continue
        
        if stp == 'EVB' : 
            evb_users = rft[pfx+'EVB_grid_bat_pc'] /100 * float(storage[0][6])  ###### Percent who will use the grid * qty from sum(qty) comes from purchases.
            stp = 'EVG'
            if pfx+region+stp not in rfd : rfd[pfx+region+stp] = np.zeros(rfc['FYD'+'elements'])
        else : evb_users = 1

        for stg_grouped in storage :
            
            if carf == 'A' :  inflow_file = np.full(rfc["FYD"+"elements"], round(int(stg_grouped[3])/1000 ,3))
            else : inflow_file = np.zeros(rfc["FYD"+"elements"])
            
            loss = float((100 - float(stg_grouped[4])) / 100)
            
            if stp == 'EVG' :  
                max_stg = float(stg_grouped[2]) * evb_users * rfc['FYD'+'EVB_allocate_as_battery_pc'] - rfc[pfx+region+'EVB_stg_taken']
                gwi = gwo = float(stg_grouped[5]) * evb_users * rfc['FYD'+'EVB_allocate_as_battery_pc']
            else : 
                max_stg = float(stg_grouped[2]) / 1000
                gwi = gwo = float(stg_grouped[5]) / 1000
                            
            if stp == 'GOC' or stp == 'NGT' : load_GWO_and_CAP(rfc, pfx, region, stp, gcd, gwo, cap = 0)
            
            ### Set the letters used for GCD(gcd) as we group else require a different SQL read
            if stp in ('BAT', 'EVB', 'EVG', 'GOC', 'NGT') : gcd = region[0] + stp[0] + stp[2] ### Setup correct code for gcd
            elif stp in ('HPU','HYD') : gcd = region[0] + stp[0] + stp[1]
            else : gcd = '___'
            
            ### Get Storage Capacity and Record in the 'CAP' suffix for p+r+f+g+'CAP'
            #cap = max_stg
            
            if stp not in ['GOC','NGT'] : load_GWO_and_CAP(rfc, pfx, region, stp, gcd, gwo, max_stg)
        
            rfc[pfx+region+stp+gcd+'init_storage'] = stg = max_stg / 2
            if pfx+region+stp+'init_storage' not in rfc :  rfc[pfx+region+stp+'init_storage'] = rfc[pfx+region+stp+gcd+'init_storage']
            else : rfc[pfx+region+stp+'init_storage'] += rfc[pfx+region+stp+gcd+'init_storage']
            if pfx+region+stp not in rfd : rfd[pfx+region+stp] = np.zeros(rfc['FYD'+'elements'], dtype = np.float32)
            if pfx+region+stp+'LOSS' not in rfd : rfd[pfx+region+stp+'LOSS'] = np.zeros(rfc['FYD'+'elements'], dtype = np.float32)
            stg_file = rfd[pfx+region+stp+gcd] = np.zeros(rfc['FYD'+'elements'], dtype = np.float32)  ### 
            loss_file = rfd[pfx+region+stp+gcd+'LOSS'] = np.zeros(rfc['FYD'+'elements'], dtype = np.float32)  ### 
            bat_stg_file = rfd[pfx+region+stp+gcd+'STG'] = np.zeros(rfc['FYD'+'elements'], dtype = np.float32)
            
            #### MAIN LOOP THROUGH list of GAPS AND EXCESS IN GRID OUTPUT - storage and +/- determine actions in functions ####
            for i, gap in enumerate(ger_data) :
                
                start_pos = int(ger_data[i][0])
                end_pos = int(ger_data[i][3] )
                
                svd_view = region_svd[start_pos : end_pos]
                inflow_view = inflow_file[start_pos : end_pos]
                stg_view = stg_file[start_pos : end_pos]
                loss_view = loss_file[start_pos : end_pos]
                bat_stg_view = bat_stg_file[start_pos : end_pos]
                
                if  ger_data[i][1] > 0 : # This is a GAP file and numbers are positive
                    
                    if stg > 0 :
                        if stg > svd_view.sum() / 4 or (len(svd_view) * gwo) / 4 < stg :  stg = stg_above_gap(carf, stg, gwo, svd_view, stg_view, inflow_view, bat_stg_view)
                        else :  stg = stg_below_gap(carf, max_stg, stg, gwo, svd_view, stg_view, inflow_view, bat_stg_view)
                
                if  ger_data[i][1] < 0 and  stg < max_stg:
                
                    if carf == 'C' : stg = load_stg_up(max_stg, stg, gwi, loss, svd_view, stg_view, loss_view, bat_stg_view) ##### C = Charge so charge from Excess
                    if carf == 'A' : stg = load_inflow_up(max_stg,  stg, stg_view, inflow_view, bat_stg_view) ### A = Auto so Charge from Inflow
                    if carf == 'R' : pass  #### Recharge from Solar Rooftop SRT
                    if carf == 'F' : continue #### Has own FUEL so doesn't recharge
            
        ####### Write to files for later graph display #####
        rfd[pfx+region+stp] += rfd[pfx+region+stp+gcd]  #### Build 'STP' from 'GCD's - Why doesn't calc_totals do this ?
        rfd[pfx+region+stp+'LOSS'] += rfd[pfx+region+stp+gcd+'LOSS']  #### Build 'STP' from 'GCD's - Why doesn't calc_totals do this ?

    stg_level_hold = 0
    for i, stg_level in enumerate(bat_stg_file) :   #### Corrects zeroes with the actual storage at that point
        
        if stg_level != 0 : stg_level_hold = stg_level
        else : bat_stg_file[i] = stg_level_hold
    
    storage_calc_totals_add_stp(rfd, rft, rfc, rfg, pfx, stp) 
    
    add_stp_to_rfg_genfuel(rfd, rft, rfc, rfg, pfx, stp)
    
    stp = rfg["stp"]
    rfc[pfx+"ALL"+stp+"done"] = "Y"  

    if rfc['FYD'+'autorun'] == 'N' : print(fn,  "End_pos Stg File Time  ",  datetime.now())
        
    return
############################################


def charge_from_solar(i, curr_stg, max_stg, gwi, loss, ihb_data, chgup, loss_data, bat_stg_file) :
    
    if curr_stg <= max_stg :  # Should always be true 
        if max_stg - curr_stg < (gwi / 4) :
            gwhin = max_stg - curr_stg
        else :
            gwhin = min(chgup[i], gwi)

        curr_stg += gwhin / 4 * loss
        loss_data[i] = gwhin * (1-loss)
        ihb_data[i] = -gwhin 
        bat_stg_file[i] = curr_stg

def discharge_to_profile(i, curr_stg, gwo, ihb_data, dischg, bat_stg_file) :
    
    if curr_stg  < dischg[i] :
        if dischg[i] < gwo :gwhout = curr_stg
        else : gwhout = min(curr_stg, dischg[i])
    else :
        gwhout = min(dischg[i], gwo)
        
    curr_stg -= gwhout / 4
    ihb_data[i] = gwhout
    bat_stg_file[i] = curr_stg
    
def ihb_runner(rfd, rft, rfc,rfg,pfx) : # Used by IHB, EVB. Key diff to Storage_Runner is load from SRT only and discharge according to a fixed profile.
    fn = " Manages IHB / EVB  "
    if rfc['FYD'+'autorun'] == 'N' : print(fn, 'Start ihb_runner   ', datetime.now())
    stp = rfg["stp"]

    cur_obj.execute("select genregion, genfuel, gencode, gwout, storage, inflow, inloss, qty , status, sqlid from gbstg where genfuel = %s and status = 'L'", [stp])
    ihb_all = cur_obj.fetchall()
    
    for ihb in ihb_all :
        region = ihb[0]
        stp = fuel = ihb[1]
        gcd = ihb[2]
        loss = (100 - ihb[6]) / 100   #### ie 15% loss becomes 0.85 as easier to use later
        srt_qty = rfc[pfx+region+'SRT'+'srt_uplift_users']  # This comes from Realloc for REN's ###
        users =  float(ihb[7]) # This is millions and assumes a Powerwall or equivalent is a 12KWH battery
        if stp == 'EVB' : 
            users = users * rft[pfx+'EVB_house_bat_pc'] / 100
            max_stg = float(ihb[4] * users * rfc['FYD'+'EVB_allocate_as_battery_pc']) # This figure is GWH's and is the amount EV owner allocates for storage IHB or EVG
        else :  max_stg = float(ihb[4] * users) # This figure is GWH's and assumed to start half full at start of period

        rfc[pfx+region+stp+'init_storage'] = rfc[pfx+region+stp+gcd+'init_storage'] = curr_stg = max_stg / 2  #### these are 1:1 so OK but poor
        gwi = float(ihb[5]) * users # This is GW's
        gwo = float(ihb[3]) * users  # This is GW's
        
        load_GWO_and_CAP(rfc, pfx, region, stp, gcd, gwo, max_stg)
        
        if (stp == 'IHB' and 'EVB' not in rfg['genfuel']) or (stp == 'EVB' and 'IHB' not in rfg['genfuel']) :  base_use = np.full(rfc["FYD"+"elements"], rfc['FYD'+'House_Base_KWHs'] * users)   ###### Ensure we DO NOT USE TWICE IE IHB AND EVB
        else : base_use = np.zeros(rfc["FYD"+"elements"])
        chgup = np.array(rfd[pfx+region+"SRT"]) * users / srt_qty ##### rfc[pfx+region+fuel+'srt_market'] #### 
        chgup -= base_use
        chgup[chgup < 0] = 0  ##### WHY IS THIS NEEDED  #######

        ihb_data = rfd[pfx+region+fuel+gcd] = np.zeros(rfc["FYD"+"elements"], dtype = np.float32)
        if pfx+region+stp not in rfd : rfd[pfx+region+stp] = np.zeros(rfc["FYD"+"elements"], dtype = np.float32)
        loss_data = rfd[pfx+region+stp+gcd+'LOSS'] = np.zeros(rfc["FYD"+"elements"], dtype = np.float32)
        if pfx+region+stp+'LOSS' not in rfd : rfd[pfx+region+stp+'LOSS'] = np.zeros(rfc["FYD"+"elements"], dtype = np.float32)  
        bat_stg_file = rfd[pfx+region+stp+gcd+'STG'] = np.zeros(rfc['FYD'+'elements'], dtype = np.float32)
        actdem = np.array(rfd["FYD"+region+"DEM"])   ##### GET THE ACT DEMAND AT EVERY POINT
        avgdem = (actdem.reshape(-1,96).mean(axis=0))  #### GET THE AVERAGE DEMAND AS A FIGURE FOR EACH OF 96 TIMEs OF DAY

        dischg = np.array(rfc["DEV"+region+stp+"PRO"]) * users 
        dischg_start = rfc['FYD'+'start_pos'] % (365 * 96) + 4 ####  (Start a hour earlier for discharge)
        dischg = np.append(dischg[dischg_start:], dischg[:dischg_start])   #### Adjust the profile to fit selected date / time ie 4am / 8pm /Start winter / Summer etc etc
        
        j = 0
        for i in range(len(dischg)) :
            dischg[i] = dischg[i] + 2 * (dischg[i] * (actdem[i] - avgdem[j]) / avgdem[j]) ### Adjust discharge up / down based on demand at that time vs average demand
            j = 0 if j == 95 else j + 1
        
            if chgup[i] > 0 : charge_from_solar(i, curr_stg, max_stg, gwi, loss, ihb_data, chgup, loss_data, bat_stg_file)
            if dischg[i] > 0 :   discharge_to_profile(i, curr_stg, gwo, ihb_data, dischg, bat_stg_file)  ####### THIS IS DISCHARGING ACCORDING TO PROFILE 
            if bat_stg_file[i] == 0 : bat_stg_file[i] = bat_stg_file[i-1]

###### THIS IS BUILT AS IF THERE IS ONLY EVER ONE ENTRY PER REGION - MULTIPLE ENTRIES ARE SUPPORTED via GCD's #####

        rfd[pfx+region+stp] += rfd[pfx+region+stp+gcd]  #### Build 'STP' from 'GCD's - Why doesn't calc_totals do this ?
        rfd[pfx+region+stp+'LOSS'] += rfd[pfx+region+stp+gcd+'LOSS']  #### Build 'STP' from 'GCD's - Why doesn't calc_totals do this ?
 
    
    
    add_stp_to_rfg_genfuel(rfd, rft, rfc, rfg, pfx, stp)

    storage_calc_totals_add_stp(rfd, rft, rfc, rfg, pfx, stp)
    
    rfc[pfx+"ALL"+stp+"done"] = "Y"     
    
    if rfc['FYD'+'autorun'] == 'N' : print(fn, 'Finish ihb_runner   ', datetime.now())
    
    return

