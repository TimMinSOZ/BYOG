# gbgraphselectV2

import numpy as np
from datetime import datetime

from gbFfuncsV2 import *
from gbGFStgV2 import*
from gbCtlscnV2 import*
from gbGCtlV2 import*
from gbGTreeV2 import*
from gbXXtestfile import*

def on_click(event, *args):
    fn = " On Click for Graph    "
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f',
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

    print("*********** Inside onclick ***************")
    rfd = args[0]
    rft = args[1]
    rfc = args[2]
    rfg = args[3]
    pfx = rfg['pfx']
    if event.xdata != None :
        xdata = int(event.xdata)
        ydata = int(event.ydata)
        rfc["onclick"].insert(0, [int(event.x), int(event.y), xdata, ydata, event.dblclick, event.button])
    else :
        rfc["onclick"].insert(0, [event.x, event.y, 0, 0, event.dblclick, event.button])
        xdata = round(event.xdata,4)
        ydata = round(event.ydata,4)
    print(fn, "Actuall Click Pos =   ", rfg["startpos"] + xdata ," xdata  =  " , xdata ,' ydata = ', round(event.ydata,3), "  Click Position =  " , rfg["startpos"] + xdata ,  "  On Click Stuff   " , rfc["onclick"][:3])

    if len(rfc["onclick"]) > 1 :
        if rfc["onclick"][0][4] == False and rfc["onclick"][1][4] == False :
            if int(rfc["onclick"][0][2]) > int(rfc["onclick"][1][2]) :
                zoommark = rfc["ax"].axvspan(int(rfc["onclick"][1][2]), int(rfc["onclick"][0][2]), ymin=0, ymax=1, alpha=0.3, color='blue')
                rfc["fig"].canvas.draw()
                rfc["fig"].canvas.flush_events()

    if event.dblclick :
        rfc["dblclickxy"] = [event.xdata, event.ydata]
        move_graph_order(rfd, rft, rfc,rfg, pfx)

    if len(rfc["onclick"]) > 6 :
        rfc["onclick"] = rfc["onclick"][0:5]

    return


def on_key(event, *args):
    print('you pressed', event.key, event.y, event.x, event.xdata, event.ydata, datetime.now())


    rfd = args[0]
    rft = args[1]
    rfc = args[2]
    rfg = args[3]
    pfx = rfg["pfx"]
    if event.xdata != None :
        xdata = round(event.xdata,4)
        ydata = round(event.ydata,4)
        rfc["onclick"].insert(0, [event.key, event.x, event.y, xdata, ydata,"Empty"])
    else :
        rfc["onclick"].insert(0, [event.key, event.x, event.y, 0, 0,"Empty"])
    
    print(rfc["onclick"][:3])

    rfc["onkey"].insert(0, event.key)
    if len(rfc["onclick"]) > 10 :
        rfc["onclick"] = rfc["onclick"][0:9]

    rfc[pfx+"eventkey"] = event.key
    #print("doing on_key >>>>>  Degran from rfc  ", rfc[pfx+"degran"], event.key)

    if event.key in ["1","2","3","4","5","6","7","9"] :
        region_graph(rfd, rft, rfc, rfg, pfx)

    elif event.key == "<" or event.key == ">" :
        graph_resolution(rfd, rft, rfc, rfg, pfx)

    elif event.key == "z" :
        rf_graph_zoom(rfd, rft, rfc, rfg, pfx)

    elif event.key == "escape" :
        rf_zoom_esc(rfd,rft,rfc,rfg,pfx)

    elif event.key == "y" :
        pfx_switch(rfd,rft,rfc,rfg,pfx)

    elif event.key == "insert" :
        main_control_scn(rfd,rft,rfc,rfg,pfx)
        
    elif event.key == "j" :
        show_gen_drilldown(rfd,rft,rfc,rfg,pfx)
        
    elif event.key == "ctrl+a" :
        
        rfg['genfuel'] = [fuel_from_graph_pos(rfd,rft,rfc,rfg,pfx)]
        graph_display(rfd,rft,rfc,rfg,pfx)
        
        print('*** Control a key press combination detected - return =  ', rfg['genfuel'])
    
    elif event.key == 'ctrl+b' :
        
        #fuel = fuel_from_graph_pos(rfd,rft,rfc,rfg,pfx)
        pass
    
    elif event.key == 'ctrl+/' : # Used as a test bed key for development
        
        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
        #gas_optimizer(rfd,rft,rfc,rfg, pfx)
        pass

        
    elif event.key == "f1" : # Grid Battery
        F1(rfd,rft,rfc,rfg,pfx)

    elif event.key == "f2" : # Pumped Hydro
        F2(rfd,rft,rfc,rfg,pfx)

    elif event.key == "f3" : # Hydro
        F3(rfd,rft,rfc,rfg,pfx)

    elif event.key == "f4" : # Interconnectors
        F4(rfd,rft,rfc,rfg,pfx)

    elif event.key == "f5" : # Existing Gas Turbines
        F5(rfd,rft,rfc,rfg,pfx)

    elif event.key == "f6" : # Build New Gas Turbines
        F6(rfd,rft,rfc,rfg,pfx)

    elif event.key == "f7" : # Base Load Generators
        F7(rfd,rft,rfc,rfg,pfx)
            
    elif event.key == "f8" : # In House Batteries
        F8(rfd,rft,rfc,rfg,pfx)

    elif event.key == "f9" : # EV Batteries
        F9(rfd,rft,rfc,rfg,pfx)
    
    elif event.key == 'f11' :
        rfg['stp'] = 'BAT'
        storage_runner(rfd,rft,rfc,rfg,pfx)
        
        calc_totals(rfd,rft,rfc,rfg,pfx)
        
        graph_display(rfd,rft,rfc,rfg,pfx)

    elif event.key == "f12" : # Reset to Norm ???
        F12(rfd,rft,rfc,rfg,pfx)

