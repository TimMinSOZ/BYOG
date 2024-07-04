# Test matplotlib toolbar buttons

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backend_tools import ToolBase, ToolToggleBase

plt.rcParams['toolbar'] = 'toolmanager'


# Define custom tools
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

class StgToggle(ToolToggleBase):
    """Show lines with a given gid."""
    default_keymap = 'S'
    description = 'Show Storage Levels'
    default_toggled = True

    def __init__(self, *args, gid, flag, **kwargs):
        self.gid = gid
        self.flag = flag
        super().__init__(*args, **kwargs)

    def enable(self, *args):
        self.flag = 'Y'
        print('Have set battery to  Y   ', self.flag)

    def disable(self, *args):
        self.flag = 'N'
        print('Have set battery to  N   ', self.flag)

class NewClass(ToolBase) :
    
    something = 10
        
    def trigger(self, *args, **kwargs):
        something = 5
        print(' New Class   ', something )
    

    
def add_TB_buttons(fig):
    
    #toolmanager = fig.canvas.manager.toolmanager
    # toolmanager = fig.canvas.manager.toolmanager
    # toolbar = fig.canvas.toolbar
    x = 1
    # Add tools to the ToolManager
    #fig.canvas.manager.toolmanager.add_tool('LIST', ListTools)
    fig.canvas.manager.toolmanager.add_tool('STG', StgToggle, gid='mygroup', flag='N')
    fig.canvas.manager.toolmanager.add_tool('LIST', ListTools)
    fig.canvas.manager.toolmanager.add_tool('NC', NewClass)
    fig.canvas.manager.toolmanager.add_tool('Button', NewClass)
    
    
    fig.canvas.manager.toolmanager.remove_tool('forward')
    fig.canvas.manager.toolmanager.remove_tool('home')
    fig.canvas.manager.toolmanager.remove_tool('back')

#### <matplotlib.backends._backend_tk.ToolbarTk object .!toolbartk> - This ToolbarTk works
    
    fig.canvas.manager.toolbar.add_tool('STG','io', 1)
    fig.canvas.manager.toolbar.add_tool('LIST', 'new_group') #, 2)    
    fig.canvas.manager.toolbar.add_tool('NC', 'new_group')
    fig.canvas.manager.toolbar.add_tool('Button','new_group',1)

###   <matplotlib.backends._backend_tk.FigureManagerTk object at 0x000001B5F70E08E0>
# Create a figure and add the custom buttons
fig, ax = plt.subplots()
add_TB_buttons(fig)
plt.show()