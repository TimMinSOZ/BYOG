# gbgraphctlV2

from gbGRunV2 import*
from gbUtilsV2 import*
from gbBaseV2 import*
from gbFfuncsV2 import *
import numpy as np
import copy


def update_after_start_date_changes(rfd, rft, rfc, rfg, pfx) :
    fn = ' update_after_start_date_changes which is done in Main Control Screen '
    
    FYD_update_list = [key for key in rfd if 'all_FYD_data' in key]
    
    rfd_start = position_from_date_sort(rfc['FYD'+'FYDs_initial_start_date'])
    rfd_end = rfd_start + rfc['FYD' + 'elements']
    
    print(fn, '   ', rfd_start, rfd_end, rfc['FYD'+'FYDs_initial_start_date'],'     ', FYD_update_list)
    
    for key in FYD_update_list :
        pfx, region, fuel, gcd = key_split(key)
        pfx = 'FYD'
        gcd = ''
        rfd[pfx+region+fuel+gcd] = copy.deepcopy(rfd[pfx+region+fuel+gcd+'all_FYD_data'][rfd_start : rfd_end])
    
        start_date_obj = date_obj_from_position(rfd_start)
        rfc['FYD'+"start_date"] = start_date_obj.strftime('%Y%m%d%H%M')
        rfc['FYD'+'start_pos'] = rfd_start 
     
    calc_totals(rfd, rft, rfc, rfg, pfx)
        
    #############       S W I T C H    TO    D I F F E R E N T     P R E F I X  and Reload Fuels      ##################################    
        
    pfx = rfg['pfx']
                     
    calc_totals(rfd, rft, rfc, rfg, pfx)
    
    renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
    
    rfc['FYD'+'autorun'] = "Y"
    
    for fuel in rfg['genfuel'][:-4] : #### Maybe should use rfc[pfx+'genfuel']
        
        if fuel in ['WIN','SRT','SUT'] : continue
        
        Fkey =  [Fkey[0] for Fkey in rfc['FYD'+'F_code_link'] if Fkey[1] == fuel][0]
        
        print(fn,'   F Key =  ', Fkey)
        
        if Fkey != [] :
            rfg['stp'] = fuel
            if rfc[pfx+"ALL"+fuel+"done"] == 'Y' or pfx+region+fuel in rfd : gen_destroy(rfd,rft,rfc,rfg,pfx)  
            rfc[pfx+"dogapfix"] == "Y"
            globals()[Fkey](rfd, rft, rfc, rfg, pfx)
            if Fkey not in('F6','F7') :
                calc_totals(rfd, rft, rfc, rfg, pfx)
                renewable_target_allocation(rfd, rft, rfc, rfg, pfx)
    
    rfc['FYD'+'autorun'] = "N"     
    
    print(fn,'    ', datetime.now())    
    return


def pfx_switch(rfd,rft,rfc,rfg,pfx) :
    fn = " PFX Switch    "
    region = rfg["region"]
    if rfg["pfx"] == "FYD" :
        rfg["pfx"] = "125" #### Shoukld not hard copy as what about other prefixes than 125
        rfg["genfuel"] = copy.deepcopy(rfc[rfg["pfx"]+region+"genfuel"])
    else :
        rfg["pfx"] = "FYD"
        rfg["genfuel"] = copy.deepcopy(rfc[rfg["pfx"]+region+"genfuel"])

    rfc[rfg["pfx"]+"zoom"] = "N"
    rfc[rfg["pfx"]+"eventkey"] = "1"
    pfx = rfg["pfx"] # crossing boundries 
    graph_display(rfd, rft, rfc, rfg, pfx)
    return


