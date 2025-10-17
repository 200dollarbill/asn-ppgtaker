

# GUI, serial, and plotting imports
import customtkinter as ctk
import serial
import serial.tools.list_ports
import csv
import time
import threading
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SerialCollectorApp(ctk.CTk):
	def __init__(self):
		super().__init__()
		self.title("Serial Data Collector")
		self.geometry("900x650")
		self.configure(bg="#222831")

		# Variables
		self.com_var = ctk.StringVar()
		self.filename_var = ctk.StringVar(value="output.csv")
		self.collecting = False
		self.data_rows = []
		self.red_data = []
		self.ir_data = []
		self.timestamps = []
		self.serial_handle = None  # Keep serial handle for END

		# UI Layout
		self.create_widgets()


	def create_widgets(self):
		# Minimalist color scheme
		main_frame = ctk.CTkFrame(self)
		main_frame.pack(fill="both", expand=True, padx=20, pady=20)

		# Top controls
		top_frame = ctk.CTkFrame(main_frame)
		top_frame.pack(fill="x", pady=10)

		ctk.CTkLabel(top_frame, text="Select COM Port:", width=120).pack(side="left", padx=5)
		self.combobox = ctk.CTkComboBox(top_frame, values=self.get_com_ports(), variable=self.com_var, width=120)
		self.combobox.pack(side="left", padx=5)

		ctk.CTkLabel(top_frame, text="Filename:", width=80).pack(side="left", padx=5)
		self.filename_entry = ctk.CTkEntry(top_frame, textvariable=self.filename_var, width=180)
		self.filename_entry.pack(side="left", padx=5)

		self.start_btn = ctk.CTkButton(top_frame, text="Start", command=self.start_collection, width=100)
		self.start_btn.pack(side="left", padx=10)
		self.save_btn = ctk.CTkButton(top_frame, text="Save", command=self.save_data, state="disabled", width=100)
		self.save_btn.pack(side="left", padx=10)
		self.end_btn = ctk.CTkButton(top_frame, text="Send END", command=self.send_end, width=100)
		self.end_btn.pack(side="left", padx=10)
		self.end_btn.configure(state="normal")

		# Logging area
		log_frame = ctk.CTkFrame(main_frame)
		log_frame.pack(fill="x", pady=10)
		ctk.CTkLabel(log_frame, text="Log:", width=60).pack(side="left", padx=5)
		self.log_text = ctk.CTkTextbox(log_frame, width=700, height=80)
		self.log_text.pack(side="left", padx=5)

		# Plot area: two subplots for RED and IR
		plot_frame = ctk.CTkFrame(main_frame)
		plot_frame.pack(fill="both", expand=True, pady=10)
		self.fig = Figure(figsize=(8,5), dpi=100)
		self.ax_red = self.fig.add_subplot(211)
		self.ax_ir = self.fig.add_subplot(212)
		self.ax_red.set_title("Red Signal")
		self.ax_red.set_xlabel("Time (s)")
		self.ax_red.set_ylabel("Value")
		self.line_red, = self.ax_red.plot([], [], color="red")
		self.ax_ir.set_title("IR Signal")
		self.ax_ir.set_xlabel("Time (s)")
		self.ax_ir.set_ylabel("Value")
		self.line_ir, = self.ax_ir.plot([], [], color="blue")
		self.fig.tight_layout()
		self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
		self.canvas.get_tk_widget().pack(fill="both", expand=True)

	def send_end(self):
		port = self.com_var.get()
		if not port:
			self.log("Select a COM port.")
			return
		BAUDRATE = 115200
		try:
			if self.collecting and self.serial_handle:
				# Use the open handle if collecting
				self.serial_handle.write(b'END\n')
				self.log("Stop Collection")
		except Exception as e:
			self.log(f"Error sending END: {e}")

	def get_com_ports(self):
		return [port.device for port in serial.tools.list_ports.comports()]

	def log(self, msg):
		self.log_text.insert("end", msg + "\n")
		self.log_text.see("end")

	def start_collection(self):
		if self.collecting:
			self.log("Already collecting data.")
			return
		port = self.com_var.get()
		if not port:
			self.log("Select a COM port.")
			return
		self.collecting = True
		self.data_rows.clear()
		self.red_data.clear()
		self.ir_data.clear()
		self.timestamps.clear()
		self.save_btn.configure(state="disabled")
	# Do not disable the END button during collection; always keep it enabled
		self.log_text.delete("1.0", "end")
		threading.Thread(target=self.collect_serial_data, args=(port,), daemon=True).start()

	def collect_serial_data(self, port):
		BAUDRATE = 115200
		SAMPLE_RATE = 100  # Hz
		DISCARD_SECONDS = 5
		COLLECT_SECONDS = 300  # 5 minutes
		TARGET_SAMPLES = SAMPLE_RATE * COLLECT_SECONDS
		try:
			self.serial_handle = serial.Serial(port, BAUDRATE, timeout=1)
			ser = self.serial_handle
			time.sleep(2)
			ser.write(b'START\n')
			self.log("Sent START. Waiting 5 seconds to discard initial data...")
			# Discard the first 5 seconds of data
			discard_start = time.time()
			while time.time() - discard_start < DISCARD_SECONDS:
				line = ser.readline().decode('utf-8', errors='ignore').strip()
				if int(time.time() - discard_start) % 1 == 0:
					self.log(f"Discarding... {int(time.time() - discard_start) + 1}/5s")
			self.log("Begin collecting 5 minutes of data...")
			collect_start = time.time()
			sample_count = 0
			self.data_rows.clear()
			self.red_data.clear()
			self.ir_data.clear()
			self.timestamps.clear()
			while sample_count < TARGET_SAMPLES:
				line = ser.readline().decode('utf-8', errors='ignore').strip()
				if not line:
					continue
				parts = line.split(',')
				if len(parts) == 3:
					ts, red, ir = parts
					self.data_rows.append([ts, red, ir])
					try:
						self.timestamps.append(ts)
						self.red_data.append(float(red))
						self.ir_data.append(float(ir))
						sample_count += 1
						if sample_count % 100 == 0:
							elapsed = time.time() - collect_start
							self.log(f"Collected {sample_count}/{TARGET_SAMPLES} samples ({elapsed:.1f}s elapsed)")
						if sample_count % SAMPLE_RATE == 0:
							self.update_plot(scroll=True)
					except Exception as e:
						self.log(f"Data parse error: {e} | Raw: {line}")
			# Send END after collection using the same handle
			try:
				ser.write(b'END\n')
				self.log("Sent END to device. Collection finished. 5 minutes of data acquired.")
			except Exception as e:
				self.log(f"Error sending END after collection: {e}")
			self.save_btn.configure(state="normal")
			ser.close()
			self.serial_handle = None
		except Exception as e:
			self.log(f"Error: {e}")
			if self.serial_handle:
				try:
					self.serial_handle.close()
				except Exception:
					pass
			self.serial_handle = None
		self.collecting = False
	
	def update_plot(self, scroll=False):
		# Show only the last 5 seconds of data if scroll=True
		SAMPLE_RATE = 100
		window = SAMPLE_RATE * 5
		if scroll:
			red_y = self.red_data[-window:] if len(self.red_data) > window else self.red_data
			ir_y = self.ir_data[-window:] if len(self.ir_data) > window else self.ir_data
			x_vals = list(range(len(self.red_data)))[-window:] if len(self.red_data) > window else list(range(len(self.red_data)))
		else:
			red_y = self.red_data
			ir_y = self.ir_data
			x_vals = list(range(len(self.red_data)))
		# Use time axis if possible
		if len(self.timestamps) == len(self.red_data):
			try:
				t0 = float(self.timestamps[0]) if self.timestamps else 0
				x_vals = [(float(ts) - t0)/1000000 for ts in self.timestamps][-window:] if scroll else [(float(ts) - t0)/1000000 for ts in self.timestamps]
			except Exception:
				pass
		self.line_red.set_data(x_vals, red_y)
		self.line_ir.set_data(x_vals, ir_y)
		self.ax_red.relim()
		self.ax_red.autoscale_view()
		self.ax_ir.relim()
		self.ax_ir.autoscale_view()
		self.canvas.draw()

	def save_data(self):
		filename = self.filename_var.get()
		try:
			with open(filename, 'w', newline='') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow(['timestamp', 'red', 'ir'])
				writer.writerows(self.data_rows)
			self.log(f"Data saved to {filename}")
		except Exception as e:
			self.log(f"Save error: {e}")

if __name__ == '__main__':
	app = SerialCollectorApp()
	app.mainloop()
