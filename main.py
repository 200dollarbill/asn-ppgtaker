import serial as sr
import csv
import matplotlib.pyplot as plt

# port
espport = "/dev/ttyACM0"
baud = 115200
filename = str(input("input nama : ")) + ".csv"
header = ['Index', 'Amplitude (0-4096)']

#plot
fig= plt.figure()
ax = fig.add_subplot(111)
ax.set_ylim(0,4097)
ax.set_title("plot")
currentdata = []

# var
recordingtime = 300
setuptime = 10
delay = 0.02


with sr.Serial(port=espport,baudrate=baud) as serialread, \
    open("asn-csv/data/"+filename,'w',newline='') as file:
    print("written\n")
    print("press en button")
    var = csv.writer(file)
    var.writerow(header)
    i = 0
    l=0
    while True:
        # skip menit pertama
        # sample rate = 50hz or 20ms per sample
        while l < setuptime/delay:
            line = serialread.readline()
            print("setup:", line)
            print("setup time elapsed:", l*delay)
            l+=1    
            
        while i<(recordingtime/delay):
            # reading
            line = int(serialread.readline().decode('utf-8').strip())
            print("line:",line)
            print("recording time elapsed:", i*delay)
            # note i disini masih index i
            
            # writing
            data = [i, line]
            print(data)
            var.writerow(data)
            i+=1
            
            # plotting
            currentdata.append(line)
            currentdata  = currentdata[-50:]
            ax.clear() 
            ax.plot(currentdata) 
            ax.set_ylim(0, 4097)
            ax.set_title("plot (delay +- 7s)")
            plt.pause(0.01)