def region_graph(rfd, rft, rfc, rfg, pfx) :
    fn = " Region Graph   "
    region = rfg["region"]
    print(fn,"   ", region)
    if rfc[pfx+"eventkey"] == "1" :
        region = "ALL"
    elif rfc[pfx+"eventkey"] == "2" :
        region = "NSW"
    elif rfc[pfx+"eventkey"] == "3" :
        region = "VIC"
    elif rfc[pfx+"eventkey"] == "5" :
        region = "SA"
    elif rfc[pfx+"eventkey"] == "7" :
        region = "QLD"
    elif rfc[pfx+"eventkey"] == "9" :
        region = "TAS"

    if len(rfg["genfuel"]) > 3 or rfg["region"] == region :
        rfg["genfuel"] = copy.deepcopy(rfc[pfx+region+"genfuel"])
    rfg["region"] = region
    rfc[pfx+"region"] = region
    
    if "degran" not in rfg.keys() :
        rfg["degran"] = rfc[pfx+"degran"]
        
    if rfc[pfx+"eventkey"] == "6" :
        print(fn, "Doing Pie Display")
        piedisplay(rfd,rft,rfc,rfg,pfx)
    elif rfc[pfx+"eventkey"] == "4" :
        print(fn, "Doing Greg Display")
        gregdisplay(rfd,rft,rfc,rfg,pfx)
    else :
        graph_display(rfd, rft, rfc, rfg, pfx)

    return


def graphsmoother(rfd, rft, rfc, rfg, pfx) :
    " Based on days figure in smoother the graph is a transformed into a ruuning average"   
    print("Graph Smoother Start  ", datetime.now())
    smoother = 30 * 96
    region = rfg[pfx+"region"]
    smooth_graph = np.zeros(int(rfc["FYD"+"elements"]))
    for fuel in rfg["genfuel"] :
        smooth = 0
        if pfx+"ALL"+fuel in rfd :
            data = np.array(rfd[pfx+"ALL"+fuel])
        else :
            print("Graph Smoother Error - Cannot read rfd for key in rfc[pfx+'rfgraph'] =  ", pfx+"ALL"+fuel, "Print just prefix " , pfx)
            print(rfd.keys())
            print(rfc[pfx+"rfgraph"].keys())
            continue
        #print(fuel, "Sum", data.sum())
        for i, gwh in enumerate(data) :
            smooth = smooth + gwh
            if i < smoother :
                smoothgwh = round(smooth/(i+1),3)
                #print(gwh,"   ",smooth,"    ",i,"    ", smoothgwh,"   View first few transactions in smoother")
            if i >= smoother :
                smooth = smooth - data[i-smoother]
                smoothgwh = round(smooth / smoother,3)
            smooth_graph[i] = smoothgwh
        #print(fuel, "After Smoothing Total  ", listsum(smooth_graph))
        rfc[pfx+"rfgraph"][pfx+"ALL"+fuel] = list(smooth_graph)
        
        print(rfc[pfx+"rfgraph"].keys(), "Graphsmoother finishes  ", datetime.now())
        smooth_graph.fill(0)

    return

def graph_resolution(rfd, rft, rfc, rfg, pfx) :
    fn ="  Graph Resolution   "
    rfc["zoom"] = "N"
    eventkey = rfc[pfx+"eventkey"]
    degranlist = [1,24,96,480]
    if eventkey == "<" :
        if rfg["degran"] != 1 :
            rfg["degran"] = degranlist[degranlist.index(rfg["degran"])-1]
        else :
            return
    elif eventkey == ">" :
        if rfg["degran"] != 480 :
            rfg["degran"] = degranlist[degranlist.index(rfg["degran"])+1]
        else :
            return
    graph_display(rfd, rft, rfc, rfg, pfx)
    return


