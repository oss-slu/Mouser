from tkinter import *

# add window
win = Tk();
win.title('Mouser 2.0');
win.geometry('800x400');
win.configure(bg='white');

# window label
# label = Label(win, text='Experiment Setup', bg='teal', width='80');

# text box labels
nameLabel = Label(win, text='Experiment Name', bg='white', fg='black', width='15', height='2');
investLabel = Label(win, text='Investigators', bg='white', fg='black', width='15', height='2');
specLabel = Label(win, text='Species', bg='white', fg='black', width='25', height='2');
measItemLabel = Label(win, text='Measurement Items', bg='white', fg='black', width='15', height='2');

# text boxes
nameText = Text(win, bg='white', fg='black', height='1', width='50');
nameText.config(state='normal');

specText = Text(win, bg='white', fg='black', height='1', width='50');
specText.config(state='normal');

measItemText = Text(win, bg='white', fg='black', height='1', width='50');
measItemText.config(state='normal');

# drop-down menu
investDrop = OptionMenu(win, StringVar(), 'connect list of users here');
investDrop.config(bg='white');
investDrop.config(width='35');

# buttons
investButton = Button(win, text='Add');
measItemButton = Button(win, text='Add');
nextButton = Button(win, text='Next');


# label.place(relx=0, rely=0);

nameLabel.place(x=0, y=100);
nameText.place(x=200, y=100);

investLabel.place(x=0, y=150);
investDrop.place(x=200, y=150);
investButton.place(x=600, y=150);

specLabel.place(x=0, y=200);
specText.place(x=200, y=200);

measItemLabel.place(x=0, y=250);
measItemText.place(x=200, y=250);
measItemButton.place(x=600, y=200);

nextButton.place(x=600, y=250);


win.mainloop();