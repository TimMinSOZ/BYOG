# gbFfuncs - Contains the wrapper to run each fuel type in

import numpy as np

from gbGFuncsV2 import* 
from gbGFStgV2 import * 
from gbGRunV2 import*
from gbUtilsV2 import*
from gbBaseV2 import*
from gbTablescnV2 import*

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()
con_obj.autocommit = True


def F1(rfd,rft,rfc,rfg,pfx) :
    stp = rfg["stp"] = "BAT"
    rfc['tabletype'] = "STG"
    

    if rfc[pfx+"ALL"+stp+"done"] == "N" :
        data_table_scn(rfd, rft, rfc, rfg, pfx)
        if rfc[pfx+"dogapfix"] == "Y" :
            storage_runner(rfd, rft, rfc, rfg, pfx)
            rfc[pfx+"dogapfix"] = "N"
            #print('Inside F1 launcher - here is the tracked info b4 Renew and Calc_tots    ', rfd[pfx+'NSW'+stp][27193:27198],'   ', pfx+'NSW'+stp)

    else :
        gen_destroy(rfd, rft, rfc, rfg, pfx)
        rfc[pfx+"dogapfix"] = "N"
        
    if rfc['FYD'+'autorun'] == 'N' : 
        
        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
        calc_totals(rfd, rft, rfc, rfg, pfx)
        graph_display(rfd, rft, rfc, rfg, pfx)
        #print('Inside F1 launcher - here is the tracked info AFTER Renew and Calc_tots    ', rfd[pfx+'NSW'+stp][27193:27198],'   ', pfx+'NSW'+stp)

    return

def F2(rfd,rft,rfc,rfg,pfx) :
    stp = rfg["stp"] = "HPU"
    rfc['tabletype'] = "STG"
    
    if rfc[pfx+"ALL"+stp+"done"] == "N" :
        data_table_scn(rfd, rft, rfc, rfg, pfx)
        if rfc[pfx+"dogapfix"] == "Y" :
            storage_runner(rfd, rft, rfc, rfg, pfx)
            rfc[pfx+"dogapfix"] = "N"
    else :
        gen_destroy(rfd, rft, rfc, rfg, pfx)
        rfc[pfx+"dogapfix"] = "N"

    if rfc['FYD'+'autorun'] == 'N' : 

        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
        calc_totals(rfd, rft, rfc, rfg, pfx)
        graph_display(rfd, rft, rfc, rfg, pfx)
        
        return



def F3(rfd,rft,rfc,rfg,pfx) :

    stp = rfg["stp"] = "HYD"
    rfc['tabletype'] = "STG"
    if rfc[pfx+"ALL"+stp+"done"] == "N" :
        data_table_scn(rfd, rft, rfc, rfg, pfx)
        if rfc[pfx+"dogapfix"] == "Y" :
            storage_runner(rfd, rft, rfc, rfg, pfx)
            rfc[pfx+"dogapfix"] = "N"
            print('F3 running 1st pass total  ', rfd[pfx+'ALL'+'HYD'].sum()/4)
            renewable_target_allocation(rfd, rft,  rfc, rfg, pfx) #### Runs a 2nd time to adjust for REN change adjusted for HYD output
            gen_destroy(rfd, rft, rfc, rfg, pfx)
            calc_totals(rfd, rft, rfc, rfg, pfx)
            storage_runner(rfd, rft, rfc, rfg, pfx)
            print('F3 running 2nd pass total  ', rfd[pfx+'ALL'+'HYD'].sum()/4)
    else :
        gen_destroy(rfd, rft, rfc, rfg, pfx)
        rfc[pfx+"ALL"+stp+"done"] = "N"
        rfc[pfx+"dogapfix"] = "N"
    
    if rfc['FYD'+'autorun'] == "N" :     
          
        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
        calc_totals(rfd, rft, rfc, rfg, pfx)
        graph_display(rfd,rft,rfc,rfg, pfx)