def rf_graph_zoom(rfd, rft, rfc, rfg, pfx) :
    fn = " RF ZOOM  "
    if len(rfc["onclick"]) > 2 :
        print("rf_graph_zoom - this is onclick file", rfc["onclick"])
        print("rf_graph_zoom - this is zommtrck  file", rfc["zoomtrack"])

        if rfc["onclick"][1][4] == False and rfc["onclick"][2][4] == False : # should actuall check against the click type <MouseButton.LEFT: 1>
        # do position here and pass across in rfc
            if rfc["zoom"] != "Y" or rfg["degran"] != 1 :
                rfg["startpos"] = round(rfc["onclick"][2][2] * rfg["degran"])
                rfg["endpos"] = round(rfc["onclick"][1][2] * rfg["degran"])
                rfc["zoomtrack"].insert(0, [rfg["startpos"], rfg["endpos"], rfg["region"], rfg["degran"]])
            else : 
                rfg["startpos"] = round(rfc["zoomtrack"][0][0] + rfc["onclick"][2][2])
                rfg["endpos"] = round(rfc["zoomtrack"][0][0] + rfc["onclick"][1][2])
                rfc["zoomtrack"].insert(0, [rfg["startpos"], rfg["endpos"], rfg["region"], rfg["degran"]])
            print (fn, rfg["startpos"], rfg["endpos"], rfg["degran"], "    ", rfc["zoomtrack"][0][0] ,  rfc["zoomtrack"])
            rfc["zoom"] = "Y"
            rfg["degran"] = 1
        else :
            print("Zoom Exiting No 1 on_key at return  ", rfc["onclick"], rfc["onclick"][1][4], rfc["onclick"][2][4])
            return
    else :
        print("zoom Exiting No 2 on_key at return  ", rfc["onclick"])
    if rfg["startpos"] < rfg["endpos"] :
        graph_display(rfd,rft,rfc,rfg,pfx)
    else :
        print(fn , "Start is greater then End position ", rfg["startpos"] ,"  ", rfg["endpos"])
    
    return

def rf_zoom_esc(rfd,rft,rfc,rfg,pfx) :
    fn = " RF Zoom Escape    "
    if rfc["pie"] == "Y" :
        rfc["pie"] = "N"
        rfc["ax"].clear()
        rfc["ax"] = plt.gca()  # get the current axes
        rfc["ax"].relim()      # make sure all the data fits
        rfc["ax"].autoscale()  # auto-scale
        
    if rfc["zoom"] == "Y" :
        print("rf_zoom_esc zoomtrack before anything is deleted",rfc["zoomtrack"] )
        if len(rfc["zoomtrack"]) > 1 :
            del rfc["zoomtrack"][0]
            rfg["startpos"] = rfc["zoomtrack"][0][0]
            rfg["endpos"] =rfc["zoomtrack"][0][1]
            #rf_graph_zoom(rfd, rft, rfc, rfg, pfx)
            print("rf_zoom_esc zoomtrack after zoom and 1st deleted", rfc["zoomtrack"])
            if len(rfc["zoomtrack"]) == 1 :
                rfc["zoom"] == "N"
                #rfg["degran"] = rfc[pfx+"degran"]
                
        else :
            #print("Done the else so set zoom off " , rfc["zoomtrack"], rfc["no"])
            rfc["event.key"] = rfc["no"]
            rfc["zoom"] = "N"
            rfg["degran"] = rfc["FYD"+"degran"]
            rfc[pfx+"elements"] = rfc["FYD"+"elements"] # These 3 lines are standard and should be in the function on exit ??????? Else duplicating code
            rfg["startpos"] = rfc["FYD"+"startpos"]
            rfg["endpos"] = rfc["FYD"+"endpos"]
            
    graph_display(rfd, rft, rfc, rfg, pfx)
    
    
def move_graph_order(rfd, rft, rfc, rfg, pfx) :
    fn = "  Move Graph Order   "

    realx = int(rfc["dblclickxy"][0])
    realy = round(rfc["dblclickxy"][1],3)
    height = 0
    
    ##### This deletes the fuel if the fuel is on the bottom of the graph
    if realy < rfg["rfgout"][0][realx] and len(rfg["rfgout"]) > 1  :
        del rfg["rfgout"][0]
        del rfg["genfuel"][0]
        if rfg["genfuel"] != [] :
            if rfg["genfuel"][-1] == "DL1" :
                del rfg["rfgout"][-4:]
                del rfg["genfuel"][-4:]

        graph_display(rfd,rft,rfc,rfg,pfx)
        return

    ##### This moves the fuel from any position bar first to first position ie bottom of graph
    for i, fuel in enumerate(rfg["genfuel"]) :
        height = height + rfg["rfgout"][i][realx] 
            
        if height > realy :
            del rfg["genfuel"][i]
            rfg["genfuel"].insert(0, fuel)
            graph_display(rfd,rft,rfc,rfg,pfx)
            break
        elif len(rfg["genfuel"]) == i+1 and  realy > height  : 
            rfg["genfuel"] = copy.deepcopy(rfc[rfg["pfx"]+rfg["region"]+"genfuel"])
            graph_display(rfd,rft,rfc,rfg,pfx)
            break
    return
