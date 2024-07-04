# gbGRButV2


####   From working Example are the Matplot imports

import matplotlib
matplotlib.use('TkAgg')
from tkinter import ttk
import matplotlib.backend_managers
from matplotlib.backend_tools import ToolBase, ToolToggleBase
import PySimpleGUI as sg


from gbBaseV2 import *
from gbUtilsV2 import *
from gbGRTablesV2 import *

def add_TB_buttons(rfd, rft, rfc, rfg, pfx) :
    
    gui_size = 15
    bs = (15,1) # Button size
    bf = ('Helvetica',gui_size) # Button Font & size
    tf = ('Helvetica',gui_size) # Text font & size
    mf = ('Helvetica',gui_size) # Menu Font and size
    ts = ('Helvetica',30) # Title Size

    from gbGRunV2 import graph_display

    
    fig = rfc['fig']

    rfc['plt'].rcParams['toolbar'] = 'toolmanager'
    
    #print("Matplotlib plt backend: {}".format(plt.get_backend()))

    class ListTools(ToolBase):
        """List all the tools controlled by the `ToolManager`."""
        default_keymap = 'm'  # keyboard shortcut
        description = 'List Tools'

        def trigger(self, *args, **kwargs):
            print('_' * 80)
            fmt_tool = "{:12} {:45} {}".format
            print(fmt_tool('Name (id)', 'Tool description', 'Keymap'))
            print('-' * 80)
            tools = self.toolmanager.tools
            for name in sorted(tools):
                if not tools[name].description:
                    continue
                keys = ', '.join(sorted(self.toolmanager.get_tool_keymap(name)))
                print(fmt_tool(name, tools[name].description, keys))
            print('_' * 80)
            fmt_active_toggle = "{!s:12} {!s:45}".format
            print("Active Toggle tools")
            print(fmt_active_toggle("Group", "Active"))
            print('-' * 80)
            for group, active in self.toolmanager.active_toggle.items():
                print(fmt_active_toggle(group, active))



    class StgToggle(ToolToggleBase) :
        """Show lines with a given gid."""
        default_keymap = 'S'
        description = 'Show Storage Levels'
        default_toggled = False
        pfx = rfg['pfx']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def enable(self, *args) :
            pfx = rfg['pfx']
            rfc[pfx+'show_battery'] = 'Y'
            if pfx != 'FYD' : graph_display(rfd, rft, rfc, rfg, pfx)

        def disable(self, *args) :
            pfx = rfg['pfx']
            rfc[pfx+'show_battery'] = 'N'
            if pfx != 'FYD' : graph_display(rfd, rft, rfc, rfg, pfx)

    class LegToggle(ToolToggleBase) :
        """Legend Bold and Double Size"""
        default_keymap = 'L'
        description = 'Show Large Legend'
        default_toggled = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def enable(self, *args) :
            rfg['legsize'] = 20
            rfg['legbold'] = 'bold'
            graph_display(rfd, rft, rfc, rfg, pfx)

        def disable(self, *args) :
            rfg['legsize'] = 10
            rfg['legbold'] = 'normal'
            graph_display(rfd, rft, rfc, rfg, pfx)
            
    class DemandLineToggle(ToolToggleBase) :
        """Show Thicker Demand line """
        default_keymap = 'D'
        description = 'Show Thicker Demand Line'
        default_toggled = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def enable(self, *args) :
            rfg['demline'] = 150
            calc_totals(rfd, rft, rfc, rfg, pfx)
            graph_display(rfd, rft, rfc, rfg, pfx)

        def disable(self, *args) :
            rfg['demline'] = 300
            calc_totals(rfd, rft, rfc, rfg, pfx)
            graph_display(rfd, rft, rfc, rfg, pfx)

    class GraphTableToggle(ToolToggleBase) :
        """Display Graph Table"""
        default_keymap = 'T'
        description = 'Display Graph Table'
        default_toggled = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def enable(self, *args) :
            rfg["graph_table"] = 'Y'
            rfg["graph_table_size"] = 15
            graph_display(rfd, rft, rfc, rfg, pfx)

        def disable(self, *args) :
            rfg["graph_table"] = 'N'
            rfg["graph_table_size"] = 10
            graph_display(rfd, rft, rfc, rfg, pfx)

    class GapExsTableToggle(ToolToggleBase) :
        """Gap or Excess Analyse Table"""
        default_keymap = 'E'
        description = 'Gap or Excess Analyse Table'
        default_toggled = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def enable(self, *args) :
            rfg['graph_analysis_table'] = 'Excess'
            graph_display(rfd, rft, rfc, rfg, pfx)

        def disable(self, *args) :
            rfg['graph_analysis_table'] = 'Gap'
            graph_display(rfd, rft, rfc, rfg, pfx)
            
    class GapExsSizeToggle(ToolToggleBase) :
        """Gap or Excess Analyse Table Size"""
        default_keymap = 'A'
        description = 'Gap or Excess Analyse Table Size'
        default_toggled = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def enable(self, *args) :
            rfg['graph_analysis_table_size'] = 15
            graph_display(rfd, rft, rfc, rfg, pfx)

        def disable(self, *args) :
            rfg['graph_analysis_table_size'] = 10
            graph_display(rfd, rft, rfc, rfg, pfx)
       
    class CostTableToggle(ToolToggleBase) :
        """ Graph Cost Table - Build Cost + 25yr Cost """
        #default_keymap = 'A'
        description = 'Gap or Excess Analyse Table Size'
        default_toggled = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def enable(self, *args) :
            rfg['rf_cost_table'] = 'Y'
            rfg['table_request'] = 'total'
            graph_display(rfd, rft, rfc, rfg, pfx)

        def disable(self, *args) :
            rfg['rf_cost_table'] = 'N'
            graph_display(rfd, rft, rfc, rfg, pfx)

    class L_lcoeTableToggle(ToolToggleBase) :
        """ Graph Cost Table - Use Lazards LCOE Cost """
        #default_keymap = 'A'
        description = 'Cost Table uses LCOE from Lazards'
        default_toggled = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def enable(self, *args) :
            rfg['rf_cost_table'] = 'Y'
            rfg['table_request'] = 'L_lcoe'
            graph_display(rfd, rft, rfc, rfg, pfx)

        def disable(self, *args) :
            rfg['rf_cost_table'] = 'N'
            graph_display(rfd, rft, rfc, rfg, pfx)

    class C_lcoeTableToggle(ToolToggleBase) :
        """ Graph Cost Table - Use Lazards LCOE Cost """
        #default_keymap = 'A'
        description = 'Cost Table uses LCOE from Lazards'
        default_toggled = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def enable(self, *args) :
            rfg['rf_cost_table'] = 'Y'
            rfg['table_request'] = 'C_lcoe'
            graph_display(rfd, rft, rfc, rfg, pfx)

        def disable(self, *args) :
            rfg['rf_cost_table'] = 'N'
            graph_display(rfd, rft, rfc, rfg, pfx)

    class DetailCOETableToggle(ToolToggleBase) :
        """ Graph Cost Table - Use Lazards LCOE Cost """
        #default_keymap = 'A'
        description = 'Cost Table uses LCOE from Lazards Breakdown of Parts'
        default_toggled = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def enable(self, *args) :
            rfg['rf_cost_table'] = 'Y'
            rfg['table_request'] = 'sub_total'
            graph_display(rfd, rft, rfc, rfg, pfx)
            
        def disable(self, *args) :
            rfg['rf_cost_table'] = 'N'
            graph_display(rfd, rft, rfc, rfg, pfx)

