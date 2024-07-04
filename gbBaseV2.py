#gbcorefuncV2

import numpy as np
from datetime import datetime
import copy
from gbUtilsV2 import fuelsort
import dill



import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()


def gap_excess_calc(rfd, rft, rfc, rfg, pfx) : # Belongs to profile with start end POS ?
    "Takes each region and looks up demand and compares to supply and returns a list of + / - gwhs and places these with totals in rfd and rft with code DVS appended"
    "Add 2 further lines which are a ZL1 for extra info in legend and DL1 which gives a black line at the Demand Line"
    "NOTED - GAPS are positive and EXS is negative due to building graph"
    fn = ' Gap Excess Calc after Calc_Totals  '
    #print("Start gap_excess_calc  ", datetime.now())
    
    all_svd_data = np.zeros(rfc["FYD"+"elements"])
    all_gap_data = np.zeros(rfc["FYD"+"elements"])
    all_exs_data = np.zeros(rfc["FYD"+"elements"])
    
    dav = rfc['FYD'+'demand_allowed_variance']
    
    for region in rfc[pfx+"genreg"] :
        
        rfd[pfx+region+"ZL1"] = np.full(rfc["FYD"+"elements"], 0)
        rfd[pfx+"ALL"+"ZL1"] = np.full(rfc["FYD"+"elements"], 0)

        rfd[pfx+region+"DL1"] = np.full(rfc["FYD"+"elements"], max(rfd[pfx+region+"ALL"]/rfg['demline']))
        rfd[pfx+"ALL"+"DL1"] = np.full(rfc["FYD"+"elements"], max(rfd[pfx+"ALL"+"ALL"]/rfg['demline']))
        
        #print(fn,'  What is happening with rfg Demline  ', rfg['demline'], rfd[pfx+region+"DL1"].sum(), region)
        
        reg_dem_data = np.array(rfd["FYD"+region+"ALL"]) + np.array(rfd[pfx+region+'EVB'+'DEM']) ###### HERE WE WRITE DEMAND which reallocate uses to uplift supply
        reg_all_data = np.array((rfd[pfx+region+"ALL"]))
        
        #avg_dem = reg_dem_data.mean()
        
        #dav_act = dav * avg_dem
        
        reg_svd_data = reg_dem_data - reg_all_data
        reg_gap_data = reg_dem_data - reg_all_data
        reg_gap_data[reg_gap_data < 0] = 0
        reg_exs_data = reg_dem_data - reg_all_data
        reg_exs_data[reg_exs_data > 0] = 0
        
        all_svd_data = all_svd_data + reg_svd_data
        all_gap_data = all_gap_data + reg_gap_data
        all_exs_data = all_exs_data + reg_exs_data
           
        rfd[pfx+region+"DEM"] = copy.deepcopy(reg_dem_data)
        rfd[pfx+region+"SVD"] = copy.deepcopy(reg_svd_data)
        rfd[pfx+region+"EXS"] = copy.deepcopy(reg_exs_data)
        rfd[pfx+region+"GAP"] = copy.deepcopy(reg_gap_data)
        
        #rfd[pfx+region+"GAP"+'ADJ'] = copy.deepcopy(np.where(reg_gap_data < dav_act, reg_gap_data, 0))
        #rfd[pfx+region+"GAP"+'ADJ'] = np.zeros(rfc['FYD'+'elements'])    
        
        rft[pfx+region+"DEM"] = round(reg_dem_data.sum()/4)
        rft[pfx+region+"SVD"] = round(reg_svd_data.sum()/4)
        rft[pfx+region+"EXS"] = round(reg_exs_data.sum()/4)
        rft[pfx+region+"GAP"] = round(reg_gap_data.sum()/4)
        
        if pfx != "FYD" :
            if rft[pfx+region+"GAP"] > rfc[pfx+region+"max_gap"] :
                rfc[pfx+region+"max_gap"] = rft[pfx+region+"GAP"]
        
        del reg_dem_data, reg_all_data, reg_svd_data, reg_gap_data, reg_exs_data

    all_dem_data = np.array(rfd["FYD"+"ALL"+"ALL"]) + np.array(rfd[pfx+'ALL'+'EVB'+'DEM'])
   
    rfd[pfx+"ALL"+"DEM"] = all_dem_data
    rfd[pfx+"ALL"+"SVD"] = all_svd_data
    rfd[pfx+"ALL"+"EXS"] = all_exs_data
    rfd[pfx+"ALL"+"GAP"] = all_gap_data
    
    rft[pfx+"ALL"+"DEM"] = round(all_dem_data.sum()/4)
    rft[pfx+"ALL"+"SVD"] = round(all_svd_data.sum()/4)
    rft[pfx+"ALL"+"EXS"] = round(all_exs_data.sum()/4)
    rft[pfx+"ALL"+"GAP"] = round(all_gap_data.sum()/4)
    
    if pfx != "FYD" :
        if rft[pfx+"ALL"+"GAP"] > rfc[pfx+"ALL"+"max_gap"]  :
            rfc[pfx+"ALL"+"max_gap"] = rft[pfx+"ALL"+"GAP"]

    if rfc['FYD'+'autorun'] == 'N' : print("End gap_excess_calc  ", datetime.now())
    return              

