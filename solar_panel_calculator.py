import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import pandas as pd
import numpy as np
import os
import sys

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors

def get_csv_path(filename):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, filename)

csv_file = get_csv_path("data.csv")

def handle_checkbox_selection():
    if acre_checkbox_var.get():
        acre_dropdown.config(state=tk.DISABLED)
        area_entry.config(state=tk.NORMAL)
    else:
        acre_dropdown.config(state=tk.NORMAL)
        area_entry.config(state=tk.DISABLED)

def update_tumbols(*args):
    selected_province = province_var.get()
    # Filter Tumbols based on the selected province
    tumbols = data[data["Province"] == selected_province]["Tumbol"].unique().tolist()
    tumbol_dropdown['values'] = tumbols
    tumbol_dropdown.set("")

def calculate_solar_energy():
    tumbol = tumbol_var.get()
    if acre_checkbox_var.get():
        area = float(area_entry.get()) * 1600
    else:
        area = float(acre_var.get()) * 1600

    # Default values
    hours_of_sunlight = 5
    days = 120
    solar_W = 0.45
    panel_efficiency = 0.2
    panel_area = 2

    # Load data
    data = pd.read_csv(csv_file)

    # Find data for selected Tumbol
    tumbol_data = data[data["Tumbol"] == tumbol]
    # Read Province data from CSV
    provinces = data["Province"].unique().tolist()

    required_electricity = data["total"].values[0]

    area_new = area / 1600

    # Check if required_electricity_entry is not empty
    if required_electricity_entry.get():
        required_electricity_new = float(required_electricity_entry.get()) * area_new
    else:
        required_electricity_new = required_electricity * area_new

    # Calculate energy per panel per day
    kwh_per_panel_per_day = (
        tumbol_data["solar_energy"].values[0]
        / 3.6
        * panel_efficiency
        * hours_of_sunlight
        * solar_W
    )
    # Calculate number of solar panels needed
    number_of_panels = 1
    while True:
        total_kwh = kwh_per_panel_per_day * number_of_panels * days
        if total_kwh >= required_electricity_new:
            break
        number_of_panels += 1

    # Display results
    result_label.config (
        text=f"ความเข้มของพลังงานแสงอาทิตย์: {tumbol_data['solar_energy'].values[0]} mj/m2\n"
        f"จำนวนแผงโซล่าเซลล์ที่ต้องการ: {number_of_panels:,.0f} แผง\n"
        f"จำนวนไฟฟ้าที่ต้องการ: {required_electricity_new:,.2f} kW\n"
        f"จำนวนไฟฟ้าที่ผลิตได้: {total_kwh:,.2f} kW\n"
        f"จำนวนไฟฟ้าที่ผลิตมาเกิน: {total_kwh - required_electricity_new:,.2f} kW\n"
        f"พื้นที่สำหรับติดตั้งโซล่าเซลล์: {number_of_panels * panel_area:,.2f} ตารางเมตร\n"
        f"พื้นที่ที่เหลือ: {area - number_of_panels * panel_area:,.2f} ตารางเมตร"
    )

    # Calculate areas
    area_used = number_of_panels * panel_area
    area_remaining = area - area_used

    # Waffle Chart Data
    categories = ["Solar area", "Space"]
    values = [area_used, area_remaining]
    width = 10
    height = 10
    colormap = ['#3234a8', '#008000']
    cmap = mcolors.LinearSegmentedColormap.from_list("mycmap", colormap)
    # Show the chart
    create_waffle_chart(categories, values, width, height, cmap, canvas)
    canvas.draw()
    fig.clear()
    #plt.show()

# Function to create waffle chart
def create_waffle_chart(categories, values, width, height, cmap, canvas):
    total_values = sum(values)
    category_proportions = [(float(value) / total_values) for value in values]
    total_num_tiles = width * height
    tiles_per_category = [round(proportion * total_num_tiles) for proportion in category_proportions]

    waffle_chart = np.zeros((height, width))
    category_index = 0
    tile_index = 0

    for col in range(width):
        for row in range(height):
            tile_index += 1

            if tile_index > sum(tiles_per_category[0:category_index]):
                category_index += 1

            waffle_chart[row, col] = category_index

    ax = canvas.figure.add_subplot(111)
    ax.matshow(waffle_chart, cmap=cmap)

    ax.set_xticks(np.arange(-0.5, (width), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, (height), 1), minor=True)
    ax.grid(which='minor', color='Black', linestyle='-', linewidth=2)

    ax.set_xticks([])
    ax.set_yticks([])

    values_cumsum = np.cumsum(values)
    legend_handles = []
    for i, category in enumerate(categories):
        if i == 0:
            color_val = '#3234a8'
        else:
            color_val = '#008000'
        if i == 0:
            label_str = f"{category}: {values[i]:,.0f} sq.m"
        else:
            label_str = f"{category}: {values[i]:,.0f} sq.m"
        #color_val = colormap(float(i) / len(categories))
        legend_handles.append(plt.Line2D([0], [0], marker='s', color=color_val, markerfacecolor=color_val, markersize=15, label=label_str))

    ax.legend(
        handles=legend_handles,
        loc='lower center',
        ncol=len(categories),
        bbox_to_anchor=(0.5, -0.2),
        framealpha=0.0,
        handletextpad=0.5,
    )
    ax.set_title(' ({:,.0f} sq.m / {:,.0f} sq.m)'.format(values_cumsum[i - 1], values_cumsum[i]))

