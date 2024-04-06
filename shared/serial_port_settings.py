from customtkinter import *
#from shared.tk_models import SettingPage
from tk_models import SettingPage
from os import listdir, getcwd
from os.path import isfile, join
  
class serialPortSetting(SettingPage):

    def __init__(self):

        super().__init__(self)

        self.title("Serial Port")

        self.template_name = StringVar(value="")
        self.baud_rate = "9600"
        self.baud_rate_var = StringVar(value="9600")
        self.parity = "None"
        self.parity_var = StringVar(value="None")
        self.flow_control = "None"
        self.flow_control_var = StringVar(value="None")
        self.data_bits = "Eight"
        self.data_bits_var = StringVar(value="Eight")
        self.stop_bits_var = StringVar(value="1")
        self.input_bype_var = StringVar(value="Binary")


        self.tab_view = CTkTabview(master=self)
        self.tab_view.grid(padx=20, pady=20, sticky = "ew")

        self.tab_view.add("Map RFID")  # add tab at the end
        self.tab_view.add("Data Collection")  # add tab at the end
        self.summary_page("Map RFID")
        self.summary_page("Data Collection")

        #self.port_setting_template_path = os.getcwd() + "\\settings\\serial ports"
        self.port_setting_template_path = "C:\\Users\\stanl\\capstone1\\mouser\\Mouser\\settings\\serial ports"
        self.available_template = [file for file in listdir(self.port_setting_template_path) if isfile(join(self.port_setting_template_path, file))]

        for x in self.available_template:
            print(x)

    
    def edit_page(self, tab: str):
        self.template_region = CTkFrame(master=self.tab_view.tab(tab), corner_radius=10, border_width=2, width=400, height=200)
        self.region_title_label = CTkLabel(master = self.template_region, text="Existing Template")
        self.setting_template_label = CTkLabel(self.template_region, text="Current Template", width=8, height=12)
        self.import_file = CTkOptionMenu(self.template_region, values=self.available_template, height=12, width = 274)
        self.edit_template_button = CTkButton(self.template_region, text="Edit", width=2, height=14, command=self.edit_template)
        self.set_preference_button = CTkButton(self.template_region, text="Set Preference", width=2, height=14, command=self.set_preference)
        self.comfirm_button = CTkButton(self.template_region, text="Confirm", width=2, height=14, command=self.confirm_setting)

        self.template_region.grid(row=0, column=0, columnspan=5, padx=20, pady=5, sticky="ew")
        self.region_title_label.grid(row=0, column=0, padx=5, pady=3, sticky="ew")
        self.setting_template_label.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.import_file.grid(row=1, column=1, columnspan=2, padx=18, pady=10, sticky="ew")
        self.edit_template_button.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        self.set_preference_button.grid(row=2, column=2, padx=20, pady=15, sticky="ew")
        self.comfirm_button.grid(row=2, column=3, padx=20, pady=15, sticky="ew")

        self.edit_region = CTkFrame(master=self.tab_view.tab(tab), corner_radius=10, border_width=2, width=400, height=400)
        self.edit_region.grid(row=1, column=0, columnspan=5, padx=20, pady=5, sticky="ew")

        self.new_template_label = CTkLabel(self.edit_region, text="New Template", width=8, height=12)
        self.new_template_name_label = CTkLabel(self.edit_region, text="Template Name", width=8, height=12)
        self.template_name_entry = CTkEntry(self.edit_region, textvariable=self.template_name)
        self.baud_rate_label = CTkLabel(self.edit_region, text="Baud Rate", width=8, height=12)
        self.baud_rate_menu = CTkOptionMenu(self.edit_region, height=12, 
                                            values=["100", "300", "600", "1200", "2400", "4800", "9600", "19200"], 
                                            variable=self.baud_rate_var)
        
        self.new_template_label.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        self.new_template_name_label.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.template_name_entry.grid(row=1, column=1, columnspan=2, padx=20, pady=5, sticky="ew")
        self.baud_rate_label.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.baud_rate_menu.grid(row=2, column=1, columnspan=2, padx=20, pady=5, sticky="ew")

        self.parity_label = CTkLabel(self.edit_region, text="Parity", height=12)
        self.parity_menu = CTkOptionMenu(self.edit_region, height=12, 
                                         values=["None", "Odd", "Even", "Mark", "Space"],
                                         variable=self.parity_var)
        self.parity_label.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.parity_menu.grid(row=3, column=1, columnspan=2, padx=20, pady=5, sticky="ew")

        self.flow_control_label = CTkLabel(self.edit_region, text="Flow Control", height=12)
        self.flow_control_menu = CTkOptionMenu(self.edit_region, height=12, 
                                               values=["None", "Xon/Xoff", "Hardware", "Opto-RS"],
                                               variable=self.flow_control_var)
        self.flow_control_label.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.flow_control_menu.grid(row=4, column=1, columnspan=2, padx=20, pady=5, sticky="ew")

        self.data_bits_label = CTkLabel(self.edit_region, text="Data Bits", height=12)
        self.data_bits_menu = CTkOptionMenu(self.edit_region, height=12, 
                                            values=["Five", "Six", "Seven", "Eight"],
                                            variable=self.data_bits_var)
        self.data_bits_label.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        self.data_bits_menu.grid(row=5, column=1, columnspan=2, padx=20, pady=5, sticky="ew") 

        self.stop_bits_label = CTkLabel(self.edit_region, text="Stop Bits", height=12)
        self.one_button = CTkRadioButton(self.edit_region, text="1", variable=self.stop_bits_var, value = "1", height=12)
        self.one_point_five_button = CTkRadioButton(self.edit_region, text="1.5", variable=self.stop_bits_var, value = "1.5", height=12)
        self.two_button = CTkRadioButton(self.edit_region, text="2", variable=self.stop_bits_var, value = "2", height=12)
        self.stop_bits_label.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        self.one_button.grid(row=6, column=1, padx=20, pady=5, sticky="ew")
        self.one_point_five_button.grid(row=6, column=2, padx=20, pady=5, sticky="ew")
        self.two_button.grid(row=7, column=1, padx=20, pady=5, sticky="ew")

        self.input_byte_label = CTkLabel(self.edit_region, text="Input Byte", height=12)
        self.binary_button = CTkRadioButton(self.edit_region, text="Binary", variable=self.input_bype_var, value = "Binary", height=12)
        self.text_button = CTkRadioButton(self.edit_region, text="Text", variable=self.input_bype_var, value = "Text", height=12)
        self.input_byte_label.grid(row=8, column=0, padx=20, pady=5, sticky="ew")
        self.binary_button.grid(row=8, column=1, padx=20, pady=5, sticky="ew")
        self.text_button.grid(row=8, column=2, padx=20, pady=5, sticky="ew")

        self.save_button = CTkButton(self.edit_region, text="Save", command=self.save, height=14)
        self.save_button.grid(row=9, column=2, padx=20, pady=40, sticky="ns")

    def summary_page(self, tab: str):

        self.baud_rate_label = CTkLabel(self.tab_view.tab(tab), text="Baud Rate")
        self.current_baud_rate = CTkLabel(self.tab_view.tab(tab), text=self.baud_rate)
        
        self.baud_rate_label.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        self.current_baud_rate.grid(row=0, column=2, padx=20, pady=5, sticky="ew")


        self.parity_label = CTkLabel(self.tab_view.tab(tab), text="Parity")
        self.current_parity = CTkLabel(self.tab_view.tab(tab), text=self.parity)
        self.parity_label.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.current_parity.grid(row=1, column=2, padx=20, pady=5, sticky="ew")

        self.flow_control_label = CTkLabel(self.tab_view.tab(tab), text="Flow Control")
        self.current_flow_control = CTkLabel(self.tab_view.tab(tab), text=self.flow_control)
        self.flow_control_label.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.current_flow_control.grid(row=2, column=2, padx=20, pady=5, sticky="ew")


        self.data_bits_label = CTkLabel(self.tab_view.tab(tab), text="Data Bits")
        self.current_data_bits = CTkLabel(self.tab_view.tab(tab), text=self.data_bits)
        self.data_bits_label.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.current_data_bits.grid(row=3, column=2, padx=20, pady=5, sticky="ew")

        self.stop_bits_label = CTkLabel(self.tab_view.tab(tab), text="Stop Bits")
        self.current_stop_bits = CTkLabel(self.tab_view.tab(tab), text=self.stop_bits_var.get())
        self.stop_bits_label.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.current_stop_bits.grid(row=4, column=2, padx=20, pady=5, sticky="ew")

        self.input_byte_label = CTkLabel(self.tab_view.tab(tab), text="Input Byte")
        self.current_input_byte = CTkLabel(self.tab_view.tab(tab), text=self.input_bype_var.get())
        self.input_byte_label.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        self.current_input_byte.grid(row=6, column=2, padx=20, pady=5, sticky="ew")

        self.edit_button = CTkButton(self.tab_view.tab(tab), text="Edit", command=self.edit)
        self.edit_button.grid(row=7, column=2, padx=20, pady=40, sticky="ns")


    def save(self):

        self.baud_rate = self.baud_rate_menu.get()
        self.parity = self.parity_menu.get()
        self.flow_control = self.flow_control_menu.get()
        self.data_bits = self.data_bits_menu.get()

        # TODO: save the setting to serial port directory
        print("name: ",self.template_name.get())
        file_name = os.path.join(self.port_setting_template_path, self.template_name.get()+".csv")         

        file = open(file_name, "w")
        setting = self.baud_rate+","+self.parity+","+self.flow_control+","+self.data_bits+","+self.stop_bits_var.get()+","+self.input_bype_var.get()
        file.write(setting)
        file.close() 

        self.refresh_tabs()
        self.summary_page("Map RFID")
        self.summary_page("Data Collection")


    def edit(self):
        self.refresh_tabs()
        self.edit_page("Map RFID")
        self.edit_page("Data Collection")
    
    def refresh_tabs(self):
        self.tab_view.delete("Map RFID")
        self.tab_view.delete("Data Collection")
        self.tab_view.add("Map RFID")
        self.tab_view.add("Data Collection")

    def set_preference(self):
        # TODO: save the name of current template file to the preference file in preference directory
        pass
    
    def confirm_setting(self):
        # TODO: read from the selected file the associated data used for serial port
        pass

    def edit_template(self):
        #TODO: edit the selected template, possibly bt opening a new window
        pass




  


if __name__ == "__main__":
    app = serialPortSetting()
    app.mainloop()