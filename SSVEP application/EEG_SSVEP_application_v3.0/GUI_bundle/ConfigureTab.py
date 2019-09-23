from Tkinter import *
import ttk

######################################################
# This class is used to input a configure tab to a Tkinter project GUI
# The configure tab is set as followed:
# When init, user input the number of instance that is configure tab is expected to output
# The configure tab will create a grid of widgets for each of the instance
# each instance is an object of the class single_instance
# use configure_tab.add_instance(self, name = '', method = 'entry', input_option = []) to auto populate content
# create a button and call configure.tab.output() to read all the value from the tab
# override the button in configuret_tab for meaningful callback method
######################################################

class single_instance(Frame):
    # input_method takes in:
    # - menu: create an option_menu for all the list
    # - entry: create an entry to input
    # - button: a button
    def __init__(self, master, name = '', input_method = 'menu', input_option = [], width = 0, init_value = None, split_percentage = 0.25):
        Frame.__init__(self, master, width = width)
        self.name = name
        self.var = StringVar(master)
        if init_value:
            self.var.set(init_value)
        self.method = input_method
        self.input_option = input_option
        self.master = master
        self.index = 0
        self.width = width
        labelWidth = int(self.width*split_percentage)
        inputWidth = int(self.width*(1 - split_percentage))

        if self.method == 'button':
            self.input = Button(self, text = self.name, command = self.output, width = inputWidth)
        elif self.method == 'menu':
            self.input = ttk.Combobox(self, textvariable = self.var, values = self.input_option, postcommand = self.output, width = inputWidth, justify = CENTER)
        elif self.method == 'entry':
            self.input = Entry(self, width = inputWidth, justify = CENTER)
            if init_value:
                self.input.insert(0, init_value)
        label = Label(self, text = self.name, width = labelWidth, anchor = 'w', justify = LEFT, background = "gray25", foreground = "gray100")
        label.pack(side = LEFT, padx = (0, 10))
        self.input.pack(side = RIGHT, fill = Y)

    def output(self):
        # need to be override to make sense
        if self.method == 'entry':
            return self.input.get()
        elif self.method == 'menu':
            return self.var.get()

    def set_name(self, name):
        self.name = name
        self.init()
    
    def get_name(self):
        return self.name
    
    def set_method(self, method, array = []):
        self.method = method
        if array != []:
            self.input_option = array
            self.var = array[0]
        self.init()
        
    def set_input_option(self, array):
        self.input_option = array
        self.var.set(array[0])
        #self.init()
        if self.method == 'menu':
            self.input['values'] = self.input_option
    
    def init(self):
        self.__init__(self.master, self.name, self.method, self.input_option)
    
    def get_instance(self):
        return self.input
    
    def set_index(self, index):
        self.index = index
        self.init()
    
    def disable(self):
        if self.method == 'entry':
            self.input.config(state = DISABLED)
    
    def enable(self):
        if self.method == 'entry':
            self.input.config(state = NORMAL)

    def get_index(self):
        return self.index

    def get_method(self):
        return self.method

    def get_input_option(self):
        return self.input_option
    
    def set_value(self, value):
        if self.method == 'entry':
            self.input.delete(0, "end")
            self.input.insert(0, value)
        elif self.method == 'menu':
            if value in self.input_option:
                self.var = value

class configure_tab(Frame):
    def __init__(self, master, width = 100, split_percentage = 0.25):
        Frame.__init__(self, master, background = "gray25")
        self.instance_array = {}
        self.width = width
        self.split_percentage = split_percentage

    def output(self):
        output = {}
        for i in self.instance_array.values():
            output[i.get_name()] = i.output()
        return output

    def add_instance(self, name = '', method = 'entry', input_option = [], init_value = None):
        instance = single_instance(self, name, method, input_option, width = self.width, init_value = init_value, split_percentage = self.split_percentage)
        self.instance_array[name] = instance
        instance.pack(anchor = 'w', padx = 5, pady = 5)
    
    def config(self, width = 0):
        if width > 0:
            self.width = width
    
    def set_value(self, name, value):
        for i in self.instance_array.values():
            if i.get_name() == name:
                i.set_value(value)
    
    def get_instance(self, key):
        return self.instance_array[key]
    
    def disable_instance(self, key):
        if self.instance_array[key].get_method() == "entry":
            self.instance_array[key].disable()
    
    def enable_instance(self, key):
        if self.instance_array[key].get_method() == "entry":
            self.instance_array[key].enable()
    
    def update(self):
        # use this function to update all the instances based on the default config of system (bind with <Visibility> event)
        pass

            