# EQ-318 - TMX Keyence Measurement System
# 3/7/2023
# Nelson To
# 
# v3.1
# - add long reference checkbox to adjust x1 location
# - fix csv file write error
# 
# v3.2
# - increase measured data points to 100
#

import thorlabs_apt as apt
import serial
import time
import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

ser = serial.Serial(port='COM3', baudrate=9600, parity= 'N', stopbits= 1, bytesize= 8, timeout= None)

y1 = 2.3    #y location
    
motorX=apt.Motor(27259557)
motorY=apt.Motor(27259910)

#homing x and y motors
def home_motors ():
    print('Homing x,y linear rails')
    motorX.set_velocity_parameters(0,1.5,2.3)  #set to max velocity
    motorY.set_velocity_parameters(0,1.5,2.3)  #set to max velocity
    motorX.move_home(True)
    motorY.move_home(True)

#wire measurment function
def measure_wires ():  
    
    wireDiameter = [[],[],[],[]]    #wire diameter list
    x = [[],[],[],[]]               #wire x location
    numSamples = 100    #Number of sampling points

    if (wireType.get() == 0):
        x1 = 9.0                    #reference wire
    else:
        x1 = 0.0                    #working wire
        
        
    if (motorX.has_homing_been_completed or motorY.has_homing_been_completed) == 0: #checks if motors have been homed, execute homing sequence if not homed
        home_motors()

    rawstring = ""
    
    for i in range(numSamples):
        rawstring = rawstring +",Raw"+str(i+1)

    wireHeaderData = "DateTime,OperatorID, EquipmentID, LotID,SensorNumber,FixtureID,SensorID,TipDiameter"+ rawstring +"\n"
    file = open ("Data\wireDiameter-" + time.strftime("%Y%m%d-%H%M%S") +"_" + fixtureID.get() + ".csv", 'w')
    file.write(wireHeaderData)
    
    for i in range (4):
        j = 0

        file.write(time.strftime('%m/%d/%y %H:%M,') + 'N/A'+ ',' + 'EQ-318 TMX,' + lotID.get() + ',' + str(i+1) + ',' + fixtureID.get() + ',' + fixtureID.get() + '-' + str(i+1) + ',' + 'TipDiameter,')
        motorY.move_to(y1+(9.5*i), blocking =1)        
        motorX.move_to(x1, blocking = 1)
        
        time.sleep(1.0)                                  #1000ms pause
        print ("Measuring Wire %d" %(i+1))
        
        measureCommand = ("GM,0,0\r")
        ser.write(measureCommand.encode())              #send measure command to keyence via rs232
        rawDiameter = ser.read_until(b'\r')             #read output until carriage return
    
        wireDiam = rawDiameter.decode('utf-8')
        wireDiam = wireDiam.split(',')
        wireDiam = wireDiam [2:]
        
        wireDiam = ([float(x) for x in wireDiam])
        
        for j in range(100):
            if (wireDiam[j]>0):
                file.write(str(wireDiam[j])+',')
                x[i].append(0.03*j)
                wireDiameter[i].append(wireDiam[j])
                             
        file.write('\n')
        
    file.close()
    plotData(fixtureID, wireDiameter, x)
    
def endProgram():
    print ('Exiting')
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        ser.close()
        window.destroy()
        
#Data Plot Function
def plotData(fixtureID, wireDiameter, x):  
    figure.clear()
    plt = figure.add_subplot(111)

    # plt.title('Wire Diameter - FX-' + str(fixtureID),color='black',fontsize=10)
    plt.set_title('Wire Diameter - FX-' + fixtureID.get(),color='black',fontsize=10)
    plt.plot(x[0],wireDiameter[0],label="wire 1", color="red")
    plt.plot(x[1],wireDiameter[1],label="wire 2", color="orange")
    plt.plot(x[2],wireDiameter[2],label="wire 3", color="green")
    plt.plot(x[3],wireDiameter[3],label="wire 4", color="blue")
    
    plt.set_xlabel('X (mm)')
    plt.set_ylabel('Diameter (mm)')
    plt.legend(loc="best")
    plt.grid(color = 'grey', linestyle = '-', linewidth = 0.5)
    
    figure.tight_layout()

    canvas.draw()
    canvas.flush_events()
    canvas.get_tk_widget().pack()
    toolbar.update()
    canvas.get_tk_widget().pack()
    
