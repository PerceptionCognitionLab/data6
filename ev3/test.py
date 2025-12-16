from psychopy import core, visual, event
import serial
import numpy as np

# ==== SERIAL CONFIG ====
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0.01)
ser.reset_input_buffer()

# ==== WINDOW ====
win = visual.Window(size=(1400, 600), color=[-1, -1, -1], units="pix", fullscr=False)
win_width = win.size[0]
win_height = win.size[1]

# ==== PARAMETERS ====
bar_color = "white"
line_color = [1, 0, 0]  # red
bar_width = 0.6
x_range = 200     # much wider now
max_bar_height = 50

# Top border: V shape y = |x|
# Bottom border: y = -(x/2)^2

# ==== STATIC BORDER LINES ====

# Upper line - two halves of V
upper_line_left = visual.Line(
    win,
    start=(-x_range, abs(-x_range)),
    end=(0, 0),
    lineColor=line_color,
    lineWidth=1
)
upper_line_right = visual.Line(
    win,
    start=(0, 0),
    end=(x_range, abs(x_range)),
    lineColor=line_color,
    lineWidth=1
)

# Bottom curve - approximate quadratic with many small line segments

num_points = 300
x_vals = np.linspace(-x_range, x_range, num_points)
y_vals = - (x_vals / 2) ** 2

bottom_curve_segments = []
for i in range(num_points - 1):
    seg = visual.Line(
        win,
        start=(x_vals[i], y_vals[i]),
        end=(x_vals[i + 1], y_vals[i + 1]),
        lineColor=line_color,
        lineWidth=1
    )
    bottom_curve_segments.append(seg)

# ==== VERTICAL BAR ====
bar = visual.Rect(
    win,
    width=bar_width,
    height=10,
    fillColor=bar_color,
    lineColor=bar_color,
    pos=(0, 0),
    anchor='bottom'
)

print("Running. Press ESC to exit.")
while True:
    if "escape" in event.getKeys():
        break

    # ==== READ POTENTIOMETER ====
    line = None
    while ser.in_waiting:
        try:
            raw = ser.readline().decode("utf-8", errors="ignore").strip()
            if raw:
                line = raw
        except Exception:
            continue

    if line and line.isdigit():
        val = int(line)
        norm_val = (val - 512) / 512.0  # Range -1 to 1

        # ==== MAP TO X POSITION ====
        x_pos = norm_val * x_range

        # ==== COMPUTE HEIGHT BETWEEN BORDERS AT X ====
        upper_y = abs(x_pos)
        lower_y = - (x_pos / 2) ** 2

        bar_height = upper_y - lower_y
        bar_height = max(1, min(bar_height, max_bar_height))

        # ==== UPDATE BAR ====
        bar.pos = (x_pos, lower_y)
        bar.height = bar_height

    # ==== DRAW ====
    upper_line_left.draw()
    upper_line_right.draw()
    for seg in bottom_curve_segments:
        seg.draw()
    bar.draw()
    win.flip()

# ==== CLEAN UP ====
ser.close()
win.close()
core.quit()
