from tkinter import *
from tkinter.ttk import *
from turtle import onclick

root = Tk()
root.title("Mouser")
root.geometry('600x600')

animalSetupFrame = Frame(root)
dataCollectionFrame = Frame(root)
analysisFrame = Frame(root)
accountsFrame = Frame(root)
mainFrame = Frame(root)


def raiseFrame(frame: Frame):
    frame.tkraise()


def setupFrame(name: str, buttonImage: PhotoImage, frame: Frame, relx: float, rely: float):
    button = Button(mainFrame, text=name, image=buttonImage,
                    compound=TOP, width=25, command=lambda: raiseFrame(frame))
    button.place(relx=relx, rely=rely, anchor=CENTER)


titleLabel = Label(mainFrame, text="Mouser", font=("Arial", 25))
titleLabel.grid(row=0, column=0, columnspan=4, sticky=N)

mouseImage = PhotoImage(file="./images/mouse_small.png")
graphImage = PhotoImage(file="./images/graph_small.png")
magnifyImage = PhotoImage(file="./images/magnifier_small.png")
userImage = PhotoImage(file="./images/user_small.png")

setupFrame("Animal Setup", mouseImage, animalSetupFrame, 0.33, 0.33)
setupFrame("Data Collection", graphImage, dataCollectionFrame, 0.67, 0.33)
setupFrame("Analysis", magnifyImage, analysisFrame, 0.33, 0.67)
setupFrame("Accounts", userImage, accountsFrame, 0.67, 0.67)

frames = [mainFrame, animalSetupFrame,
          dataCollectionFrame, analysisFrame, accountsFrame]

for i, frame in enumerate(frames):
    if i != 0:
        back_button = Button(frame, text="Back", compound=TOP,
                             width=15, command=lambda: raiseFrame(mainFrame))
        back_button.place(relx=0.15, rely=0.05, anchor=CENTER)
    frame.grid(row=0, column=0, sticky="NESW")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