debug_info_shown = False

def toggle_debug_info(event=None):
    global debug_info_shown
    if debug_info_shown:
        required_electricity_label.grid_forget()
        required_electricity_entry.grid_forget()
        required_electricity_entry.delete(0, tk.END)
        debug_info_shown = False
    else:
        required_electricity_label.grid(row=3, column=0, padx=(0, 10), pady=5, sticky="e")
        required_electricity_entry.grid(row=3, column=1, padx=(0, 10), pady=5, sticky="w")
        debug_info_shown = True



root = tk.Tk()
root.title("Solar Panel Calculator")

# Apply ttkbootstrap style
style = Style(theme='cosmo')
style.configure('TLabel', font=('Tahoma', 12))
style.configure('TButton', font=('Tahoma', 12))
style.configure('TRadiobutton', font=('Tahoma', 12))
style.configure('TCombobox', font=('Tahoma', 12))

# Read Tumbol data from CSV
data = pd.read_csv(csv_file)
tumbols = data["Tumbol"].unique().tolist()

# app_title_label = ttk.Label(root, text="", font=("Tahoma", 1, "bold"))
# app_title_label.grid(row=0, column=0, columnspan=1, pady=10, sticky="nsew") 

# Province selection
province_label = ttk.Label(root, text="จังหวัด:")
province_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="e")
provinces = data["Province"].unique().tolist()
province_var = tk.StringVar()
province_dropdown = ttk.Combobox(root, textvariable=province_var, values=provinces, state="readonly")
province_dropdown.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="e")
province_dropdown.bind("<<ComboboxSelected>>", update_tumbols)

# Tumbol selection
tumbol_label = ttk.Label(root, text="ตำบล:")
tumbol_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="e")
tumbol_var = tk.StringVar()
tumbol_dropdown = ttk.Combobox(
    root, textvariable=tumbol_var, values=tumbols,state="readonly"
)
tumbol_dropdown.grid(row=1, column=1, padx=10, pady=(10, 5), sticky="w")

# Total area entry
area_label = ttk.Label(root, text="พื้นที่ทั้งหมด (ไร่):")
area_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

acre_var = tk.StringVar()
acre_checkbox_var = tk.IntVar()
acre_checkbox = ttk.Checkbutton(
    root,
    text="กรอกจำนวนไร่เอง",
    variable=acre_checkbox_var,
    bootstyle="info-round-toggle",
    command=handle_checkbox_selection
)
acre_checkbox.grid(row=2, column=1, padx=(0, 2), pady=5, sticky="w")

acre_dropdown = ttk.Combobox(
    root, textvariable=acre_var, state="readonly"
)
acre_dropdown["values"] = tuple(range(1, 11))
acre_dropdown.grid(row=2, column=2, padx=(0, 2), pady=5, sticky="w")

area_entry = ttk.Entry(
    root,
    state=tk.NORMAL if acre_checkbox_var.get() else tk.DISABLED,
)
area_entry.grid(row=2, column=3, padx=(0, 10), pady=5, sticky="w")

required_electricity_label = ttk.Label(root, text="Debug(kW):")
required_electricity_entry = ttk.Entry(root, state=tk.NORMAL)

# Ctrl+D เปิดปุ่ม Debug
root.bind('<Control-d>', toggle_debug_info)

calculate_button = ttk.Button(
    root, text="คำนวณ", command=calculate_solar_energy
)
calculate_button.grid(row=4, column=0, columnspan=4, padx=10, pady=10)


# Label แสดงหน้าจอ
result_sum_label = ttk.Label(root, text="ผลลัพท์", font=("Tahoma", 16))
result_sum_label.grid(row=5, column=0, columnspan=4, pady=(20, 5))

result_label = ttk.Label(root, text="")
result_label.grid(row=6, column=0, columnspan=4, padx=15, pady=5)

# สร้าง Frame สำหรับกราฟ
plot_frame = ttk.Frame(root)
plot_frame.grid(row=7, column=0, columnspan=4, padx=10, pady=10, sticky="w")
fig, ax = plt.subplots(figsize=(5, 3))
ax.axis('off')

# สร้าง Canvas สำหรับแสดงกราฟ
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)



# หมายเหตุ
# text_note = ttk.Label(
#     root,
#     text="*Highlights* : อนาคตจะมีการเปลี่ยนแปลงเป็นการประมวลผลอัตโนมัติ",background="orange"
# )
# text_note.grid(row=7, column=0, columnspan=2, sticky="n")

root.mainloop()

#pyinstaller --onefile --windowed --add-data "data.csv;." solar_panel_calculator.py
