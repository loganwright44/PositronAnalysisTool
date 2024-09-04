from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PepTo3

# WINDOW INSTANTIATION
root = Tk()
root.title("PepTo - Positron Annihilation Analysis")
root.configure(background = 'lightgray')

# WINDOW SETUP
# Get window max width and height
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.maxsize(width, height)
root.geometry("%dx%d" % (width, height))

# BUILD PEPTO OBJECT AND RUN ITS COMMANDS
datast = PepTo3.DataSet(['nickel', 'aluminum', 'copper', 'lead', 'gold', 'tungsten'])
datast.FillDataSet(PepTo3.GetDirectories())
fig, ax = datast.SvW()
canvas = FigureCanvasTkAgg(fig, root)

def PlotBoxes():
    canvas.draw()
    canvas.get_tk_widget().pack()
    return None

# WIDGETS - ADD ALL BUTTONS AND SWITCHES
plot_button = Button(root, height = 2, width = 10, text = 'Run Box Plots', command = PlotBoxes)

plot_button.pack()

# RUN APP
root.mainloop()