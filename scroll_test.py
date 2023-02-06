from tkinter import *
from tkinter.ttk import *

root = Tk()
root.title("root")

## SCROLL STUFF BELOW ##

# binds scroll to mouse wheel
def _on_mouse_wheel(event):
    my_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

# create main frame
main_frame = Frame(root) 
main_frame.pack(fill=BOTH, expand=1) # pack version
# main_frame.grid(row=0, column=0)  # grid version


# create canvas
my_canvas = Canvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1) # pack version
# my_canvas.grid(row=0, column=0) # grid version


# add scrollbar to canvas
my_scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview) # scrollbar is attached to canvas
my_scrollbar.pack(side=RIGHT, fill=Y) # pack version
# my_scrollbar.grid(row=0, column=1, rowspan=100) # grid version


# config the canvas - set the scrollbar/mouse commands
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
my_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)


# create another frame inside canvas
second_frame = Frame(my_canvas)
second_frame.grid(row=10, column=0)


# add new frame to window in the canvas
my_canvas.create_window((0,0), window=second_frame, anchor="nw")


##### END OF SCROLL WINDOW CREATION : #####
# all below is to test adding widgets to the "second frame" which 
# is on the scroll canvas window, theoretically this should work but get error: 
# "_tkinter.TclError: cannot use geometry manager grid inside . which already has slaves managed by pack"
# when adding another frame onto the "second frame"
# if pack widgets onto new frame, they are added below the scroll area



# works/scrollable - but not on seperate frame 
# for thing in range(100):
#     Button(second_frame, text=f'Button {thing}').grid(row=thing, column=0)


# # packs under scroll area:
# for num in range(10):
#     fram = Frame(second_frame).pack(side=TOP)
#     but = Button(fram, text=f'Frame {num}').pack(side=TOP)



# # packs under scroll area:
# for num in range(100):
#     fram = Frame(second_frame).grid(row=num, column=0)
#     Label(fram, text="this is the label").pack(side=TOP)


# # not scrollable
# y_cord = 0.1
# for num in range(100):
#     fram = Frame(second_frame).grid(row=num, column=0)
#     Label(fram, text="this is the label").place(relx=0.2, rely=y_cord)
#     y_cord += 0.1



# labels do not show up on frame & not scrollable
y_cord = 0.1
for num in range(100):
    # fram = Frame(second_frame).grid(row=num, column=0)
    Label(second_frame, text="this is the label").place(relx=0.2, rely=y_cord)
    y_cord += 0.1



# frames = []

# fram1 = Frame(second_frame).grid(row=0, column=0)
# fram2 = Frame(second_frame).grid(row=1, column=0)
# fram3 = Frame(second_frame).grid(row=2, column=0)
# fram4 = Frame(second_frame).grid(row=3, column=0)
# fram5 = Frame(second_frame).grid(row=4, column=0)
# fram6 = Frame(second_frame).grid(row=5, column=0)
# fram7 = Frame(second_frame).grid(row=6, column=0)
# fram8 = Frame(second_frame).grid(row=7, column=0)

# but1 = Button(fram1, text='Frame 1').pack(side=TOP)
# but2 = Button(fram2, text='Frame 2').pack(side=TOP)
# but3 = Button(fram3, text='Frame 3').pack(side=TOP)
# but4= Button(fram4, text='Frame 4').pack(side=TOP)
# but5 = Button(fram5, text='Frame 5').pack(side=TOP)
# but6 = Button(fram6, text='Frame 6').pack(side=TOP)
# but7 = Button(fram7, text='Frame 7').pack(side=TOP)
# but8 = Button(fram8, text='Frame 8').pack(side=TOP)






root.mainloop()