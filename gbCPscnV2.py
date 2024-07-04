# gbCPscnV2

# Runs the Prefix or Profile  Save / Load / Add / Delete

from gbGFuncsV2 import*
from gbGRunV2 import*
from gbBaseV2 import*
from gbFfuncsV2 import*
import numpy as np
import PySimpleGUI as sg
import dill as dill

import mysql.connector
con_obj = mysql.connector.connect(host="localhost", user="root", passwd="Thomas01$", database="etreports")
cur_obj = con_obj.cursor()
con_obj.autocommit = True

def main_pfx_control(rfd, rft, rfc, rfg, pfx, event, values, pfx_load_list, pfx_del_list) :
    fn = " Profile Control   "

    sep='-'
    
    gui_size = 15
    bs = (15,1) # Button size
    bf = ('Helvetica',gui_size) # Button Font & size
    tf = ('Helvetica',gui_size) # Text font & size
    mf = ('Helvetica',gui_size) # Menu Font and size
    ts = ('Helvetica',30) # Title Size
    
    
    def filekeys(rfd, rft, rfc, rfg, pfx, event, values) :
        
        filekeys = []

        for i, pfxfile in enumerate([rfd, rft, rfc, rfg]) :
            flist = ['rfd','rft','rfc','rfg']
            for key in pfxfile.keys() :
                filekeys.append([flist[i], str(key)])
            print(filekeys,'No of Entries in SQL', len(filekeys))
        
        return filekeys
    
    def pfx_del() :
        
        del_pfx = event[:3]
        
        cur_obj.execute('delete from gb_pfx_store where pfx = %s',[del_pfx])
        con_obj.commit()

    def pfx_save(rfd,rft,rfc,rfg,pfx, event, values) :
        
        if pfx_load_list != [] : pname = [str(name.split('-')[1]) for name in pfx_load_list if name[:3] == pfx]
        else : pname = ['None Saved']
        if pname == [] : pname = ['NA']

        scount = 0
        
        savew = [[sg.Frame('' , [[sg.T('Profile Save Screen', font = ts, text_color = 'blue', background_color = 'white', expand_x = True, justification = 'center')],
                [sg.T()],
                [sg.T(f'This Will Overwrite Any Saved Profiles Belonging To', pad = 20)],
                [sg.T(f'Your Current Profile = {pfx}')],
                [sg.Text('Else [EXIT] and Save Under a Different Code')],
                [sg.T()],
                [sg.B('Exit', key = '-EXIT-', enable_events = True, size = bs)],
                [sg.T()],
                [sg.T(f'Continue to Save {pfx}', font = ts, text_color = 'blue', background_color = 'white', expand_x = True, justification = 'center')],
                [sg.T()],
                [sg.T('Save As Profile Name : '), sg.Input(default_text = pname[0], size = (15,1), enable_events = True , key = '-PNAME-')],
                [sg.T()],
                [sg.T(f'Save Counter = scount', key = '-SCOUNT-', enable_events = True)],
                [sg.T()],
                [sg.P(), sg.B('Exit', size = bs, key = '-SEXIT-', enable_events = True), sg.P(), sg.B('Save', key = '-SAVE-', enable_events = True, size = bs),sg.P()]],
                element_justification='center', pad = 10)]]
        
        pfx_save_w = sg.Window('Profile Save Screen', savew,  default_button_element_size = bs, grab_anywhere=True, resizable=True, finalize=True, keep_on_top=True)

        while True :
            
            sevent, svalues = pfx_save_w.read()
            
            print(sevent,"   ", svalues)
            
            if sevent in ['sg.Logout','exit','-EXIT-', None,'-SEXIT-'] :
                pfx_save_w.close()
                break     

            if sevent == '-SAVE-' :
                
                pfx_del()
                
                file_key_list = filekeys(rfd, rft, rfc, rfg, pfx, event, values)
                
                for key in file_key_list :
                    
                    if key[0] == 'rfd' : fdict = rfd
                    if key[0] == 'rft' : fdict = rft
                    if key[0] == 'rfc' : fdict = rfc
                    if key[0] == 'rfg' : fdict = rfg
                    
                    if key[1][:3] == pfx :
                        
                        sqlparams = [pfx, svalues['-PNAME-'], 'L' , key[0], key[1], dill.dumps(fdict[key[1]])] 
                        cur_obj.execute('insert into gb_pfx_store (pfx, pfx_name, status, dname, dkey, dvals) values(%s,%s,%s,%s,%s,%s)',sqlparams)
                        con_obj.commit()
                        
                        scount += 1
                        pfx_save_w['-SCOUNT-'].update(f'Save Counter = {scount}') 
                        pfx_save_w.refresh()
                        
                pfx_save_w['-SCOUNT-'].update(f'Save Counter = {scount} - Finished') 
                
                pfx_save_w.refresh()
                
                rfc[pfx+'pfx_name'] = svalues['-PNAME-']
                if sep.join([pfx, rfc[pfx+'pfx_name'], 'L']) not in pfx_load_list :  pfx_load_list.append(sep.join([pfx, rfc[pfx+'pfx_name'], 'L']))
                if sep.join([pfx, rfc[pfx+'pfx_name'], 'L']) not in pfx_del_list : pfx_del_list.append(sep.join([pfx, rfc[pfx+'pfx_name'], 'L']))
                
                
                print(pfx_load_list, pfx_del_list)
                                    
        return pfx_load_list, pfx_del_list
    
    def pfx_add(rfd,rft,rfc,rfg,pfx, event, values) :
        acount = 0
        pfx_addscr = [[sg.T()],
                    [sg.T('Enter 3 Letter Code and Name', justification='center', font=ts, expand_x = True, relief=sg.RELIEF_RIDGE, text_color = 'blue', background_color = 'white',size = (25,1))],
                    [sg.T()],
                    [sg.Column([[sg.Frame(' Code & Name Entry ', [[sg.T()],
                    [sg.T("Enter New 3 Letter Code  : ", key = '-E3LC-', enable_events = True), sg.I('', size=(5,1), font=tf, justification = 'left', k='-PFXCODE-', enable_events = True)],
                    [sg.T('', key = '-PFXDUP-', enable_events = True, justification = 'center', text_color = 'red')],
                    [sg.T('Enter Profile Name        : '), sg.I('', size=(15,1), font=tf, justification = 'left', k='-PFXNAME-', enable_events = True)],
                    [sg.T()],
                    [sg.T(f'Add Counter = {acount}', key = '-ACOUNT-', enable_events = True, justification = 'center')],
                    [sg.T()],
                    [sg.T()]])]], justification = 'center')],
                    [sg.T()],
                    [sg.P(),sg.B('EXIT', size = bs, key = '-PFXEXIT-', enable_events = True),sg.B('SAVE', size = bs, key = '-PFXSAVE-', enable_events = True), sg.P()]]

        pfx_add_w = sg.Window('Save to New Code', pfx_addscr,  grab_anywhere = True, resizable = True, finalize = True, keep_on_top = True)
        
        while True :
            
            aevent, avalues = pfx_add_w.read()
            
            if aevent in ['sg.Logout','exit','-EXIT-', None,'-PFXEXIT-'] :
                pfx_add_w.close()
                break
            
            if aevent == '-PFXCODE-' : 
                pfx_add_w['-PFXCODE-'].update(avalues['-PFXCODE-'].upper())
                if len(avalues['-PFXCODE-']) > 3 : pfx_add_w['-PFXCODE-'].update(avalues['-PFXCODE-'][:-1])
                if avalues['-PFXCODE-'] in pfx_load_list[:3] :  pfx_add_w['-PFXDUP-'].update('Duplicate Code')
            
                pfx_add_w.refresh()
                   
            if aevent == '-PFXSAVE-' :
                
                file_key_list = filekeys(rfd, rft, rfc, rfg, pfx, event, values)
                
                for key in file_key_list :
                    
                    if key[1][:3] != pfx : continue
                    
                    if key[0] == 'rfd' : fdict = rfd
                    if key[0] == 'rft' : fdict = rft
                    if key[0] == 'rfc' : fdict = rfc
                    if key[0] == 'rfg' : fdict = rfg
                    
                    sqlparams = [avalues['-PFXCODE-'], avalues['-PFXNAME-'], 'L' , key[0], key[1], dill.dumps(fdict[key[1]])] 
                    cur_obj.execute('insert into gb_pfx_store (pfx, pfx_name, status, dname, dkey, dvals) values(%s,%s,%s,%s,%s,%s)',sqlparams)
                    con_obj.commit()
                    
                    acount += 1
                        
                    pfx_add_w['-ACOUNT-'].update(f'Add Counter = {acount}') 
                    
                    pfx_add_w.refresh()
                
            for region in rfc['FYD'+'genreg'] :
                for fuel in rfc['FYD'+'renfuel'] :
                        rfc[avalues['-PFXCODE-']+region+fuel+'TGT'] = rfc[pfx+region+fuel+'TGT']
                                

                
                pfx_add_w['-ACOUNT-'].update(f'Add Counter = {acount} Finished') 
                
                pfx_add_w.refresh()

        

    def pfxload(rfd,rft,rfc,rfg,pfx, event, values) :
        
        load_pfx = event.split(sep)[0]
        print(load_pfx)
        
        cur_obj.execute('select pfx, dname, dkey, dvals from gb_pfx_store where pfx = %s',[load_pfx])
        pfxdb = cur_obj.fetchall()
        for i, dbline in enumerate(pfxdb) :
            pfx = str(dbline[0])
            dname = str(dbline[1])
            dkey = str(dbline[2])
            
            if dname == 'rfd' : fdict = rfd
            if dname == 'rft' : fdict = rft
            if dname == 'rfc' : fdict = rfc
            if dname == 'rfg' : fdict = rfg
            
            fdict[pfx+dkey[3:]] = dill.loads(dbline[3])
            
            sg.one_line_progress_meter(f'Loading Prefix - {load_pfx}', i + 1 , len(pfxdb), orientation='h', size = (125,50), bar_color = ('blue', 'white'), keep_on_top = True, no_button = True)
            
            print( 'Dict Key =  ', pfx+dkey[3:])
        
        rfg['pfx'] = pfx
            
       
       
    if event == 'Save Profile' : pfx_save(rfd,rft,rfc,rfg,pfx, event, values)
    if event in pfx_load_list : pfxload(rfd,rft,rfc,rfg,pfx, event, values)
    if event == 'Save With New Code' : pfx_add(rfd,rft,rfc,rfg,pfx, event, values)
    if event in pfx_del_list : pfx_del()
    
    return pfx_load_list, pfx_del_list