def calc_totals(rfd, rft, rfc, rfg, pfx) : # Non positional ? or Positional for totals for a start > end POS ?
    fn = "Calc Totals   "
    " Uses the base lists in rfd[pfx+region+fuel] to add up and update all the totals held in rft[pfx+region+fuel or pfx+region+ALL or pfx+ALL+fuel or ALL and include for list by region and by fuel by ALL]"
    #print(fn, "   Start Time  ", datetime.now())

    allgenfuel = []
    reg_list = np.zeros(rfc["FYD"+"elements"], dtype= 'float32')
    fuel_list = np.zeros(rfc["FYD"+"elements"], dtype= 'float32')
    all_list = np.zeros(rfc["FYD"+"elements"], dtype= 'float32')
    rfc[pfx+"ALL"+"genfuel"] = []
    for region in rfc[pfx+"genreg"] :
        rfc[pfx+region+"genfuel"] = []
        for fuel in rfc["FYD"+"allfuel"][:-4] :
            if pfx+region+fuel in rfd.keys() :
                nplist = np.array(rfd[pfx+region+fuel]) # HERE IS THE HEART OF CALC 
                rft[pfx+region+fuel] = round(nplist.sum() / 4) 
                reg_list = np.round(reg_list + nplist,3)
                rfc[pfx+region+"genfuel"].append(fuel)
                if fuel not in allgenfuel : allgenfuel.append(fuel)
                    
                    
        rfc[pfx+region+"genfuel"] = fuelsort(rfd, rft, rfc, rfg, pfx, rfc[pfx+region+"genfuel"])           
        rfd[pfx+region+"ALL"] = copy.deepcopy(reg_list)
        rft[pfx+region+"ALL"] = round(reg_list.sum() / 4)
        all_list = np.round(all_list + reg_list,3)
        reg_list[:len(reg_list)] = 0
        
    for fuel in rfc["FYD"+"allfuel"] :
            if fuel in allgenfuel :
                rfc[pfx+"ALL"+"genfuel"].append(fuel)
    
    rfc[pfx+"ALL"+"genfuel"] = fuelsort(rfd, rft, rfc, rfg, pfx, rfc[pfx+"ALL"+"genfuel"])
    
    rfd[pfx+"ALL"+"ALL"]  = copy.deepcopy(all_list)
    rft[pfx+"ALL"+"ALL"] = round(all_list.sum() / 4)


    for fuel in rfc["FYD"+"allfuel"][:-4] :
        for region in rfc[pfx+"genreg"] :
            if pfx+region+fuel in rfd.keys() :
                fuel_list = np.round(fuel_list + np.array(rfd[pfx+region+fuel]),3)
        rfd[pfx+"ALL"+fuel]  = copy.deepcopy(fuel_list)
        rft[pfx+"ALL"+fuel] = round(fuel_list.sum() /4)
        
        fuel_list[:len(fuel_list)] = 0
    
    for region in rfc[pfx+"genreg"] : # Gets last 4 and appends them
        for fuel in rfc["FYD"+"allfuel"][-4:] :
            rfc[pfx+region+"genfuel"].append(fuel)
    
    for fuel in rfc["FYD"+"allfuel"][-4:] :
        rfc[pfx+"ALL"+"genfuel"].append(fuel)
        if pfx+region+fuel+"done" not in rfc.keys() :
            rfc[pfx+region+fuel+"done"] = "N"

    if rfc['FYD'+'autorun'] == 'N' : print(fn,  "   END  = ", datetime.now())
    
    gap_excess_calc(rfd, rft, rfc, rfg, pfx) 
    
    return