def F4(rfd,rft,rfc,rfg,pfx) :

    stp = rfg["stp"] = "HVI"
    rfc['tabletype'] = "IC"
    if rfc[pfx+"ALL"+stp+"done"] == "N" :
        data_table_scn(rfd, rft, rfc, rfg, pfx)
        if rfc[pfx+"dogapfix"] == "Y" :
            interconnect_runner(rfd, rft, rfc, rfg, pfx)
            rfc[pfx+"ALL"+stp+"done"] = "Y"
            rfc[pfx+"dogapfix"] = "N"
    else :
        gen_destroy(rfd, rft, rfc, rfg, pfx)
        rfc[pfx+"ALL"+stp+"done"] = "N"
        rfc[pfx+"dogapfix"] = "N"
        
    if rfc['FYD'+'autorun'] == 'N' : 
        
        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
        calc_totals(rfd, rft, rfc, rfg, pfx)
        graph_display(rfd, rft, rfc, rfg, pfx)


def F5(rfd,rft,rfc,rfg,pfx) :

    stp = "GOC"
    rfg["stp"] = "GOC"
    rfc['tabletype'] = "STG"
    if rfc[pfx+"ALL"+stp+"done"] == "N" :
        data_table_scn(rfd, rft, rfc, rfg, pfx)
        if rfc[pfx+"dogapfix"] == "Y" :
            storage_runner(rfd, rft, rfc, rfg, pfx)
            renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
            gen_destroy(rfd, rft, rfc, rfg, pfx)
            calc_totals(rfd, rft, rfc, rfg, pfx)
            storage_runner(rfd, rft, rfc, rfg, pfx)
            rfc[pfx+"dogapfix"] = "N"
    else :
        gen_destroy(rfd, rft, rfc, rfg, pfx)
        rfc[pfx+"dogapfix"] = "N"
        for region in rfc["FYD"+"genreg"] :
            #rft[pfx+region+"ALL"+"GOC"] = 0
            rfc[pfx+region+'GOC'+'CAP'] = 0

    if rfc['FYD'+'autorun'] == 'N' : 

        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
        calc_totals(rfd, rft, rfc, rfg, pfx)
        graph_display(rfd,rft,rfc,rfg, pfx)


def F6(rfd,rft,rfc,rfg,pfx) :
    
    stp = rfg["stp"] = "NGT"
    rfc['tabletype'] = "STG"
    if rfc[pfx+"ALL"+stp+"done"] == "N" :
        new_gas_turbines(rfd,rft,rfc,rfg, pfx)
        data_table_scn(rfd, rft, rfc, rfg, pfx)

        if rfc[pfx+"dogapfix"] == "Y" :
            
            storage_runner(rfd, rft, rfc, rfg, pfx)
            rfc[pfx+"dogapfix"] = "N"
    else :
        gen_destroy(rfd, rft, rfc, rfg, pfx)
        rfc[pfx+"dogapfix"] = "N"
        for region in rfc["FYD"+"genreg"] :
            rft[pfx+region+"ALL"+"NGT"] = 0
    
    if rfc['FYD'+'autorun'] == 'N' : 
    
        calc_totals(rfd, rft, rfc, rfg, pfx)
        graph_display(rfd, rft, rfc, rfg, pfx)



