# Runs the Control Screen

from gbGFuncsV2 import*
from gbGRunV2 import*
from gbGCtlV2 import*
from gbBaseV2 import*
from gbFfuncsV2 import*
from gbCGscnV2 import*
from gbCPscnV2 import*
import numpy as np
import PySimpleGUI as sg


import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()
con_obj.autocommit = True

def main_control_scn(rfd,rft,rfc,rfg,pfx) :
    
    fn = " MAIN runs the event loop  "
    
    if pfx == 'FYD' : 
        print('FYD does not have access to Insert and Control Screen')
        return

    cur_obj.execute('select scrcode, scrname, sqlid from gbscreens') ##### Gets the list of pre loaded renewable targets to list in menu
    result = cur_obj.fetchall()
    sep = "-"
    loadlist = [sep.join([str(word)  for word in line]) for line in result]
    dellist = [str(sep.join([str(word)  for word in line]))+'-Delete' for line in result]
    
    cur_obj.execute('select pfx, pfx_name from gb_pfx_store group by pfx, pfx_name ') ##### Gets the list of pre saved profile to list in menu
    pfxresult = cur_obj.fetchall()
    if pfxresult != [] :
        pfx_load_list = [sep.join([str(word)  for word in line]) for line in pfxresult]
        pfx_del_list = [str(sep.join([str(word)  for word in line]))+'-Delete' for line in pfxresult]
    else :
        pfx_load_list = []
        pfx_del_list = []

    start_year = rfc['FYD'+'FYDs_initial_start_date'][:4]
    start_month = rfc['FYD'+'months_in_year'][int(rfc['FYD'+'FYDs_initial_start_date'][4:6])-1]
    
    gui_size = 15
    bs = (15,1) # Button size
    bf = ('Helvetica',gui_size) # Button Font & size
    tf = ('Helvetica',gui_size) # Text font & size
    mf = ('Helvetica',gui_size) # Menu Font and size
    ts = ('Helvetica',30) # Title Size

    def make_ctl_screen(rfd,rft,rfc, rfg, pfx):
        #sg.theme(theme)
        
        tgt_list = []
        tgt_tots = []
        
        ##### Build the list of all region/fuel targets plus totals ####
        for fuel in rfc['FYD'+'renfuel'] : 
            for region in rfc['FYD'+'genreg'] :
                tgt_list.append(rfc[pfx+region+fuel+'TGT'])
                #rfc[pfx+region+'ALL'+'TGT'] = 0
                
        national_fuel_targets(rfd,rft,rfc, rfg, pfx)
        
        for region in rfc['FYD'+'genreg'] : 
            tgt_list.append(rfc[pfx+region+'ALL'+'TGT'])
        
        for fuel in  rfc['FYD'+'renfuel'] :
            tgt_tots.append(rfc[pfx+'ALL'+fuel+'TGT'])
            
        tgt_tots.append(rfc[pfx+'ALL'+'ALL'+'TGT'])
        

        linedisp = ['Solar Farms Percent              ','Wind Farms Percent              ','Solar Rooftop Percent     ', 'State TOTAL Percent     ']

        menu_def = [['&Grid Resources   ', ['F1 - Grid Batteries', 'F2 - Pumped Hydro', 'F3 - Hydro','F4 - InterConnectors','F5 - Existing Gas Turbines', 'F6 - Build New Gas Turbines', 'F7 - Base Load Generators', 'F8 - In House Batteries','F9 - EV Batteries', 'SUT - Solar Utility', 'SRT - Solar Rooftop', 'WIN - Wind Generation']], ['   &Screen Control', ['Save Targets - Current Code', 'Save Targets - Under New Code', 'Load Saved Targets', loadlist, 'Delete Saved Targets', dellist, 'Graph Controls']] , ['    &Profiles' , ['Save Profile', 'Save With New Code', 'Load Saved Profile', pfx_load_list, 'Delete Saved Profile', pfx_del_list]]] ###['                                                 Exit',['Exit Program']]]
                    
        menu =     [[[sg.MenubarCustom(menu_def, key='-MENU-', font=mf, text_color = 'blue', background_color = 'white')]]]
        
        c1title =  [[sg.Text('Enter State Wide Renewable Targets', justification='center', font=ts, expand_x = True, relief=sg.RELIEF_RIDGE, text_color = 'blue', background_color = 'white')]]
        
        c1colheader=[[sg.T()],
                    [sg.Push(), sg.Push(), sg.T('Start Year ', text_color = 'blue', background_color = 'white' ), sg.Combo(values = rfc['FYD'+'years_in_range'], default_value = start_year, size=(6, 1), key='-START_YEAR-', enable_events=True), sg.Push(), sg.T('Start Month ', text_color = 'blue', background_color = 'white'), sg.Combo(values = rfc['FYD'+'months_in_year'], default_value = start_month, size=(6, 1), key='-START_MONTH-', enable_events=True),sg.Push(), sg.Push()],
                    [sg.T()],
                    [sg.Text("The 5 NEM States", text_color = 'white', font=tf), sg.Push(), sg.T("    NSW          QLD            SA           TAS        VIC         National                      ", text_color = 'white', font=tf)]]
        
        c1griddisp = [[sg.Text(linedisp[i], size = (20,1), font=tf)] + [sg.InputText(tgt_list[j+i*5], size=(8, 1), key=(i, j), enable_events = True, justification = 'right', font=tf) for j in range(5)] + [sg. InputText(tgt_tots[i], size=(8, 1), font=tf, key=f'-NATTOT{i}-',  background_color='blue', disabled = True, justification = 'right')] for i in range(4)]

        c1footer =  [[sg.T()],
                    [sg.Push(),sg.Text('NEM Supply / Demand', size=(20,1), font=tf, justification = 'right', key = '-NEMTOT-'), 
                    sg.Input(0, size=(3,1), font=tf, justification = 'right', k='-NEMTOT-', enable_events = True), sg.Text('%', font=tf, justification = 'right'), sg.Push()],
                    [sg.T()],  
                    [sg.Push(), sg.Button('    Exit     ', font=bf, k='-EXIT-', size = bs), sg.Button(' Clear Gens ', font=bf, k='-CLEARGENS-', size = bs),sg.Button(' Save & Show ', font=bf, k='-SAVESHOW-', size = bs), 
                    sg.Button(' Save & Exit ', font=bf, k='-SAVEEXIT-', size=bs), sg.Button('  AutoCalc  ', font=bf, k='-AUTOCALC-', size=bs), sg.Push()]]
        
        c2title =   [[sg.T(" AUTOBUILD ", justification = 'center', font=ts, text_color = 'green', background_color = 'white')]]
        
        c2autobs  = [[sg.T()],[sg.B("Build Actual Grid", size=bs, font=bf, k='-ACTGRID-')],[sg.B('Renewable Grid', size=bs, font=bf, k='-RENGRID-')], [sg.B('Nuclear Grid', size=bs, font=bf,k='-NUCGRID-')], [sg.B('Auto ReBuild', k='-AUTOREB-', size=bs, font=bf)], [sg.B('Optimiser', k = '-OPTIMISE-', size = bs, font=bf)], [sg.B('Test REN PCs', k = '-RENPC-', size = bs, font=bf)]]
                    
        twocol =    [[sg.Column([[sg.Frame(" Target Entry Screen ", c1title+c1colheader+c1griddisp+c1footer)]]), sg.Column([[sg.Frame(" Auto Grid Builds ", c2title+c2autobs,  expand_y = True, element_justification = 'center')]], vertical_alignment = 'top'), sg.Sizegrip()]]
        
        control_scn_window = sg.Window(f'Renewable Targets and Configuration Control - Current Profile = {pfx}', menu  + twocol , grab_anywhere=True, resizable=True, margins=(0,0), use_custom_titlebar=True, finalize=True, keep_on_top=True)
        
        return control_scn_window

    control_scn_window = make_ctl_screen(rfd, rft, rfc, rfg, pfx)
        
    while True:
        
        def update_target_totals(event, values) :
            fn = " Update Screen Totals for Renewable Tgts "
            
            national_fuel_targets(rfd, rft, rfc, rfg, pfx)
            
            #### Update National ie the Vertical Renewable Totals ####
            for i, region in enumerate(rfc['FYD'+'genreg']) : control_scn_window[(3, i)].update(rfc[pfx+region+'ALL'+'TGT'])
            for i, fuel in enumerate(rfc['FYD'+'renfuel']) : control_scn_window[f'-NATTOT{i}-'].update(rfc[pfx+'ALL'+fuel+'TGT'])
            control_scn_window['-NATTOT3-'].update(rfc[pfx+'ALL'+'ALL'+'TGT'])
                
            control_scn_window.refresh()
     
            return
        
        def write_state_targets() :
            
            cur_obj.execute('select pfx from gbrentgt where pfx = %s group by pfx',[pfx])
            present = cur_obj.fetchone()
            if present == [] or present == None :
                for fuel in ["SUT","WIN","SRT"] :
                    for region in rfc["FYD"+"genreg"] :
                        cur_obj.execute('insert into gbrentgt (pfx, region, fuel, rentgt) values(%s, %s, %s, %s)',[pfx, region, fuel, rfc[pfx+region+fuel+"TGT"]])
                        con_obj.commit()
            else :           
                for fuel in ["SUT","WIN","SRT"] :
                    for region in rfc["FYD"+"genreg"] :
                        cur_obj.execute("update gbrentgt set rentgt = %s where pfx = %s and fuel = %s and region = %s",[rfc[pfx+region+fuel+"TGT"], pfx, fuel, region])
                        con_obj.commit()
                        
            renewable_target_allocation(rfd, rft, rfc, rfg, pfx)
            calc_totals(rfd, rft, rfc, rfg, pfx) 

            return

        event, values = control_scn_window.read()
        
        datacs = values
        
        if event in (None, 'Exit', '-EXIT-','escape'):
            print("[LOG] Clicked Exit!")
            control_scn_window.close()
            break
        
        if event == 'Exit Program' :
            control_scn_window.close()
            exit()
            
        
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            print('============ Event = ', event, ' ==============')
            print('-------- Values Dictionary ', type(event), ' --------')
            for key in values:
                print(key, ' = ', values[key])
                
        if isinstance(event, tuple) : #### This little guy directs the RowByCol Tuple to Update as long as it's valid ###
            if values[event] and values[event][-1] not in ('0123456789') or len(values[event]) > 3 or values[event] == '' :
                control_scn_window[event].update(values[event][:-1])
            else :
                region = rfc['FYD'+'genreg'][int(event[1])]
                fuel = rfc['FYD'+'renfuel'][int(event[0])]
                rfc[pfx+region+fuel+'TGT'] = int(values[event])
                update_target_totals(event, values)
               
        if event == '-CLEARGENS-':
            for gen in rfg['genfuel'][:-4] :
                rfg['stp'] = gen
                gen_destroy(rfd, rft, rfc, rfg, pfx)

            calc_totals(rfd, rft, rfc, rfg, pfx)
            graph_display(rfd, rft, rfc, rfg, pfx)

            for gen in ['SUT','SRT','WIN'] :
                rfg['genfuel'].insert(0,gen)

        if event == '-SAVESHOW-':
            print('>>>>>>>>>>>>>>>>>>>>>>>>> ARRIVED HERE NOTE METHOD $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            if start_year != values['-START_YEAR-'] or start_month != values['-START_MONTH-'] : 
                
                start_year = values['-START_YEAR-'] ; start_month = values['-START_MONTH-']
                rfc['FYD'+'FYDs_initial_start_date'] = values['-START_YEAR-'] + rfc['FYD'+'months_in_year_num'][rfc['FYD'+'months_in_year'].index(values['-START_MONTH-'])][1] + rfc['FYD'+'FYDs_initial_start_date'][6:]   ##### Lengthy cos covert Month Word ie Jun to Number ie NOT 6 but '06' ####
                
                
                print('New Start Date    ',rfc['FYD'+'FYDs_initial_start_date'])

                update_after_start_date_changes(rfd, rft, rfc, rfg, pfx)
                
            update_target_totals(event, values)
            write_state_targets()
            graph_display(rfd, rft, rfc, rfg, pfx)
            
        if event == '-SAVEEXIT-':
            update_target_totals(event, values)
            write_state_targets()
            control_scn_window.close()
            graph_display(rfd, rft, rfc, rfg, pfx)
            break
        
        if event == '-ACTGRID-' :
            rfc['FYD'+'autorun'] = "Y"
            control_scn_window.disappear()
            renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
            calc_totals(rfd, rft,  rfc, rfg, pfx)
            graph_display(rfd, rft,  rfc, rfg, pfx)
            F7(rfd,rft,rfc,rfg,pfx)
            F4(rfd,rft,rfc,rfg,pfx)
            F3(rfd,rft,rfc,rfg,pfx)
            F2(rfd,rft,rfc,rfg,pfx)
            F5(rfd,rft,rfc,rfg,pfx)
            button = control_scn_window['-ACTGRID-']
            button.TKButton.configure(foreground='green')
            control_scn_window.reappear()
            rfc['FYD'+'autorun'] = "N"
            
        if event == '-RENGRID-' :
            rfc['FYD'+'autorun'] = "Y"
            control_scn_window.disappear()
            F8(rfd,rft,rfc,rfg,pfx)
            #F9(rfd,rft,rfc,rfg,pfx)
            F4(rfd,rft,rfc,rfg,pfx)
            F2(rfd,rft,rfc,rfg,pfx)
            F3(rfd,rft,rfc,rfg,pfx)
            F1(rfd,rft,rfc,rfg,pfx)
            F5(rfd,rft,rfc,rfg,pfx)
            #F6(rfd,rft,rfc,rfg,pfx)
            control_scn_window.reappear()
            rfc['FYD'+'autorun'] = "N"
        
        if event == '-NUCGRID-' :
            rfc['FYD'+'autorun'] = "Y"
            control_scn_window.disappear()
            F7(rfd,rft,rfc,rfg,pfx) #### Set for NUclear Only
            F4(rfd,rft,rfc,rfg,pfx)
            F2(rfd,rft,rfc,rfg,pfx)
            F3(rfd,rft,rfc,rfg,pfx)
            F5(rfd,rft,rfc,rfg,pfx)
            control_scn_window.reappear()
            rfc['FYD'+'autorun'] = "N"
            
        if event == '-AUTOREB-' :
            rfc['FYD'+'autorun'] = "Y"
            control_scn_window.disappear()
            # F7(rfd,rft,rfc,rfg,pfx)
            # F4(rfd,rft,rfc,rfg,pfx)
            # F2(rfd,rft,rfc,rfg,pfx)
            # F3(rfd,rft,rfc,rfg,pfx)
            # F5(rfd,rft,rfc,rfg,pfx)
            control_scn_window.reappear()
            rfc['FYD'+'autorun'] = "N"
            
            
        if event == '-OPTIMISE-' :
            rfc['FYD'+'autorun'] = "Y"
            control_scn_window.disappear()
            F7(rfd,rft,rfc,rfg,pfx)
            F4(rfd,rft,rfc,rfg,pfx)
            F2(rfd,rft,rfc,rfg,pfx)
            F3(rfd,rft,rfc,rfg,pfx)
            F5(rfd,rft,rfc,rfg,pfx)
            control_scn_window.reappear()
            rfc['FYD'+'autorun'] = "N"
            
        if event == '-RENPC-' :
            rfc['FYD'+'autorun'] = "Y"
            control_scn_window.disappear()
            rfc['FYD'+'F_code_link'] = [('F8', 'IHB'), ('F4', 'HVI'),('F2','HPU'), ('F3', 'HYD'), ('F1', 'BAT'), ('F5','GOC')]   
            #### ('F6','NGT'),('F7','FIX'), ('F9', 'EVB'), ,  
            counter = 0
            cur_obj.execute('update gbstg set status = CASE when genname = "DO NOT REMOVE" then "L" else "X" end where genfuel = "BAT"')
            
                               
            run_no = '052123'  #### Month, Day, Hour
            for region in rfc['FYD'+'genreg'] :
                if region == 'TAS' : continue
                for size in range(105, 130, 5) :
                    for win in range(40, size - 10, 10) :
                        sun = size - win
                            
                        rfc[pfx+region+"SUT"+"TGT"] = sun
                        rfc[pfx+region+"WIN"+"TGT"] = win
                        rfc[pfx+region+"SRT"+"TGT"] = srt = 100 + sun
                    
                        renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
                        calc_totals(rfd, rft,  rfc, rfg, pfx)
                        
                        b4_gap = int(rfd[pfx+region+'GAP'].sum() / 4)

                        hour_battery = round(rfd[pfx+region+'DEM'].sum() / 365 / 24 / 4) * 1000
                        
                        for hour in range(1, 5, 1) : 
                            bat_cap = hour_battery * hour
                            bat_gwo = bat_cap / 2
                            
                            cur_obj.execute('update gbstg set storage = %s, gwout = %s where genregion = %s and genfuel = "BAT" and genname = "DO NOT REMOVE"',[bat_cap, bat_gwo, region])
                            
                            for fuel in rfc['FYD'+'F_code_link'] :
                                fuel_key = fuel[0]
                                fuel_code = fuel[1]
                                
                                rfc[pfx+"ALL"+fuel_code+"done"] = "N"
                                to_call_func = globals()[fuel_key]
                                to_call_func(rfd, rft,  rfc, rfg, pfx) #### Cals the function called by fuel_key
                                renewable_target_allocation(rfd, rft,  rfc, rfg, pfx)
                                calc_totals(rfd, rft,  rfc, rfg, pfx)

                            after_gap = int(rfd[pfx+region+'GAP'].sum() / 4)
                            
                            ihb_cap = rfc[pfx+region+'IHB'+'init_storage']
                            
                            goc_gwh = rfd[pfx+region+'GOC'].sum() / 4 / 365

                            cur_obj.execute('insert into zzrenpc (region, size, win, sun, srt, b4_gap, after_gap, run_no, bat_cap, bat_gwo, ihb_cap, goc_gwh) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',[region, size, win, sun, srt, b4_gap, after_gap, run_no, bat_cap, bat_gwo, ihb_cap, goc_gwh])
                            con_obj.commit()
                            
                            for fuel in rfc['FYD'+'F_code_link'] :
                                rfg['stp'] = fuel[1]
                                gen_destroy(rfd, rft, rfc, rfg, pfx)
                                
                        counter += 1       
                        print(counter, region, size, win, sun)
                        
                rfc[pfx+region+"SUT"+"TGT"] = 40
                rfc[pfx+region+"WIN"+"TGT"] = 60
                rfc[pfx+region+"SRT"+"TGT"] = 150


            cur_obj.execute('update gbstg set status = CASE when genname != "DO NOT REMOVE" then "L" else "X" end where genfuel = "BAT"')

            control_scn_window.reappear()
            rfc['FYD'+'autorun'] = "N"
            
            
            

##### THIS IS THE MAIN RESOURCE control_scn_window AND TURNS GENERATORS ON AND OFF #####
        if event in ['F1','F2','F3','F4','F5','F6','F7','F8','F9'] :
            control_scn_window.disappear()

        if event == "F1 - Grid Batteries" :
            F1(rfd,rft,rfc,rfg,pfx)
        
        if event == "F2 - Pumped Hydro" :
            F2(rfd,rft,rfc,rfg,pfx)

        if event == "F3 - Hydro" :
            F3(rfd,rft,rfc,rfg,pfx)

        if event == "F4 - InterConnectors" :
            F4(rfd,rft,rfc,rfg,pfx)

        if event == "F5 - Existing Gas Turbines" :
            F5(rfd,rft,rfc,rfg,pfx)

        if event == "F6 - Build New Gas Turbines" :
            F6(rfd,rft,rfc,rfg,pfx)

        if event == "F7 - Base Load Generators" :
            F7(rfd,rft,rfc,rfg,pfx)

        if event == "F8 - In House Batteries" :
            F8(rfd,rft,rfc,rfg,pfx)

        if event == "F9 - EV Batteries" :
            F9(rfd,rft,rfc,rfg,pfx)
        
        if event in ['F1','F2','F3','F4','F5','F6','F7','F8','F9'] :
            control_scn_window.reappear()
            
        
        if event == 'Save Targets - Current Code' :
            
            #update_target_totals(event, values)
            write_state_targets()
            graph_display(rfd,rft,rfc,rfg,pfx)

        if event == 'Save Targets - Under New Code' :
            
            datacs = values #### values is a dictionary containing tuple pair keys (i,j) for the targets in the CNTL screen
            
            def save_new_code() :
                
                se = [[sg.T()],
                    [sg.T('Enter 3 Letter Code and Name', justification='center', font=ts, expand_x = True, relief=sg.RELIEF_RIDGE, text_color = 'blue', background_color = 'white',size = (25,1))],
                    [sg.T()],
                    [sg.Column([[sg.Frame(' Code & Name Entry ', [[sg.T()],
                    [sg.T("Enter 3 Letter Code    : "), sg.I('', size=(6,1), font=tf, justification = 'left', k='-SECODE-', enable_events = True)],
                    [sg.T('Enter Screen Name     : '), sg.I('', size=(16,1), font=tf, justification = 'left', k='-SENAME-', enable_events = True)],
                    [sg.T('Status                         : '), sg.Combo(['L','X'], default_value = 'L' , size=(2,1), font=tf,  k='-SESTATUS-', enable_events = True)],
                    [sg.T()]])]], justification = 'center')],
                    [sg.T()],
                    [sg.P(),sg.B('Exit', size = bs, k='-SEEXIT-', enable_events = True),sg.B('SAVE', size = bs, k='-SESAVE-', enable_events = True), sg.P()]]

                sew = sg.Window('Manage Enteries', se,  grab_anywhere=True, resizable=True, finalize=True, keep_on_top=True)
                
                return sew
            
            sew = save_new_code()
            
            while True :
                
                def save_code_SQL() :
                    
                    sqlparams = [values['-SECODE-'],values['-SENAME-'], dill.dumps(datacs),values['-SESTATUS-']]
                
                    cur_obj.execute('insert into gbscreens (scrcode, scrname, scrval, status) values(%s,%s,%s,%s)',sqlparams)
                    con_obj.commit()
                    
                    loadlist.append(sep.join([values['-SECODE-'],values['-SENAME-'],values['-SESTATUS-']]))
                    
                    return
                
                event, values = sew.read()
                
                if event in (None, 'Exit', '-EXIT-', '-SEEXIT-','esc') :
                    sew.close()
                    break
                
                if len(values['-SECODE-']) > 3 :
                    sew['-SECODE-'].update(values['-SECODE-'][:-1])

                if event == '-SECODE-' :
                    sew['-SECODE-'].update(values['-SECODE-'].upper())
                    if len(values['-SECODE-']) > 3 :
                        sew['-SECODE-'].update(values['-SECODE-'][:-1])

                
                if event == '-SESAVE-' :
                    save_code_SQL()
                    sew.close()
                    control_scn_window.refresh()
                    break
            
        if event in loadlist :
            
            sqlid = event.split('-')[2]
            
            cur_obj.execute('select scrval from gbscreens where sqlid = %s',[sqlid])
            scrval = cur_obj.fetchone()[0]
            
            rentgts = dill.loads(scrval)
            
            for key in rentgts.keys() :
                control_scn_window[key].update(rentgts[key])
            control_scn_window.refresh()
            
            
        if event in dellist :
            
            sqlid = event.split('-')[2]
                
            cur_obj.execute('delete from gbscreens where sqlid = %s',[sqlid])
            con_obj.commit()
            
            dellist = [entry for entry in dellist if entry != event]
            loadlist = [entry for entry in loadlist if entry != str(event)+'-Delete']

            control_scn_window.refresh()

        if event == 'Graph Controls' :
            main_graph_control(rfd,rft,rfc,rfg,pfx)

        if event == 'Save Profile' :
            pfx_load_list, pfx_del_list = main_pfx_control(rfd, rft, rfc, rfg, pfx, event, values, pfx_load_list, pfx_del_list)
            
        if event == 'Save With New Code' :
            pfx_load_list, pfx_del_list = main_pfx_control(rfd, rft, rfc, rfg, pfx, event, values, pfx_load_list, pfx_del_list)
            
        if event in pfx_load_list :
            pfx_load_list, pfx_del_list = main_pfx_control(rfd, rft, rfc, rfg, pfx, event, values, pfx_load_list, pfx_del_list)
            pfx=rfg['pfx']
            print("Does this give us a new PFX ",pfx)
            
        if event in pfx_del_list :
            pfx_load_list, pfx_del_list = main_pfx_control(rfd, rft, rfc, rfg, pfx, event, values, pfx_load_list, pfx_del_list)

    return
            
