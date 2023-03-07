from tkinter import *
from tkinter.ttk import *
from tk_models import *
from scrollable_frame import ScrolledFrame
from experiment_pages.experiment import Experiment


class CreateExperimentButton(Button):
    def __init__(self, experiment: Experiment, page: Frame, menu_page: Frame):
        super().__init__(page, text="Create", compound=TOP,
                         width=15, command=lambda: [experiment.save_to_database(), menu_page.update_frame(), self.navigate()])
        self.place(relx=0.85, rely=0.15, anchor=CENTER)
        self.next_page = menu_page

    def navigate(self):
        self.next_page.tkraise()


class SummaryUI(MouserPage):
    def __init__(self, input: Experiment, parent:Tk, prev_page: Frame, menu_page: Frame):
        super().__init__(parent, "New Experiment - Summary", prev_page)
        
        self.input = input
        self.menu = menu_page

        CreateExperimentButton(input, self, menu_page)

        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.10, rely=0.25, relheight=0.7, relwidth=0.8)

        self.main_frame = Frame(scroll_canvas)
        self.main_frame.pack(side=LEFT, expand=True)


    def update_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.create_summary_frame() 


    def create_summary_frame(self):
        pad_x, pad_y = 10, 10
        labels, inputs = [], []

        label_style = Style()
        label_style.configure('Summary.TLabel', font=('Arial', '10', 'bold'))

        name_label = Label(self.main_frame, text='Experiment Name:', style='Summary.TLabel')
        name_input = Label(self.main_frame, text=self.input.get_name())
        labels.append(name_label)
        inputs.append(name_input)

        names = ''
        for name in self.input.get_investigators():
            names += name + ',\n'
        invest_label = Label(self.main_frame, text='Investigators:', style='Summary.TLabel')
        invest_input = Label(self.main_frame, text=names[:-1])
        labels.append(invest_label)
        inputs.append(invest_input)

        species_label = Label(self.main_frame, text='Species:', style='Summary.TLabel')
        species_input = Label(self.main_frame, text=self.input.get_species())
        labels.append(species_label)
        inputs.append(species_input)

        items = ''
        for item in self.input.get_measurement_items():
            items += item + ',\n'
        items_label = Label(self.main_frame, text='Measurement Items:', style='Summary.TLabel')
        items_input = Label(self.main_frame, text=items[:-1])
        labels.append(items_label)
        inputs.append(items_input)

        animals = self.input.get_num_animals() + ' ' + self.input.get_species()
        animal_label = Label(self.main_frame, text='Number of Animals:', style='Summary.TLabel')
        animal_input = Label(self.main_frame, text=animals)
        labels.append(animal_label)
        inputs.append(animal_input)

        cage_label = Label(self.main_frame, text='Animals per Cage:', style='Summary.TLabel')
        cage_input = Label(self.main_frame, text=self.input.get_max_animals())
        labels.append(cage_label)
        inputs.append(cage_input)

        groups = self.input.get_group_names()
        group_names = ''
        for group in groups:
            group_names += group + ',\n'
            
        group_label = Label(self.main_frame, text='Group Names:', style='Summary.TLabel')
        group_input = Label(self.main_frame, text=group_names[:-1])
        labels.append(group_label)
        inputs.append(group_input)

        rfid = str(self.input.uses_rfid())
        rfid_label = Label(self.main_frame, text='Uses RFID:', style='Summary.TLabel')
        rfid_input = Label(self.main_frame, text=rfid)
        labels.append(rfid_label)
        inputs.append(rfid_input)

        for index in range(0, len(labels)):
            labels[index].grid(row=index, column=0, padx= pad_x, pady= pad_y, sticky=NW)
            inputs[index].grid(row=index, column=1, padx= pad_x, pady= pad_y, sticky=NW)

            self.main_frame.grid_rowconfigure(index, weight=1)
            self.main_frame.grid_columnconfigure(index, weight=1)


    def create_experiment(self):
        self.input.save_to_database()