def F7(rfd,rft,rfc,rfg,pfx) :
    fn = "Doing F7  "
    
    stp = rfg["stp"] = "FIX"
    rfc['tabletype'] = "FIX"
    if rfc[pfx+"ALL"+"FIX"+"done"] == "N" :
        data_table_scn(rfd, rft, rfc, rfg, pfx)
        if rfc[pfx+"dogapfix"] == "Y" :
            
            interconnect_runner(rfd, rft, rfc, rfg, pfx)
            calc_totals(rfd, rft, rfc, rfg, pfx)
            renewable_target_allocation(rfd, rft, rfc, rfg, pfx)
            fixed_fuel_runner (rfd, rft, rfc, rfg, pfx)
            rfc[pfx+"ALL"+"FIX"+"done"] = "Y"
            calc_totals(rfd, rft, rfc, rfg, pfx)
            renewable_target_allocation(rfd, rft, rfc, rfg, pfx)
            stp = rfg["stp"] = "HVI"
            gen_destroy(rfd, rft, rfc, rfg, pfx)
            rfc[pfx+"ALL"+stp+"done"] = "N"
            
        if rfc['FYD'+'autorun'] == 'N' : 
            
            calc_totals(rfd, rft, rfc, rfg, pfx)
            graph_display(rfd, rft, rfc, rfg, pfx)
        
    else :
        for region in rfc["FYD"+"genreg"] :
            rft[pfx+region+"ALL"+"FIX"] = 0

        for stp in rfc[pfx+"fixlist"] :
            rfg["stp"] = stp
            gen_destroy(rfd, rft, rfc, rfg, pfx)
        rfc[pfx+"ALL"+"FIX"+"done"] = "N"
        rfc[pfx+"dogapfix"] = "N"
        
    if rfc['FYD'+'autorun'] == 'N' : 

        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
        calc_totals(rfd, rft, rfc, rfg, pfx)
        graph_display(rfd, rft, rfc, rfg, pfx)



def F8(rfd,rft,rfc,rfg,pfx) :

    stp = rfg["stp"] = "IHB"
    rfc['tabletype'] = "STG"
    if rfc[pfx+"ALL"+stp+"done"] == "N" :
        data_table_scn(rfd, rft, rfc, rfg, pfx)
        if rfc[pfx+"dogapfix"] == "Y" :
            ihb_runner(rfd, rft, rfc,rfg,pfx)
    else :
        gen_destroy(rfd, rft, rfc, rfg, pfx)
        rfc[pfx+"dogapfix"] = "N"
        
    if rfc['FYD'+'autorun'] == 'N' : 
        
        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
        calc_totals(rfd, rft, rfc, rfg, pfx)
        graph_display(rfd, rft, rfc, rfg, pfx)

def F9(rfd,rft,rfc,rfg,pfx) :
    
    stp = rfg["stp"] = "EVB"
    rfc['tabletype'] = "STG"
    if rfc[pfx+"ALL"+stp+"done"] == "N" :
        data_table_scn(rfd, rft, rfc, rfg, pfx)
        if rfc[pfx+"dogapfix"] == "Y" :
            evb_demand_shape(rfd, rft, rfc, rfg, pfx)
            calc_totals(rfd, rft, rfc, rfg, pfx)
            renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
            ihb_runner(rfd, rft, rfc, rfg, pfx)
            if rft[pfx+'EVB_grid_bat_pc'] != 0 :
                calc_totals(rfd, rft, rfc, rfg, pfx)
                renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
                storage_runner(rfd, rft, rfc, rfg, pfx)
    else :
        gen_destroy(rfd, rft, rfc, rfg, pfx)
        rfg['stp'] = 'EVG'
        gen_destroy(rfd, rft, rfc, rfg, pfx)
        rfc[pfx+"dogapfix"] = "N"
        
        ###### CLEAR THE DEMAND SHAPE FILES AS EVB REMOVED ######
        rfd[pfx+'ALL'+'EVB'+'DEM'][:] = 0
        rft[pfx+'ALL'+'EVB'+'DEM'] = 0
        for region in rfc['FYD'+'genreg'] :
            rfd[pfx+region+'EVB'+'DEM'][:] = 0
            rft[pfx+region+'EVB'+'DEM'] = 0
            
    if rfc['FYD'+'autorun'] == 'N' : 
        
        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
        calc_totals(rfd, rft, rfc, rfg, pfx)
        graph_display(rfd, rft, rfc, rfg, pfx)
    
    
def F12(rfd,rft,rfc,rfg,pfx) :
    
    rfg["startpos"] = rfc["FYD"+"startpos"]
    rfg["endpos"] = rfc["FYD"+"endpos"]
    rfg["degran"] = rfc["FYD"+"degran"]
    rfg["region"] = "ALL"
    rfg["genfuel"] = copy.deepcopy(rfc[pfx+"ALL"+"genfuel"])
    graph_display(rfd,rft,rfc,rfg,pfx)

    return



