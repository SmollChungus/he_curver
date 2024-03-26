import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import signal
import sys

class ActuationForceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Actuation Force Curve Editor")
        self.root.geometry("600x450")

        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor='#F3BBAF')
        self.plot = self.fig.add_subplot(111)
        self.plot.set_title("Actuation Force Curve")
        self.plot.set_xlabel("Switch Travel (%)")
        self.plot.set_ylabel("Analog Output (%)")
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

                self.update_control_points_and_line()

    def update_control_points_and_line(self):
        # Remove the previous deadzone and area fill
        if self.deadzone_fill:
            self.deadzone_fill.remove()
        if self.area_fill:
            self.area_fill.remove()

        # Update the line connecting the points
        self.line.set_data(self.control_points[:, 0], self.control_points[:, 1])

        # Then, update the positions of all draggable points based on the control_points array
        for draggable_point, control_point in zip(self.draggable_points, self.control_points):
            draggable_point.set_data(control_point[0], control_point[1])

        # Create a continuous x array for filling, to ensure the fill is continuous
        x_fill = np.linspace(self.control_points[0][0], self.control_points[-1][0], 500)
        y_line = np.interp(x_fill, self.control_points[:, 0], self.control_points[:, 1])

        # Fill the deadzone with checkered pattern, which is below the first control point's y-value
        self.deadzone_fill = self.plot.fill_between(
            x_fill, 0, self.control_points[0][1],
            facecolor='#BBAFF3', hatch='//', edgecolor='#6A58BE', alpha=1
        )

        # Fill the area between the curve and the x-axis with yellow
        # We use y_line to ensure that we are filling under the curve defined by the line
        self.area_fill = self.plot.fill_between(
            x_fill, self.control_points[0][1], y_line,
            where=(y_line >= self.control_points[0][1]),
            facecolor='pink', alpha=0.95
        )

        # Redraw the canvas to reflect the changes
        self.canvas.draw_idle()

        
    def enforce_y_constraints(self):
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

signal.signal(signal.SIGINT, sigint_handler)

root = tk.Tk()
app = ActuationForceApp(root)
root.mainloop()
