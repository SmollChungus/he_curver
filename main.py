import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import signal
import sys
import json
import re



HID_LISTEN_PATH = "C:\\Users\\mpamu\\code\\hid_listen-master\\binaries\\hid_listen.exe"


class ActuationForceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Actuation Force Curve Editor")
        self.root.geometry("1200x800")
        


        # Load keyboard layout from JSON file
        with open('info.json', 'r') as file:
            self.keyboard_layout = json.load(file)["layouts"]["LAYOUT"]["layout"]
        
        self.key_text_ids = {}  # Initialize a dictionary to store text item IDs


        # Container frame for the whole app
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Frame for the keyboard layout
        self.keyboard_frame = tk.Frame(self.container)
        self.keyboard_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)
        self.keyboard_frame.pack_propagate(0)  # Don't shrink
        self.keyboard_frame.config(width=1200, height=300)  # Or whatever size you want
                # Define base unit sizes in pixels. These should be larger to properly represent key sizes.
        self.unit_width = 50  # Width of one key unit, now an attribute of the class
        self.unit_height = 50  # Height of one key unit, now an attribute of the class
        self.spacing = 1
        # Now proceed to call create_keyboard_layout
        self.create_keyboard_layout()
        
        # Frame for the curve plot
        self.curve_frame = tk.Frame(self.container)
        self.curve_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.create_curve_plot()

       # self.check_queue()


        


    def create_curve_plot(self):
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor='#F3BBAF')
        self.plot = self.fig.add_subplot(111)
        self.plot.set_title("Actuation Force Curve")
        self.plot.set_xlabel("Analog Output (%)")
        self.plot.set_ylabel("Switch Travel (%)")
        self.plot.set_xlim(0, 100)
        self.plot.set_ylim(0, 100)

        self.deadzone_fill = None
        self.area_fill = None

        self.control_points = np.array([[0, 1], [25, 33], [75, 66], [100, 99]])

        self.line, = self.plot.plot(self.control_points[:, 0], self.control_points[:, 1], "#BBAFF3")
        
        self.plot.set_facecolor('#AFE7F3')

        self.draggable_points = []
        for point in self.control_points:
            draggable_point, = self.plot.plot(
                point[0], point[1], "o",  # 'o' is the marker style for a circle
                markersize=15,
                picker=14,
                markerfacecolor="#FF6347",  # Tomato red for visibility
                markeredgewidth=2,
                markeredgecolor="white"  # White edge to contrast with the line
            )
            self.draggable_points.append(draggable_point)

        self.current_draggable_point = None

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root, )
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.print_button = ttk.Button(self.root, text="Print Curve", command=self.print_curve_representation)
        self.print_button.pack(side=tk.BOTTOM, pady=10)

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.update_control_points_and_line()

    def create_keyboard_layout(self):
        self.keyboard_canvas = tk.Canvas(self.keyboard_frame, bg="white")
        self.keyboard_canvas.pack(side="top", fill="both", expand=True)

        # Assuming a fixed height for simplicity here
        total_width = sum(key_info.get("w", 1) * self.unit_width for key_info in self.keyboard_layout) + (len(self.keyboard_layout) - 1) * self.spacing
        self.keyboard_canvas.config(width=total_width, height=300) 
        # Initialize the x positions for each row, assuming the first key starts at x position 0
        x_positions = [5, 5, 5, 5, 5]  # Assuming there are 5 rows

        for key_info in self.keyboard_layout:
            label = key_info["label"]
            row = key_info["matrix"][0]
            column = key_info["matrix"][1]

            # 'x' from JSON indicates the unit position from the left edge, accounting for the preceding keys
            x_units = key_info.get("x", 0)  # Starting x position in key units
            y_units = row  # The y position is simply determined by the row number

            # Update the x position for the current key in this row
            x_positions[row] = x_units * self.unit_width  # Convert x units to pixels for x position

            # The x position in pixels should be where the last key in the row ended
            x_position = x_positions[row]
            y_position = y_units * self.unit_height  # Convert row number to pixels for y position

            # Determine key width in pixels using the 'w' attribute from JSON
            key_width = key_info.get("w", 1) * self.unit_width

            # Draw the key rectangle
            self.keyboard_canvas.create_rectangle(x_position, y_position, x_position + key_width, y_position + self.unit_height, fill="#f0f0f0", outline="black")

            # Add text label to the rectangle
            self.keyboard_canvas.create_text(x_position + (key_width / 2), y_position + (self.unit_height / 2), text=label)

            text_id = self.keyboard_canvas.create_text(
                x_position + (key_width / 2), 
                y_position + (self.unit_height / 2), 
                text=label
            )
            # Store the text_id in the dictionary using row and column as the key
            self.key_text_ids[(row, column)] = text_id

        # Set the canvas size to fit the entire keyboard layout
        self.keyboard_canvas.config(scrollregion=self.keyboard_canvas.bbox("all"))
    
    def on_pick(self, event):
        self.current_draggable_point = event.artist

    def on_drag(self, event):
            if self.current_draggable_point is not None and event.xdata is not None and event.ydata is not None:
                index = self.draggable_points.index(self.current_draggable_point)
                
                new_x, new_y = event.xdata, event.ydata
                
                if index == 0:  # First control point
                    new_x = self.control_points[index][0]  # Fix x-axis
                elif index == 3:  # Last control point, assuming 4 total points
                    new_x = self.control_points[index][0]  # Fix x-axis
                
                if 0 < index < 3:  # Only for the middle points
                    prev_y = self.control_points[index - 1][1]
                    next_y = self.control_points[index + 1][1]
                    new_y = max(prev_y + 1, min(new_y, next_y - 1))
                
                self.control_points[index] = [new_x, new_y]
                self.enforce_y_constraints()
                self.enforce_x_constraints()

                self.update_control_points_and_line()

    def update_control_points_and_line(self):
        # Clear the previous fill_between if it exists
        if self.deadzone_fill is not None:
            self.deadzone_fill.remove()
            self.deadzone_fill = None
            
        if self.area_fill is not None:
            self.area_fill.remove()
            self.area_fill = None

        # Update the line connecting the points
        self.line.set_data(self.control_points[:, 0], self.control_points[:, 1])

        # Update the positions of all draggable points based on the control_points array
        for draggable_point, control_point in zip(self.draggable_points, self.control_points):
            draggable_point.set_data([control_point[0]], [control_point[1]])

        # Create a continuous x array for filling, to ensure the fill is continuous
        x_fill = np.linspace(0, 100, 500)
        y_line = np.interp(x_fill, self.control_points[:, 0], self.control_points[:, 1])

        # Apply new fills
        self.deadzone_fill = self.plot.fill_between(
            x_fill, 0, self.control_points[0][1],
            facecolor='#BBAFF3', hatch='//', edgecolor='#6A58BE', alpha=1
        )

        self.area_fill = self.plot.fill_between(
            x_fill, y_line, 0,
            facecolor='pink', alpha=0.95
        )

        # Redraw the canvas to reflect the changes
        self.canvas.draw_idle()

    def update_key_text(self, row, column, text):
        # Find the text item by its row and column
        text_item_id = self.key_text_ids.get((row, column))
        if text_item_id:
            # If found, update the text of the key on the GUI
            self.keyboard_canvas.itemconfig(text_item_id, text=text)
        else:
            print(f"No text item found for key at row {row}, column {column}")


        
    def enforce_y_constraints(self):
        for i in range(1, len(self.control_points) - 1):  # Skip first and last points for y-axis constraint enforcement
            if self.control_points[i][1] <= self.control_points[i - 1][1]:
                self.control_points[i][1] = self.control_points[i - 1][1] + 1
            if i < len(self.control_points) - 1 and self.control_points[i][1] >= self.control_points[i + 1][1]:
                self.control_points[i + 1][1] = self.control_points[i][1] + 1

    def enforce_x_constraints(self):
        for i in range(1, len(self.control_points) - 1):  # Skip first and last points for x-axis constraint enforcement
            if self.control_points[i][0] <= self.control_points[i - 1][0]:
                self.control_points[i][0] = self.control_points[i - 1][0] + 1
            if i < len(self.control_points) - 1 and self.control_points[i][0] >= self.control_points[i + 1][0]:
                if self.control_points[i+1][0] < 100:
                    self.control_points[i + 1][0] = self.control_points[i][0] + 1
                else:
                    self.control_points[i+1][0] = 100

    
    def on_release(self, event):
        self.current_draggable_point = None
        self.update_control_points_and_line()

    def print_curve_representation(self):
        print("C Representation:")
        print("double evaluatePiecewiseLinear(double x) {")
        
        for i in range(len(self.control_points) - 1):
            xi, yi = self.control_points[i]
            xi1, yi1 = self.control_points[i+1]
            
            mi = (yi1 - yi) / (xi1 - xi)
            bi = yi - (mi * xi)
            
            if i == 0:
                print(f"    if (x <= {xi1}) return {mi:.6f} * x + {bi:.6f};")
            else:
                print(f"    else if (x <= {xi1}) return {mi:.6f} * x + {bi:.6f};")
        
        print("    else return x;")  # Handle the case where x is beyond the last control point
        print("}")

