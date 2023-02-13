import tkinter as tk

root = tk.Tk()

# Tkinter widgets needed for scrolling.  The only native scrollable container that Tkinter provides is a canvas.
# A Frame is needed inside the Canvas so that widgets can be added to the Frame and the Canvas makes it scrollable.
cTableContainer = tk.Canvas(root)
fTable = tk.Frame(cTableContainer)
sbHorizontalScrollBar = tk.Scrollbar(root)
sbVerticalScrollBar = tk.Scrollbar(root)

# Updates the scrollable region of the Canvas to encompass all the widgets in the Frame
def updateScrollRegion():
	cTableContainer.update_idletasks()
	cTableContainer.config(scrollregion=fTable.bbox())

# Sets up the Canvas, Frame, and scrollbars for scrolling
def createScrollableContainer():
	cTableContainer.config(xscrollcommand=sbHorizontalScrollBar.set,yscrollcommand=sbVerticalScrollBar.set, highlightthickness=0)
	sbHorizontalScrollBar.config(orient=tk.HORIZONTAL, command=cTableContainer.xview)
	sbVerticalScrollBar.config(orient=tk.VERTICAL, command=cTableContainer.yview)

	sbHorizontalScrollBar.pack(fill=tk.X, side=tk.BOTTOM, expand=tk.FALSE)
	sbVerticalScrollBar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
	cTableContainer.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
	cTableContainer.create_window(0, 0, window=fTable, anchor=tk.NW)

# Adds labels diagonally across the screen to demonstrate the scrollbar adapting to the increasing size
i=0
def addNewLabel():
	global i
	tk.Label(fTable, text="Hello World").grid(row=i, column=0)
	i+=1

	# Update the scroll region after new widgets are added
	updateScrollRegion()

	root.after(1000, addNewLabel)

createScrollableContainer()
addNewLabel()

root.mainloop()