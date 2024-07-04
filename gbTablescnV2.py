# The main Table through which generators are presented before execution via [DO IT] button

import PySimpleGUI as sg

from gbUtilsV2 import*
from gbGFuncsV2 import gen_destroy
from gbTIhbV2 import ihb_main_scn
from gbTEvbV2 import evb_main_scn
from gbTEDscnV2 import evb_demand_scn

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()
con_obj.autocommit = True

###### THIS FLAG COMES FROM AUTORUN AND TURNS OFF THE data_table_scnS BEFORE RUNNING GRAPHFUNCS #####
#def autorunflag(rfd,rft,rfc,rfg,pfx) :


sg.set_options(font=("Arial Bold", 18), dpi_awareness = True)

gui_size = 15
bs = (15,1) # Button size
bf = ('Helvetica',gui_size) # Button Font & size
tf = ('Helvetica',gui_size) # Text font & size
mf = ('Helvetica',gui_size) # Menu Font and size
ts = ('Helvetica',30) # Title Size


def gap_fix_table(datalines, header, title, colwidth, col_just, selected) :
    
    # ------ Window Layout ------
    layout = [[sg.P(),sg.T(title, font = ('Helvetica',30,'bold'), text_color = 'blue', size =(60,1), background_color = 'white',  justification = "center"), sg.P()], [sg.Table(values=datalines, headings=header,  max_col_width=25, auto_size_columns=False, col_widths=colwidth, 
                        display_row_numbers=True,  justification= 'center', num_rows=20, key='-TABLE-', selected_row_colors='black on white',
                        expand_x=False, expand_y=True, right_click_menu = ['&Right', ['Total (L)ive']], vertical_scroll_only=False, enable_click_events=True, header_text_color = 'blue',
    header_background_color = 'white',),
            sg.Sizegrip()],
            [sg.Push(), sg.B("    EXIT    ", key = '-EXIT-',s=bs), sg.B("   REMOVE   ", key = "-REMOVE-", s= bs),  sg.B("    DO IT    ", key = "-DOIT-", s=bs), sg.B('  UPDATE DATA  ', key = '-UPDATE-',s=bs), sg.B('EV Demand', key = '-EVDEM-', s=bs) ,sg.Push()]]

    # ------ Create Window ------
    window = sg.Window(title, layout, resizable=True, finalize=True, keep_on_top=True, default_button_element_size = bs)

    # Highlight the rows (select) that have checkboxes checked
    window['-TABLE-'].update(values=datalines[1:][:], select_rows=list(selected))
    
    return window
    