# def main(command):
#     if command == 'm':
#         measure_wires()
#     elif command =='h':
#         home_motors()
#     elif command == 'x':
#         quit()
#     else:
#         print ('Not a valid command\n')
    
# while (True):
    # command = input ('\nPress m to measure\nPress h to home motors\nPress x to exit\n')
    # main(command)


#GUI Components

window = tk.Tk()
window.title('R&D TM-X Keyence Wire Diameter')  
    
lotID=tk.StringVar()
fixtureID=tk.StringVar()
measureLength=tk.IntVar()
sampleRate=tk.IntVar()
wireType=tk.IntVar()

# measureLength.set(8)
# sampleRate.set(10)

frmInput=tk.Frame()
frmGraph=tk.Frame()

frmInput.grid(row=1, column=0, sticky="nw",padx=5, pady=5)
frmGraph.grid(row=1, column=1, sticky="nw",padx=5, pady=5)

figure = Figure(figsize=(6, 4), dpi=100)
canvas = FigureCanvasTkAgg(figure, master = frmGraph)
toolbar = NavigationToolbar2Tk(canvas,frmGraph)
    
tk.Label(master=frmInput,text="Lot #:", anchor="e", width= 10).grid(row=1, column=0)
entLOT = tk.Entry(master=frmInput, textvariable = lotID, width=12)
entLOT.grid(row=1, column=1, sticky="w")

tk.Label(master=frmInput,text="FX-2-#:", anchor="e", width = 10).grid(row=2, column=0, pady=(0,15))
entFX = tk.Entry(master=frmInput, textvariable = fixtureID, width=12)
entFX.grid(row=2, column=1, sticky="w", pady=(0,15))

##wireType 0 = working wire, 1 = reference wire
#tk.Label(master=frmInput,text="Reference Wire", anchor="e", width = 22).grid(row=3, column=0, pady=(0,15))
entTypeCheck = tk.Checkbutton(master=frmInput, text='Reference',variable=wireType, onvalue=1, offvalue=0)
entTypeCheck.grid(row=3, column=1, sticky="w", pady=(0,15))

# tk.Label(master=frmInput,text="Measurement Length (mm):", anchor="e", width=22).grid(row=3, column=0)
# spinLength = tk.Spinbox (master=frmInput, textvariable = measureLength, width=10, from_=0, to=10)
# spinLength.grid(row=3, column=1, sticky="w")

# tk.Label(master=frmInput,text="Sample Rate (#/mm):", anchor="e", width=22).grid(row=4, column=0, pady=(0,15))
# spinRate = tk.Spinbox(master=frmInput, textvariable = sampleRate, width=10, from_=5, to=100)
# spinRate.grid(row=4, column=1, sticky="w", pady=(0,15))

btnHome = tk.Button(master=frmInput, command = home_motors, text="Home Motors", width = 17)
btnMeasure = tk.Button(master=frmInput, command = measure_wires, text="Measure Wires", width = 17, height=2, bg="#FFEBB3")
btnExit= tk.Button(master=frmInput, command = endProgram, text="Exit", width = 17)

btnMeasure.grid(row=6, column=0, columnspan=2, sticky="e", pady=(0,10))
btnHome.grid(row=7, column=0, columnspan=2, sticky="e", pady=(0,10))
btnExit.grid(row=8, column=0, columnspan=2, sticky="e")

window.protocol("WM_DELETE_WINDOW", endProgram)
window.mainloop()
# ser.close()