def renewable_target_allocation(rfd, rft,  rfc, rfg, pfx) :
    fn = ( "renewable_target_allocation   ")
    "Takes the %age of region to be renewable energy and returns the multiple for WIN, SUT, SRT after adjust for +/- from other FUELS"
    #print("Start " , fn , "   ", datetime.now())
    
    for region in rfc["FYD"+"genreg"] :
        
        srt_tgt_pc = rfc[pfx+region+"SRT"+"TGT"] / 100 ### All INT percentages no decimal hence divide by 100
        sut_tgt_pc = rfc[pfx+region+"SUT"+"TGT"] / 100
        win_tgt_pc = rfc[pfx+region+"WIN"+"TGT"] / 100
        
        if 'FYD'+region+'SRT' in rfd : act_srt = rfd['FYD'+region+'SRT'].sum()/4
        if 'FYD'+region+'SUT' in rfd : act_sut = rfd['FYD'+region+'SUT'].sum()/4
        if 'FYD'+region+'WIN' in rfd : act_win = rfd['FYD'+region+'WIN'].sum()/4
        
        act_dem = rfd["FYD"+region+"ALL"].sum()/4
        
        ren_tgt_pc = srt_tgt_pc + sut_tgt_pc + win_tgt_pc 
        WIN_and_SUT_tgt_pc = sut_tgt_pc + win_tgt_pc
        ren_tgt_gwh = act_dem  * ren_tgt_pc
        rfd[pfx+region+"REN"] = np.zeros(rfc['FYD'+'elements'])        
        
        
        if rfd[pfx+region+'EVB'+'DEM'].sum() != 0 and WIN_and_SUT_tgt_pc != 0 :
            evb_req_gwh  = round(rfd[pfx+region+'EVB'+'DEM'].sum()/4 * 1.1 , 3)  ##### Build 10% more than EVB demand
            if act_srt != 0 : evb_srt_uplift = evb_req_gwh / act_srt * rft[pfx+'evb_srt_chg_pc'] /100  #### Gives a decimal %age
            if act_sut != 0 : evb_sut_uplift = evb_req_gwh / act_sut * (1 - rft[pfx+'evb_srt_chg_pc'] / 100) * (sut_tgt_pc / WIN_and_SUT_tgt_pc) #### Gives a decimal %age
            if act_win != 0 : evb_win_uplift = evb_req_gwh / act_win * (1 - rft[pfx+'evb_srt_chg_pc'] / 100) * (win_tgt_pc / WIN_and_SUT_tgt_pc) #### Gives a decimal %age
        else : evb_srt_uplift = 0 ; evb_sut_uplift = 0 ; evb_win_uplift = 0
        

        ##### Adjust for gain / loss of electricity from use of other fuels whether Coal or a Battery
        
        if pfx+region+"ALL"+"FIX" in rft :  #### This total comes from Fixed_fuel and is NUC, CBL, CBR and GAS
            ren_tgt_gwh -=  rft[pfx+region+"ALL"+"FIX"]
        
        for fuel in ['HYD','GOC','HVI'] + rfc['FYD'+'storage_fuel_list'] :   
            
            if pfx+region+fuel in rfd and rfc[pfx+"ALL"+fuel+"done"] == "Y" and not (fuel == "HYD" and region == "TAS") :
                ren_tgt_gwh -=  rfd[pfx+region+fuel].sum() / 4  ### Add / Subtract from renewables for Hydro and add for loss in batteries and pumped hydro  
                
        #### Get the %age change required for each of SRT, SUT, WIN that has to be applied to the actual output ie Multiply Up 'FYD'
        
        
        if "FYD"+region+'SRT' in rfd :
        
            srt_tgt_uplift = (srt_tgt_pc / ren_tgt_pc) / (act_srt / ren_tgt_gwh)
            srt_tgt_uplift += evb_srt_uplift
            rfd[pfx+region+'SRT'] = np.round(rfd["FYD"+region+'SRT'] * srt_tgt_uplift, 3)
            rfd[pfx+region+"REN"] += rfd[pfx+region+'SRT']
            rfc[pfx+region+'SRT'+'srt_uplift_users'] = round(rfc[pfx+region+'SRT'+'srt_users'] * srt_tgt_uplift,3)
            
        if "FYD"+region+'SUT' in rfd :
            
            sut_tgt_uplift = (sut_tgt_pc / ren_tgt_pc) / (act_sut / ren_tgt_gwh)
            sut_tgt_uplift += evb_sut_uplift
            rfd[pfx+region+'SUT'] = np.round(rfd["FYD"+region+'SUT'] * sut_tgt_uplift, 3)
            rfd[pfx+region+"REN"] += rfd[pfx+region+'SUT']


        if "FYD"+region+'WIN' in rfd :
            
            win_tgt_uplift = (win_tgt_pc / ren_tgt_pc) / (act_win / ren_tgt_gwh )
            win_tgt_uplift += evb_win_uplift
            rfd[pfx+region+'WIN'] = np.round(rfd["FYD"+region+'WIN'] * win_tgt_uplift, 3)
            rfd[pfx+region+"REN"] += rfd[pfx+region+'WIN']
             
        #print(fn, region, 'SRT  '  ,srt_tgt_pc, round(evb_srt_uplift,3) , '  SUT  ', sut_tgt_pc, round(rft[pfx+'evb_srt_chg_pc'] * sut_tgt_pc / (WIN_and_SUT_tgt_pc),3), '  WIN  ', win_tgt_pc)
    
    return


