#gbmiscfuncs

from gbUtilsV2 import*
from gbGFuncsV2 import*
from gbGRunV2 import*
import PySimpleGUI as sg

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()
con_obj.autocommit = True

##### Prepare Data Which Is 4 Levels - Header > Regions > Fuel > Generators

def show_gen_drilldown(rfd, rft, rfc, rfg, pfx) :
    fn =" Show Generators via Tree Select   "
    rftree = sg.TreeData()
    treedata = {}
    
    if 'ZL1' in rfg["genfuel"] : fuel_list = rfg['genfuel'][:-4]
    else : fuel_list = rfg['genfuel']
    
    rftree.insert("", 0, "DrillDown", ('Graph_Generators'))
    
    for i,region in enumerate(rfc["FYD"+"genreg"]) :
        
        cur_obj.execute('select regname from gbregion where genregion = %s',[region])
        regname = cur_obj.fetchone()
        
        rftree.insert("",str(i), region, (str(regname[0]).replace(" ","_")))
        treedata[str(i)] = (region)
        
        if fuel_list != [] :
            for j, fuel in enumerate(fuel_list) :
                if fuel in ["SUT","SRT","WIN"] or fuel not in rfc[pfx+region+"genfuel"]:
                    continue
                
                cur_obj.execute('select genfuel from gbgenfuel where code = %s',[fuel])
                fuelname = cur_obj.fetchone()
                    
                rftree.insert(str(i), str(i)+str(j), fuel,(str(fuelname[0]).replace(" ","_"), "Is this here"))
                treedata[str(i)+str(j)] = (region, fuel)

                if rfc[pfx+fuel+'table'] == "fix" :

                    cur_obj.execute('select genregion, genfuel, parent, genname from gbfix where genregion = %s and genfuel = %s and (status = "D" or genfuel = "GAS")',[region, fuel])
                    topgens = list(cur_obj.fetchall())
                    if topgens == [] :
                        continue
                    
                    for k, gen in enumerate(topgens) :
                        
                        rftree.insert(str(i)+str(j), str(i)+str(j)+str(k), gen[2], (str(gen[3]).replace(" ","_")))
                        treedata[str(i)+str(j)+str(k)] = (region, fuel, gen[2])
                        
                        cur_obj.execute('select genregion, genfuel, parent, gencode, genname from gbfix where status != "D" and genregion = %s and genfuel = %s and parent = %s',[region, fuel, gen[2]])
                        actgen = list(cur_obj.fetchall())
                        if actgen == [] :
                            continue
                        
                        for l, sub in enumerate(actgen) :
                            
                            rftree.insert(str(i)+str(j)+str(k), str(i)+str(j)+str(k)+str(l), sub[3], (str(sub[4]).replace(" ","_")))
                            treedata[str(i)+str(j)+str(k)+str(l)] = (region, fuel, gen[2], sub[3],"child")
                
                elif rfc[pfx+fuel+'table'] == "stg" :
                
                        cur_obj.execute('select genregion, genfuel, gencode, genname from gbstg where genregion = %s and genfuel = %s',[region, fuel])
                        topgens = list(cur_obj.fetchall())
                        if topgens == [] :    
                            continue
                                                
                        for k, gen in enumerate(topgens) :
                            
                            rftree.insert(str(i)+str(j), str(i)+str(j)+str(k), gen[2], (str(gen[3]).replace(" ","_")))
                            treedata[str(i)+str(j)+str(k)] = (region, fuel, "", gen[2], 'child')

                elif rfc[pfx+fuel+'table'] == "ic" :
                                    
                        cur_obj.execute('select region, oth_reg, ic_code, ic_name from gbic where region = %s',[region])
                        topgens = list(cur_obj.fetchall())
                        if topgens == [] :
                            continue
                        
                        for k, gen in enumerate(topgens) :
                            
                            rftree.insert(str(i)+str(j), str(i)+str(j)+str(k), gen[2], (str(gen[3]).replace(" ","_")))
                            treedata[str(i)+str(j)+str(k)] = (region, fuel, "", gen[2], "child")
                
                    
                tree=sg.Tree(data=rftree,
                    headings = ['   Generators Used In Graph    ', 'Output'],
                    col0_heading = "Gens By Regions",
                    col0_width = 20,
                    max_col_width = 50,
                    def_col_width = 20,
                    auto_size_columns = True,
                    text_color = 'blue',
                    background_color = 'white',
                    header_text_color = 'blue',
                    header_background_color = 'grey',
                    selected_row_colors = ('white','blue'),
                    justification = 'left',
                    right_click_menu = ['',[' Graph ', 'Calculate']],
                    font = ('Helvetica, 15'),
                    
                    #select_mode=psg.TABLE_SELECT_MODE_EXTENDED,
                    num_rows=20,
                    key='-TREE-',
                    show_expanded=False,
                    enable_events=True,
                    expand_x=False,
                    expand_y=True,
                    )
    layout=[[tree]]
    rftreewin=sg.Window("Generators Used In Graph", layout, size=(900, 1000), resizable=True)
    
    while True:
        event, values = rftreewin.read()
        print ("event:",event, "values:",values)
        if event == sg.WIN_CLOSED:
            break
            
        if event == " Graph " :
            td = treedata[values['-TREE-'][0]]
            print(fn, td)
            if len(td) >= 4 :
                if td[4] == "child" :
                    rfg["gencode"] = td[3]
                    rfg["genfuel"] = [td[1]]
                    rfg["region"] = td[0]
                    rftreewin.close()
                    graph_display(rfd, rft, rfc, rfg, pfx)
                    rfg["gencode"] = ""
                    break
                
        if event == 'Calculate' :
            pass
                    
    return

if __name__ == "__main__" : 
    pass           
    



