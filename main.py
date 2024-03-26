import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import CubicSpline
import numpy as np
import signal
import sys

class ActuationForceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Actuation Force Curve Editor")
        self.root.geometry("600x450")

        # Create a matplotlib figure and a subplot with labels
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.fig.add_subplot(111)
        self.plot.set_title("Actuation Force Curve")
        # Set the names (labels) for the x-axis and y-axis
        self.plot.set_xlabel("Switch Travel (%)")
        self.plot.set_ylabel("Analog Output (%)")
        self.plot.set_xlim(0, 100)
        self.plot.set_ylim(0, 100)

        # Initial control points with the first and last ones fixed
        self.control_points = np.array([[0, 0], [33, 33], [66, 66], [100, 100]])

        # Plotting the initial line
        self.line, = self.plot.plot(self.control_points[:, 0], self.control_points[:, 1], "ro-")

        # Making points draggable (except the first and last ones)
        self.draggable_points = []
        for point in self.control_points:
            draggable_point, = self.plot.plot(point[0], point[1], "bo", markersize=15, picker=15)
            self.draggable_points.append(draggable_point)

        self.current_draggable_point = None

        # Embed the figure in the tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Button for printing the curve representation
        self.print_button = ttk.Button(self.root, text="Print Curve", command=self.print_curve_representation)
        self.print_button.pack(side=tk.BOTTOM, pady=10)

        # Bind the pick event for dragging
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)

    def on_pick(self, event):
        self.current_draggable_point = event.artist

    def on_drag(self, event):
            if self.current_draggable_point is not None and event.xdata is not None and event.ydata is not None:
                index = self.draggable_points.index(self.current_draggable_point)
                
                # General case for middle points: freely movable
                new_x, new_y = event.xdata, event.ydata
                
                # Special handling for first and last control points: fixed x, free y
                if index == 0:  # First control point
                    new_x = self.control_points[index][0]  # Fix x-axis
                elif index == 3:  # Last control point, assuming 4 total points
                    new_x = self.control_points[index][0]  # Fix x-axis
                
                # Enforce y-axis constraints for non-edge points
                if 0 < index < 3:  # Only for the middle points
                    prev_y = self.control_points[index - 1][1]
                    next_y = self.control_points[index + 1][1]
                    new_y = max(prev_y + 1, min(new_y, next_y - 1))
                
                # Update and enforce constraints globally if needed
                self.control_points[index] = [new_x, new_y]
                self.enforce_y_constraints()

                # Redraw the updated points and line
                self.update_control_points_and_line()
            # Make sure this entire method is correctly indented within the class

    def update_control_points_and_line(self):
        # Update the positions of all draggable points based on the control_points array
        for draggable_point, control_point in zip(self.draggable_points, self.control_points):
            draggable_point.set_data(control_point[0], control_point[1])

        # Update the line connecting the points
        self.line.set_data(self.control_points[:, 0], self.control_points[:, 1])

        # Redraw the canvas to reflect the changes
        self.canvas.draw_idle()
        
    def enforce_y_constraints(self):
        # Ensure this method correctly enforces the y-axis constraints for your control points
        for i in range(1, len(self.control_points) - 1):  # Skip first and last points for y-axis constraint enforcement
            if self.control_points[i][1] <= self.control_points[i - 1][1]:
                self.control_points[i][1] = self.control_points[i - 1][1] + 1
            if i < len(self.control_points) - 1 and self.control_points[i][1] >= self.control_points[i + 1][1]:
                self.control_points[i + 1][1] = self.control_points[i][1] + 1
    
    def on_release(self, event):
        self.current_draggable_point = None

    def print_curve_representation(self):
        print("C Representation:")
        print("double evaluatePiecewiseLinear(double x) {")
        
        for i in range(len(self.control_points) - 1):
            xi, yi = self.control_points[i]
            xi1, yi1 = self.control_points[i+1]
            
            # Compute the slope and intercept
            mi = (yi1 - yi) / (xi1 - xi)
            bi = yi - (mi * xi)
            
            if i == 0:
                print(f"    if (x <= {xi1}) return {mi:.6f} * x + {bi:.6f};")
            else:
                print(f"    else if (x <= {xi1}) return {mi:.6f} * x + {bi:.6f};")
        
        print("    else return x;")  # Handle the case where x is beyond the last control point
        print("}")

def sigint_handler(signum, frame):
    print("Caught SIGINT (Ctrl+C). Exiting gracefully...")
    sys.exit(0)

# Register the SIGINT handler
signal.signal(signal.SIGINT, sigint_handler)

# Create the Tkinter root object and the app, then run the app as before...
root = tk.Tk()
app = ActuationForceApp(root)
root.mainloop()