import streamlit as st
import pandas as pd
import math

# Function to load the CSV data into the session and clean the columns
@st.cache_data
def load_data():
    butt_chart = pd.read_csv('Ripplefold Fabrication Chart - Butt.csv')
    overlap_chart = pd.read_csv('Ripplefold Fabrication Chart - Overlap.csv')
    
    # Clean column names to remove extra spaces and replace spaces with underscores
    butt_chart.columns = butt_chart.columns.str.strip().str.replace(' ', '_')
    overlap_chart.columns = overlap_chart.columns.str.strip().str.replace(' ', '_')
    
    return butt_chart, overlap_chart

# Load the CSV files
butt_chart, overlap_chart = load_data()

# Initialize session state to store yardages and outputs for each drape
if "drapes_data" not in st.session_state:
    st.session_state.drapes_data = {}

# Utility function to round up to the nearest 1/4 (0.25)
def round_up_to_quarter(value):
    return math.ceil(value * 4) / 4

# Function to calculate TOTAL WIDTH EACH PANEL based on pleat type
def calculate_total_width_each_panel(pleat_type, panel_width, fullness, side_returns, csv_data, butt_or_overlap=None, ripplefold_fullness=None):
    if pleat_type == "REGULAR":
        total_width = panel_width * fullness + 6 + side_returns
    elif pleat_type == "RIPPLEFOLD" and ripplefold_fullness:
        # Sanitize ripplefold_fullness input by stripping the word "Fullness"
        ripplefold_value = ripplefold_fullness.replace('Fullness ', '').strip()
        ripplefold_column = f'Fullness_{ripplefold_value}'
        
        # Use the correct CSV file based on 'Butt' or 'Overlap' selection
        if butt_or_overlap == "Butt":
            row = csv_data[0].loc[csv_data[0][ripplefold_column] >= panel_width].iloc[0]
        else:
            row = csv_data[1].loc[csv_data[1][ripplefold_column] >= panel_width].iloc[0]
        
        tape_length = row['Tape_Length']
        total_width = tape_length + 6 + side_returns
    else:
        total_width = 0  # Default for no selection
    return total_width

# Function to calculate Number of Fabric Widths (rounded to 2 decimal places)
def calculate_number_of_fabric_widths(total_width, fabric_width, panel_type):
    widths = total_width / fabric_width
    if panel_type == "PAIR":
        # No need to multiply by 2, since total_width is already for each panel
        return round(widths, 2)
    return round(widths, 2)  # Round to 2 decimal places

# Function to calculate Cut Height
def calculate_cut_height(height, bottom_hem, vertical_repeat, liner):
    if liner == "YES":
        return height + bottom_hem + vertical_repeat + 2
    else:
        return height + bottom_hem + vertical_repeat + 12

# Function to calculate WIDTH EACH SIDE with specific rounding rules for Single Panel and Pair
def calculate_width_each_side(fabric_widths, panel_type):
    if panel_type == "SINGLE PANEL":
        # Round up to the next integer
        return math.ceil(fabric_widths)
    elif panel_type == "PAIR":
        # Round up to the next 1/2
        return math.ceil(fabric_widths * 2) / 2


# Function to calculate Yardage (rounded to 2 decimal places)
def calculate_yardage(cut_height, width_each_side, panel_type):
    if panel_type == "SINGLE PANEL":
        return round((cut_height * width_each_side) / 36, 2)
    elif panel_type == "PAIR":
        return round((cut_height * width_each_side * 2) / 36, 2)

# Sidebar to select the number of drapes
st.sidebar.header("Drapery Calculator")
num_drapes = st.sidebar.number_input("Select number of drapes", min_value=1, max_value=50, value=1)

