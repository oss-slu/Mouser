from customtkinter import *
from tk_models import *
  
class serialPortSetting(SettingPage):

    def __init__(self):

        super().__init__(self)

        self.title("Serial Port")

        self.stop_bits_var = StringVar(value="1")

        self.iput_type_var = StringVar(value="Binary")

        self.tab_view = CTkTabview(master=self)
        self.tab_view.grid(padx=20, pady=20, sticky = "ew")

        self.tab_view.add("Map RFID")  # add tab at the end
        self.tab_view.add("Data Collection")  # add tab at the end
        self.fill_tab("Map RFID")
        self.fill_tab("Data Collection")

    
    def fill_tab(self, tab: str):
        self.baud_rate_label = CTkLabel(self.tab_view.tab(tab), text="Baud Rate")
        self.baud_rate_menu = CTkComboBox(self.tab_view.tab(tab), values=["100", "300", "600", "1200", "2400", "4800", "9600", "19200"])
        self.baud_rate_label.grid(row=0, column=0, padx=20, pady=10, stick="ew")
        self.baud_rate_menu.set("9600")
        self.baud_rate_menu.grid(row=0, column=1, columnspan=2, padx=20, pady=10, sticky="ew")

        self.parity_label = CTkLabel(self.tab_view.tab(tab), text="Parity")
        self.parity_menu = CTkComboBox(self.tab_view.tab(tab), values=["None", "Odd", "Even", "Mark", "Space"])
        self.parity_label.grid(row=1, column=0, padx=20, pady=10, stick="ew")
        self.parity_menu.set("None")
        self.parity_menu.grid(row=1, column=1, columnspan=2, padx=20, pady=10, sticky="ew")

        self.flow_control_label = CTkLabel(self.tab_view.tab(tab), text="Flow Control")
        self.flow_control_menu = CTkComboBox(self.tab_view.tab(tab), values=["None", "Xon/Xoff", "Hardware", "Opto-RS"])
        self.flow_control_label.grid(row=2, column=0, padx=20, pady=10, stick="ew")
        self.flow_control_menu.set("None")
        self.flow_control_menu.grid(row=2, column=1, columnspan=2, padx=20, pady=10, sticky="ew")

        self.data_bits_label = CTkLabel(self.tab_view.tab(tab), text="Data Bits")
        self.data_bits_menu = CTkComboBox(self.tab_view.tab(tab), values=["Five", "Six", "Seven", "Eight"])
        self.data_bits_label.grid(row=3, column=0, padx=20, pady=10, stick="ew")
        self.data_bits_menu.set("Eight")
        self.data_bits_menu.grid(row=3, column=1, columnspan=2, padx=20, pady=10, sticky="ew") 

        self.stop_bits_label = CTkLabel(self.tab_view.tab(tab), text="Stop Bits")
        self.one_button = CTkRadioButton(self.tab_view.tab(tab), text="1", variable=self.stop_bits_var, value = "1")
        self.one_point_five_button = CTkRadioButton(self.tab_view.tab(tab), text="1.5", variable=self.stop_bits_var, value = "1.5")
        self.two_button = CTkRadioButton(self.tab_view.tab(tab), text="2", variable=self.stop_bits_var, value = "2")
        self.stop_bits_label.grid(row=4, column=0, padx=20, pady=10, stick="ew")
        self.one_button.grid(row=4, column=1, padx=20, pady=10, sticky="ew")
        self.one_point_five_button.grid(row=4, column=2, padx=20, pady=10, sticky="ew")
        self.two_button.grid(row=5, column=1, padx=20, pady=10, sticky="ew")

        self.input_byte_label = CTkLabel(self.tab_view.tab(tab), text="Input Byte")
        self.binary_button = CTkRadioButton(self.tab_view.tab(tab), text="Binary", variable=self.iput_type_var, value = "Binary")
        self.text_button = CTkRadioButton(self.tab_view.tab(tab), text="2", variable=self.iput_type_var, value = "Text")
        self.input_byte_label.grid(row=6, column=0, padx=20, pady=10, stick="ew")
        self.binary_button.grid(row=6, column=1, padx=20, pady=10, sticky="ew")
        self.text_button.grid(row=6, column=2, padx=20, pady=10, sticky="ew")

        self.generateResultsButton = CTkButton(self.tab_view.tab(tab), text="Save", command=self.save)
        self.generateResultsButton.grid(row=7, column=2, padx=20, pady=40, sticky="ns")

    def save(self):
        print(self.flow_control_menu.get())
        print(self.tab_view.get())


  


if __name__ == "__main__":
    app = serialPortSetting()
    app.mainloop()
    print("success?")