##### BELOW HERE ARE FUNCTIONS NOT TOGGLE BUTTONS  #####

    class DateLookup(ToolBase) :
        """Enter Two Dates to Filter Graph By."""
        #default_keymap = 'm'  # keyboard shortcut
        description = 'Enter Filter Dates'
        
        ###### wants the default Month / Day / Year
        
        def trigger(self, *args, **kwargs) :
            
            default_start_date = (rfc['FYD'+'FYDs_initial_start_date'][4:6], rfc['FYD'+'FYDs_initial_start_date'][6:8], rfc['FYD'+'FYDs_initial_start_date'][2:4])
            default_end_date = (rfc['FYD'+'FYDs_initial_start_date'][4:6], rfc['FYD'+'FYDs_initial_start_date'][6:8], str(int(rfc['FYD'+'FYDs_initial_start_date'][2:4])+1))
                
            print(default_start_date, default_end_date)    
            
            date_entry_title = [[sg.P(), sg.Text('Enter the Start - Finish Dates to View', size=(30, 1), font=ts, justification='center', text_color = 'blue', background_color = 'white'), sg.P()],
                [sg.T()]]
            data_entry = [[sg.Column([[sg.Frame('',[[sg.T('Date Format  DD-MM-YY ', justification='center')],
                [sg.Text('Start Date   ', size=(10, 1)), sg.Input(key='-START-', size=(10, 1), font = tf, focus = False, tooltip = 'DD-MM-YY'), sg.CalendarButton('Calendar', target='-START-', format='%d-%m-%y')],  #### , default_date_m_d_y = default_start_date
                [sg.Text('Finish Date  ', size=(10, 1)), sg.Input(key='-FINISH-', size=(10, 1), font = tf, focus = False, tooltip = 'DD-MM-YY'), sg.CalendarButton('Calender', target='-FINISH-', format='%d-%m-%y')]], element_justification = 'center')]], justification = 'center')]] #### , default_date_m_d_y = default_end_date
            button_footer =    [[sg.T()],
                [sg.P(), sg.Button('Cancel', size = bs), sg.P(), sg.Button('OK', size = bs), sg.P()]]

            # Create the window
            date_entry_w = sg.Window('Date Input', date_entry_title + data_entry + button_footer, finalize = True)

            # Event loop to process events and get the values of the inputs
            while True:
                event, values = date_entry_w.read()
                if event == sg.WIN_CLOSED or event == 'Cancel':  # If user closes window or clicks Cancel
                    date_entry_w.close()
                    break
                
                # Validate the dates
                if not is_valid_date(values['-START-']) : 
                    sg.popup('Invalid Start Date format. Please enter the date in DD-MM-YY format.', button_justification = 'center')
                    continue   
                if not is_valid_date(values['-FINISH-']) : 
                    sg.popup('Invalid Finish Date format. Please enter the date in DD-MM-YY format.', button_justification = 'center')
                    continue
                
                if event == 'OK':  # If user clicks OK
                    start_date = values['-START-'].replace('-', '')
                    finish_date = values['-FINISH-'].replace('-', '')
                    start_date  = '20'+start_date[4:6]+start_date[2:4]+start_date[:2]+'0000'
                    finish_date = '20'+finish_date[4:6]+finish_date[2:4]+finish_date[:2]+'2359'
                    
                    
                    print(f'Start Date: {start_date}')
                    print(f'Finish Date: {finish_date}')

                    rfg['startpos'] = start_pos = position_from_date_sort(start_date, ipstart_date = rfc['FYD'+'FYDs_initial_start_date'])
                    rfg['endpos'] = end_pos = position_from_date_sort(finish_date, ipstart_date = rfc['FYD'+'FYDs_initial_start_date']) + 1
                    if end_pos - start_pos < rfc['FYD'+'elements'] : rfc["zoom"] = 'Y'                 
                    print(start_pos, end_pos, rfc['FYD'+'FYDs_initial_start_date'])
                    
                    date_entry_w.close()
                    graph_display(rfd, rft, rfc, rfg, pfx)
                    
                    break

    class CompareCostByPFX(ToolBase) :
        
        """Enter Two Dates to Filter Graph By."""
        #default_keymap = 'm'  # keyboard shortcut
        description = 'Enter Filter Dates'
        
        def trigger(self, *args, **kwargs) :
            
            pfx_list = get_current_pfx_list(rfd)
            
            date_entry_title = [[sg.P(), sg.Text("Enter the Two Grid Prefix's to Compare", size=(30, 1), font=ts, justification='center', text_color = 'blue', background_color = 'white'), sg.P()],
                [sg.T()]]
            data_entry = [[sg.Column([[sg.Frame('',[[sg.Text('Grid Prefix = 3 Letter Code ', justification='center', )],
                [sg.Text('First Grid Prefix   ', size=(15, 1)), sg.Combo(pfx_list, key='-PFX1-', size=(5, 1), font = tf, tooltip = '3 Letter Prefix')],  #### , default_date_m_d_y = default_start_date
                [sg.Text('Second Grid Prefix  ', size=(15, 1)), sg.Combo(pfx_list, key='-PFX2-', size=(5, 1), font = tf, tooltip = '3 Letter Prefix')]], element_justification = 'center')]], justification = 'center')]] #### , default_date_m_d_y = default_end_date
            button_footer = [[sg.T()],
                [sg.P(), sg.Button('Cancel', size = bs), sg.P(), sg.Button('OK', size = bs), sg.P()]]

            # Create the window
            date_entry_w = sg.Window('Compare Two Grids for Cost ', date_entry_title + data_entry + button_footer, finalize = True)

            # Event loop to process events and get the values of the inputs
            while True:
                event, values = date_entry_w.read()
                if event == sg.WIN_CLOSED or event == 'Cancel' or event == 'escape':  # If user closes window or clicks Cancel
                    date_entry_w.close()
                    break
                
                # Validate the pfx values
                if values['-PFX1-'] not in pfx_list : 
                    sg.popup('The First Grid Prefix must come from the Drop Down List ')
                    continue   
                if values['-PFX2-'] not in pfx_list : 
                    sg.popup('The Second Grid Prefix must come from the Drop Down List ')
                    continue   
                
                if event == 'OK':  # If user clicks OK
                    
                    pfx1 = rfg['pfx1'] = values['-PFX1-']
                    pfx2 = rfg['pfx2'] = values['-PFX2-']
                    rfg['rf_compare_table'] = 'Y'
                    rfg['rf_compare_request'] = 0
                    rfg['rf_cost_table'] = 'N'
                    rfg['rf_compare_totals'] = 'N'
                    rfg['rf_table_request'] = 'compare'
                    
                    date_entry_w.close()
                    graph_display(rfd, rft, rfc, rfg, pfx)
                    
                    break
        
    class PFXswitch(ToolBase) :
        
        def trigger(self, *args, **kwargs) :
            
            cur_pfx_list = get_current_pfx_list(rfd)
            
            pfx_layout = [[sg.P(), sg.Text('Select PFX to Switch', size=(20, 1), font=ts, justification='center', text_color = 'blue', background_color = 'white'), sg.P()],
                          [sg.T()],
                          [sg.P(), sg.Combo(cur_pfx_list, key='-PFX-', default_value = rfg['pfx'], size=(5, 1), font = tf, tooltip = 'Select Prefix'), sg.P()],
                          [sg.T()],
                          [sg.P(), sg.B('OK', size = bs, key = '-OK-'), sg.P()]]
            
            pfx_window = sg.Window('Select PFX', pfx_layout, finalize = True, keep_on_top = True)
            
            while True :
                
                event, values =  pfx_window.read()
                
                if event == sg.WIN_CLOSED or event == 'Cancel' or event == 'escape':  # If user closes window or clicks Cancel
                    pfx_window.close()
                    break
            
                if event == '-OK-' :
                    
                    if values['-PFX-'] in cur_pfx_list : pfx = rfg['pfx'] = values['-PFX-']
                    
                    pfx_window.close()
                    
                    graph_display(rfd, rft, rfc, rfg, pfx)
                    
                    break
            
    class CompareOptions(ToolBase):
        """A tool to add a combo box to the toolbar."""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.combo = None

        def trigger(self, sender, event, data = None) :
            if self.combo is None:
                self.combo = ttk.Combobox(self.figure.canvas.manager.toolbar, 
                                    values = rfg['rf_compare_options'])
                self.combo.pack(side = 'left')
                self.combo.set('Capital Cost')
                self.combo.bind("<<ComboboxSelected>>", self.on_select)


        def on_select(self, event, data = None):
            #selected = self.combo.get()
            rfg['rf_compare_request'] = rfg['rf_compare_options'].index(self.combo.get())
            if self.combo.get() != 'Exit' :
                rfg['rf_compare_table'] = 'Y'
                rfg['rf_cost_table'] = 'N'
                rfg['rf_compare_totals'] = 'N'
                rfg['rf_table_request'] = 'compare'
                
            if self.combo.get() == 'Exit' :
                rfg['rf_compare_table'] = 'N'
                rfg['rf_table'].remove()
                self.combo.set('')
            
            graph_display(rfd, rft, rfc, rfg, pfx)

    class CompareTotals(ToolBase):
        """A tool to add the Totals for  rfg['rf_compare_options'] each option choice."""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def trigger(self, *args, **kwargs) :
            
            rfg['rf_compare_totals'] = 'Y'
            rfg['rf_cost_table'] = 'N'
            rfg['rf_compare_table'] = 'N'
            rfg['rf_table_request'] = 'compare'
            
            graph_display(rfd, rft, rfc, rfg, pfx)




    fig.canvas.manager.toolmanager.add_tool('STG', StgToggle) 
    fig.canvas.manager.toolmanager.add_tool('PFX', PFXswitch) 
    fig.canvas.manager.toolmanager.add_tool('LEG', LegToggle)  
    fig.canvas.manager.toolmanager.add_tool('DL1', DemandLineToggle) 
    fig.canvas.manager.toolmanager.add_tool('GRT', GraphTableToggle) 
    fig.canvas.manager.toolmanager.add_tool('GEA', GapExsTableToggle) 
    fig.canvas.manager.toolmanager.add_tool('GES', GapExsSizeToggle) 
    fig.canvas.manager.toolmanager.add_tool('DATE', DateLookup) 
    fig.canvas.manager.toolmanager.add_tool('COST', CostTableToggle) 
    fig.canvas.manager.toolmanager.add_tool('L_lcoe', L_lcoeTableToggle)
    fig.canvas.manager.toolmanager.add_tool('C_lcoe', C_lcoeTableToggle) 
    fig.canvas.manager.toolmanager.add_tool('DCOE', DetailCOETableToggle) 
    fig.canvas.manager.toolmanager.add_tool('CCBP', CompareCostByPFX) 
    fig.canvas.manager.toolmanager.add_tool('OPTS', CompareOptions) 
    fig.canvas.manager.toolmanager.add_tool('TOTALS', CompareTotals) 

    fig.canvas.manager.toolbar.add_tool('STG', 'grp_stg')
    fig.canvas.manager.toolbar.add_tool('PFX', 'grp_stg')
    fig.canvas.manager.toolbar.add_tool('LEG', 'grp_graph')
    fig.canvas.manager.toolbar.add_tool('DL1', 'grp_graph')
    fig.canvas.manager.toolbar.add_tool('GRT', 'grp_graph')
    fig.canvas.manager.toolbar.add_tool('GEA', 'grp_graph')
    fig.canvas.manager.toolbar.add_tool('GES', 'grp_graph')
    fig.canvas.manager.toolbar.add_tool('DATE', 'grp_date')
    fig.canvas.manager.toolbar.add_tool('COST', 'grp_costs')
    fig.canvas.manager.toolbar.add_tool('L_lcoe', 'grp_costs')
    fig.canvas.manager.toolbar.add_tool('C_lcoe', 'grp_costs')
    fig.canvas.manager.toolbar.add_tool('DCOE', 'grp_costs')
    fig.canvas.manager.toolbar.add_tool('CCBP', 'grp_compare')
    fig.canvas.manager.toolbar.add_tool('OPTS', 'grp_compare')
    fig.canvas.manager.toolbar.add_tool('TOTALS', 'grp_compare')

    return