def get_fuel_tgt_fix_stg_ic( rfd, rft, rfc, rfg, pfx) :
    fn = "Get Fuel Targets Fixed and Storage Gen Types  "
    print(fn, "Start time", datetime.now())
        
    #####  THIS ADDS IHB BATTERY DISCHARGE PROFILE into rfc["DEV"+region+"IHB"+"PRO"] AND UPDATES
    
    for region in rfc["FYD"+"genreg"] :
        
        rfc["DEV"+region+"IHB"+"PRO"] = []
        cur_obj.execute('select data from gbfuelprofiles where fuel = "IHB" and prefix = "DEV" and gcd = "PRO" and region = %s', [region])
        ihb_pro = cur_obj.fetchone()
        ihb_data = dill.loads(ihb_pro[0])

        rfc["DEV"+region+"IHB"+"PRO"] = np.array(ihb_data)
      
        
    ######  THIS ADDS EVB BATTERY DISCHARGE PROFILE into rfc["DEV"+region+"EVB"+"PRO"] AND UPDATES
    
    for region in rfc["FYD"+"genreg"] :
        
        rfc["DEV"+region+"EVB"+"PRO"] = []
        
        cur_obj.execute('select data from gbfuelprofiles where fuel = "EVB" and prefix = "DEV" and gcd = "PRO" and region = %s', [region])
        evb_pro = cur_obj.fetchone()
        evb_pro_data = dill.loads(evb_pro[0])

        rfc["DEV"+region+"EVB"+"PRO"] = np.array(evb_pro_data)

    
    ##### THIS LOADS THE TARGETS SET FOR WIND SOLAR AND SRT SOLAR
    
    cur_obj.execute("select sqlid, ord, fuel, region, rentgt, srt_mkt, qty from gbrentgt where status != 'X' order by ord")
    gentgt = cur_obj.fetchall()

    for tgt in gentgt :
        fuel = tgt[2]
        region = tgt[3]
        rfc[pfx+region+fuel+"TGT"] = int(tgt[4])
        if fuel == 'SRT' : rfc[pfx+region+fuel+'srt_market'] = round(float(tgt[5]),3)
        if fuel == 'SRT' : rfc[pfx+region+fuel+'srt_users'] = round(float(tgt[6]),3)
        # if pfx+region+'ren_tgt' in rfc : rfc[pfx+region+'ren_tgt'] += int(tgt[4])
        # else : rfc[pfx+region+'ren_tgt'] = int(tgt[4])
    

    ##### LOAD POPULATION FOR EACH REGION INTO rft["FYD"+region+"regpop"]
    
    cur_obj.execute('select genregion, sum(regpop) from gbregion group by genregion, regpop with rollup')
    pop_data = list(cur_obj.fetchall())
    
    for pop in pop_data :
        if pop == pop_data[-1] : continue
        region = pop[0]
        regpop = int(str(pop[1]))
        rft["FYD"+region+'pop'] = regpop
        rft["FYD"+region+'pop_pc'] = round(regpop / int(str(pop_data[-1][1])),2)
    rft["FYD"+'ALL'+'pop'] = int(str(pop_data[-1][1]))
    
    ##### LOAD THE CHARGE / DISCHARGE / HOUSE BAT / GRID BAT PERCENTAGES to rft IN CASE WE DO NOT RUN CHANGES BUT WE WILL STILL REQUIRE THEM (SAME CODE 2 X - FUNC ??) ######
    
    cur_obj.execute('select chg_day_pc, chg_srt_pc, hse_bat_pc, grid_bat_pc from gbstg where genfuel = "EVB" and genregion = "NSW"')
    demchg = cur_obj.fetchone()

    if demchg != [] :
    
        rft[pfx+'chg_day_pc'] = int(demchg[0])
        rft[pfx+'evb_srt_chg_pc'] = int(demchg[1])
        rft[pfx+'EVB_house_bat_pc'] = int(demchg[2])
        rft[pfx+'EVB_grid_bat_pc'] = int(demchg[3])
    
    print(fn, "End time", datetime.now())

    return