# Loop over the number of drapes to display input fields for each drape
for i in range(num_drapes):
    st.subheader(f"Custom Drapes #{i + 1}")
    
    pleat_type = st.selectbox(f"Pleat Type - Drapes #{i + 1}", ["REGULAR", "RIPPLEFOLD"])
    
    if pleat_type == "RIPPLEFOLD":
        # Default to "Fullness 100" for Ripplefold
        ripplefold_fullness = st.selectbox(f"Ripplefold Fullness - Drapes #{i + 1}", ["Fullness 60", "Fullness 80", "Fullness 100", "Fullness 120"], index=2)
        butt_or_overlap = st.radio(f"Butt or Overlap - Drapes #{i + 1}", ["Butt", "Overlap"])
        fullness = None  # Set to None as it's not used for Ripplefold
    else:
        ripplefold_fullness, butt_or_overlap = None, None
        # Default to "2.5" for Regular Fullness
        fullness = st.selectbox(f"Regular Fullness - Drapes #{i + 1}", [1, 1.5, 2, 2.2, 2.5, 3, 3.5], index=4)
    
    width = st.number_input(f"Width (inches) - Drapes #{i + 1}", min_value=0, value=72)
    height = st.number_input(f"Height (inches) - Drapes #{i + 1}", min_value=0, value=90)
    liner = st.radio(f"Liner - Drapes #{i + 1}", ["YES", "NO"])
    panel_type = st.radio(f"Panel Type - Drapes #{i + 1}", ["PAIR", "SINGLE PANEL"])
    fabric_width = st.number_input(f"Fabric Width (inches) - Drapes #{i + 1}", min_value=0, value=54)
    bottom_hem = st.number_input(f"Bottom Hem (inches) - Drapes #{i + 1}", min_value=0, value=10)
    vertical_repeat = st.number_input(f"Vertical Repeat (inches) - Drapes #{i + 1}", min_value=0.0, value=0.0)
    side_returns = st.number_input(f"Side Returns (inches) - Drapes #{i + 1}", min_value=0.0, value=3.5)
    
    # Calculation button
    if st.button(f"Calculate - Drapes #{i + 1}"):
        panel_width = width / (2 if panel_type == "PAIR" else 1)
        
        # Pass the correct fullness or ripplefold_fullness based on pleat type
        total_width_each_panel = calculate_total_width_each_panel(pleat_type, panel_width, fullness, side_returns, (butt_chart, overlap_chart), butt_or_overlap, ripplefold_fullness)
        fabric_widths = calculate_number_of_fabric_widths(total_width_each_panel, fabric_width, panel_type)
        cut_height = calculate_cut_height(height, bottom_hem, vertical_repeat, liner)
        width_each_side = calculate_width_each_side(fabric_widths, panel_type)
        yardage = calculate_yardage(cut_height, width_each_side, panel_type)
        
        # Store the results for this drape in session state
        st.session_state.drapes_data[f"Drapes #{i + 1}"] = {
            "Total Width Each Panel": total_width_each_panel,
            "Number of Fabric Widths": fabric_widths,
            "Cut Height": cut_height,
            "Width Each Side": width_each_side,
            "Yardage": yardage
        }

    # Display results for the current drape after input fields
    if f"Drapes #{i + 1}" in st.session_state.drapes_data:
        drape_data = st.session_state.drapes_data[f"Drapes #{i + 1}"]
        st.write(f"Results for Drapes #{i + 1}:")
        st.write(f"Total Width Each Panel: {drape_data['Total Width Each Panel']}")
        st.write(f"Number of Fabric Widths: {drape_data['Number of Fabric Widths']:.2f}")
        st.write(f"Cut Height: {drape_data['Cut Height']}")
        st.write(f"Width Each Side: {drape_data['Width Each Side']}")
        st.write(f"Yardage: {drape_data['Yardage']:.2f}")
        st.write("---")

# Calculate the total yardage for all drapes and display it at the bottom
if st.session_state.drapes_data:
    total_yardage = sum(drape_data['Yardage'] for drape_data in st.session_state.drapes_data.values())
    st.subheader("Total Yardage for All Drapes")
    st.write(f"Total Yardage: {total_yardage:.2f} yards")