###### ------ Event Loop ------  ########
def data_table_scn(rfd, rft, rfc, rfg, pfx) :
    fn = " Running  data_table_scn   "
    rfc[pfx+"dogapfix"] = "N"   #### Sets the default which certain buttons change to 'Y' ########
    if rfc['FYD'+'autorun'] == "Y" :
        rfc[pfx+"dogapfix"] = "Y"
        return
    
    BLANK_BOX = '☐'
    CHECKED_BOX = '☑'
    stp = rfg["stp"]
    table = rfc["tabletype"]


    if table == "FIX" :
        datalines = []
        cur_obj.execute(" select genregion, genfuel, gencode, genname, respmin, respmax, respup, respdown, gwhout, gwcost, status, sqlid from gbfix where status != 'D' order by genregion, genfuel, gencode")
        fixed = cur_obj.fetchall()
        for fix in fixed :
            fix = list(fix)
            datalines.append(fix)
            helpline = "            0       1      2       3       4        5          6          7           8         9           10      11   "
            header = ['Select', 'Region','Fuel', 'Code', 'Name', 'Min %', 'Max %', 'TimeUp', 'TimeDown', 'Max MWHs', 'Cap Cost', 'Status', 'sqlid']
            title = "  Base Load Generator Assets to be Opened and Active   "
            colwidth = [8,8,8,8,15,8,8,8,8,8,8,6,6]
            col_just = ['c','c','c','c','l','r','r','r','r','r','r','c','r']

    if table == "STG" :
        datalines = []
        cur_obj.execute("select genregion, genfuel, gencode, genname, storage, inflow, inloss, gwout, qty, mktsize, gwcost, status, sqlid from gbstg where genfuel = %s and status != 'D' order by genregion, genfuel, gencode", [stp])
        storage = cur_obj.fetchall()
        for gen in storage :
            gen = list(gen)
            helpline = "         0      1      2       3       4        5       6       7       8       9       10       11       12  "
            datalines.append([gen[0],gen[1], gen[2], gen[3], gen[4], gen[5], gen[6], gen[7], gen[8], gen[9], gen[10], gen[11], gen[12]])
            header = ['Select', 'Region', 'Fuel', 'Code', 'Name', 'Cap MWHs', 'In MWHs','Loss %', 'Out MWHs', 'Qty (Mill)', 'Mkt (Mill)','Cap Cost', 'Status', 'sqlid']
            title = f"  {rfc['FYD'+stp+'fuel_name']} to be Opened and Active   "
            colwidth = [8,8,6,6,15,8,8,6,8,8,6,6,6,6]
            col_just = ['c','c','c','c','l','r','r','r','r','r','r','r','c','l']


    if table == "IC" :
        cur_obj.execute("SELECT region, oth_reg, ic_code, ic_gwh, loss, legs, status, ic_name, cap_cost, route, sqlid  FROM gbic where status != 'D' order by status, legs, region")
        icorder = cur_obj.fetchall()
        datalines = []
        for regic in icorder :
            regic = list(regic)
            datalines.append([regic[0], regic[1], regic[2], regic[7], regic[9], regic[5], regic[4], regic[3], regic[8], regic[6], regic[10]])
            header = ['Select', 'Region', 'Oth Region', 'IC Code', 'IC Name', 'Route', 'Legs', 'Loss %', 'Cap MWs', 'Cap Cost', 'Status']
            title = "  Interstate Lines to be Opened and Active   "
            colwidth = [8,8,8,6,20,6,6,6,8,8,6]
            col_just = ['c','c','c','c','l','c','c','r','r','r','c',]
            
    if table == "NGT"   :
        datalines = rfc[pfx+"ngttabledata"] # [region, stp, "New","Gas Turbine Peakers", "9999999", nogt, 0, nogt*1000, nogt * 1.25, "L", 0])
        header = rfc[pfx+"ngtheader"]
        title = rfc[pfx+"ngttitle"]
        colwidth = rfc[pfx+"ngtwidth"]
        col_just = ['c','c','c','l','r','r','r','r','r','c','c']
        
    datalines.insert(0,header)
        
    for i in range(1,len(datalines)) :
        if datalines[i][0] != CHECKED_BOX and datalines[i][0] != BLANK_BOX :
            if datalines[i][-2] == "L" :
                datalines[i].insert(0,CHECKED_BOX)
            else :
                datalines[i].insert(0,BLANK_BOX)
            
    selected = {i for i, row in enumerate(datalines[1:][:]) if row[0] == CHECKED_BOX}
    
    window = gap_fix_table(datalines, header, title, colwidth, col_just, selected)
    
    while True:
        
        event, values = window.read()
        
        def update_sql_db(rfd, rft, rfc, rfg, pfx) :
            fn = " Update SQL DB in TableData    "
            for line in datalines[1:] :
                #region = line[1]
                sqlparams = []
                sqlparams.append(line[-2]) # status
                sqlparams.append(line[-1]) # sqlid
                if rfc["tabletype"] == "FIX" :
                    cur_obj.execute(" update  gbfix set status = %s where sqlid = %s", sqlparams)
                    con_obj.commit()
                if rfc["tabletype"] == "IC" :
                    cur_obj.execute(" update  gbic set status = %s where sqlid = %s", sqlparams )
                    con_obj.commit()
                if rfc["tabletype"] == "STG" :
                    cur_obj.execute(" update  gbstg set status = %s where sqlid = %s", sqlparams)
                    con_obj.commit()
                if rfc["tabletype"] == "NGT" : # TO BE DONE AND MAYBE NOT NEEDED
                    pass
                    # cur_obj.execute(" update  gbfix set status = %s where sqlid = %s", )
                    # con_obj.commit()
                    
        print("E   ", event, " V  ", values, "S   ", selected)
        
        if event in (sg.WIN_CLOSED, '-EXIT-', 'esc'):
            rfc[pfx+"dogapfix"] = "N"
            break
        
        elif event[0] == '-TABLE-' and event[2][0] not in (None, -1) and event[2][1] == 0:   # if clicked a data row rather than header or outside table
            row = event[2][0]+1
            if datalines[row][0] == CHECKED_BOX:     # Going from Checked to Unchecked
                selected.remove(row-1)
                datalines[row][0] = BLANK_BOX
                datalines[row][-2] = "X"
            else:                               # Going from Unchecked to Checked
                selected.add(row-1)
                datalines[row ][0] = CHECKED_BOX
                datalines[row][-2] = "L"
            window['-TABLE-'].update(values=datalines[1:][:], select_rows=list(selected))    # Update the table and the selected rows
        elif event[0] == '-TABLE-' :
            if event[2][0] == -1 :  #### THIS MEANS WE ARE CLICKING ON HEADER  #####
                if event[2][1] == 0 :   #### THIS MEANS WE ARE CLICKING HEADER = "SELECTED" COLUMN ie With CHECKED_BOX in.  #####
                    
                    if rfc[pfx+"tabletog"] == "N" :
                        for line in datalines :
                            line[0] = BLANK_BOX
                            line[-2] = "X"
                        rfc[pfx+"tabletog"] = "Y"       
                    elif rfc[pfx+"tabletog"] == "Y" :
                        for line in datalines :
                            line[0] = CHECKED_BOX
                            line[-2] = "L"
                        rfc[pfx+"tabletog"] = "N"       
                    selected = {i for i, row in enumerate(datalines[1:][:]) if row[0] == CHECKED_BOX}
                    window['-TABLE-'].update(values=datalines[1:][:], select_rows=list(selected))
                
                if event[2][1] > 0 :  ##### WE ARE CLICKING ON ANY COLUMN BUT NOT THE HEADER OF A COLUMN - IS THIS REQUIRED ANYMORE #####
                    del datalines[0]
                    datalines.sort(key = lambda x: x[event[2][1]])
                    datalines.insert(0, header)
                    selected = {i for i, row in enumerate(datalines[1:][:]) if row[0] == CHECKED_BOX}
                    window['-TABLE-'].update(values=datalines[1:][:], select_rows=list(selected))

        if event == '-DOIT-' :
            update_sql_db(rfd, rft, rfc, rfg, pfx)
            rfc[pfx+"dogapfix"] = "Y"
            break
        
        if event == '-REMOVE-' :
            gen_destroy(rfd,rft,rfc,rfg,pfx)
        
        if event == '-UPDATE-' and stp == "IHB" :
            
            datalines = ihb_main_scn(rfd,rft,rfc,rfg,pfx, datalines)
            
            window['-TABLE-'].update(values=datalines[1:][:])
            window['-TABLE-'].update(values=datalines[1:][:], select_rows=list(selected))
            window.refresh()

                   
                
        if event == '-UPDATE-' and stp == "EVB" :
            
            window.disappear()
            
            datalines = evb_main_scn(rfd,rft,rfc,rfg,pfx, datalines)
            
            window['-TABLE-'].update(values=datalines[1:][:])
            window['-TABLE-'].update(values=datalines[1:][:], select_rows=list(selected))
            window['-EVDEM-'].update(visible = True)
            window.refresh()   
                    
            window.reappear()
        
        if event == '-EVDEM-' and stp == "EVB" :
            
            window.disappear()
            
            evb_demand_scn(rfd, rft, rfc, rfg, pfx)
            
            window.reappear()
        
        if '-TABLE-' in event and '+CLICKED+' in event :
            totrow = event[2][0] + 1
            totcol = event[2][1]
            
            print(totrow, totcol)
        
        if event == 'Total (L)ive' :
            
            if is_a_number(str(datalines[totrow][totcol])) :
                total = 0
                for i, num in enumerate (datalines) :
                    if i == 0 or num[-2] == 'X': continue
                    
                    total += float(num[totcol])
                round(total)
                print('This is where we Total Table', total, totcol)
                totlay = [[sg.Text(f'{datalines[0][totcol]} Total =  {total}')],
                          [sg.T()],
                          [sg.P(), sg.B('OK', size = bs, key = '-TOTOK-', enable_events = True), sg.P()]]
                
                totcalc = sg.Window(f'Total {datalines[0][totcol]} All Lines', totlay, finalize=True, keep_on_top=True)  
            
                while True :
                    tote, totv = totcalc.read()
                    
                    if tote == '-TOTOK-' :
                        totcalc.close()
                        break
                
            else : 
                print(str(datalines[totrow][totcol]) ,"   is not considered a number")
                break

    window.close()
    