#def read_hid_listen_output(process, app):
#    print("Thread: Started reading HID listen output.")  # Debug statement
####      # Add a counter for test updates
   #     counter = 0
   #     
   #     while True:
   #         # Test: Put a test message in the queue every 10 iterations
   #         # Inside read_hid_listen_output
   #         if counter % 10 == 0:
   #             # Cycle through different rows and columns if necessary
   #             test_row = (counter // 10) % 5  # Example: Cycle through rows 0-4
   #             test_column = (counter // 10) % 5  # Example: Adjust as needed
   #             print(f"Thread: Test update {counter} for row {test_row}, column {test_column}.")  # Debug statement
   #             app.update_queue.put((test_row, test_column, f"Test {counter}"))

    #$        counter += 1

        #    line = process.stdout.readline()
        #    if not line:
        #        print("Thread: No more lines to read.")  # Debug statement
        #        break  # End of output

         #   print(f"Thread: Read line: {line.strip()}")  # Debug statement

          #  matches = hid_pattern.finditer(line)
          #  for match in matches:
          #      sensor, column, row, rescale = match.groups()
          #      print(f"Thread: Match found. Row: {row}, Column: {column}, Rescale: {rescale}")  # Debug statement
          #      app.update_queue.put((int(row), int(column), rescale))

   # except Exception as e:
   #     print(f"Thread: Exception caught: {e}")  # Improved exception handling

#def start_hid_listen(app):
#    print("Inside start_hid_listen function.")
#    # Start the hid_listen process
#    print("About to start the hid_listen subprocess.")
##    print("hid_listen subprocess started.")
 #   
 #   # Create a thread to read the output of hid_listen in real-time and pass the app instance to it
 ###  thread.daemon = True
    #thread.start()
    #print("Thread started.")

    # Wait for the process to end or for user input to terminate
 #   try:
 #       process.wait()
 #   except KeyboardInterrupt:
 #       print("Stopping hid_listen.")
 #       process.kill()

def sigint_handler(signum, frame):
    print("Caught SIGINT (Ctrl+C). Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

# Main part of the script to run the app
if __name__ == "__main__":
    print("Creating Tkinter root.")
    root = tk.Tk()
    print("Creating the app.")
    app = ActuationForceApp(root)
    print("Starting hid_listen.")
    #start_hid_listen(app)
    print("Running the Tkinter loop.")
    root.mainloop()
    print("Tkinter loop has ended.")
