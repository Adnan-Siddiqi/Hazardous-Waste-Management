import os
import tkinter as tk
from tkinter import messagebox, ttk, Text, Button
from tkcalendar import DateEntry
import pandas as pd
from pymongo import MongoClient
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import base64
import webbrowser
from plotly import graph_objs as go
from plotly.subplots import make_subplots
import Prophet

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
form_data_collection = db['formdatas']
users_collection = db['users']

# Initialize Tkinter window
window = tk.Tk()
window.title('Hazardous Waste Management Form')
window.geometry("600x400")

def center_window(window, width=300, height=200):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def signup_page():
    signup_window = tk.Toplevel(window)
    signup_window.title('Signup')
    signup_window.geometry("400x200")

    def register_user():
        username = username_entry.get()
        password = password_entry.get()
        users_collection.insert_one({'username': username, 'password': password})
        messagebox.showinfo('Success', 'Signup successful! Please login.')
        signup_window.destroy()
        login_page()

    username_label = ttk.Label(signup_window, text='Username:')
    username_label.pack()
    username_entry = ttk.Entry(signup_window)
    username_entry.pack()

    password_label = ttk.Label(signup_window, text='Password:')
    password_label.pack()
    password_entry = ttk.Entry(signup_window, show='*')
    password_entry.pack()

    signup_button = ttk.Button(signup_window, text='Signup', command=register_user)
    signup_button.pack()

def login_page():
    login_window = tk.Toplevel(window)
    login_window.title('Login')
    login_window.geometry("400x200")

    def validate_login():
        username = username_entry.get()
        password = password_entry.get()
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            messagebox.showinfo('Success', 'Login successful!')
            login_window.destroy()
            show_main_menu()
        else:
            messagebox.showerror('Error', 'Invalid username or password.')

    username_label = ttk.Label(login_window, text='Username:')
    username_label.pack()
    username_entry = ttk.Entry(login_window)
    username_entry.pack()

    password_label = ttk.Label(login_window, text='Password:')
    password_label.pack()
    password_entry = ttk.Entry(login_window, show='*')
    password_entry.pack()

    login_button = ttk.Button(login_window, text='Login', command=validate_login)
    login_button.pack()

def show_main_menu():
    main_menu_window = tk.Toplevel(window)
    main_menu_window.title('Main Menu')
    main_menu_window.geometry("400x300")

    data_entry_button = ttk.Button(main_menu_window, text='Data Entry', command=main_app)
    data_entry_button.pack()

    view_data_button = ttk.Button(main_menu_window, text='View Data', command=view_data_page)
    view_data_button.pack()

    forecast_button = ttk.Button(main_menu_window, text='Forecast Waste', command=forecast_page)
    forecast_button.pack()

    logout_button = ttk.Button(main_menu_window, text='Logout', command=window.destroy)
    logout_button.pack()

def main_app():
    main_window = tk.Toplevel(window)
    main_window.title('Hazardous Waste Management Form')
    main_window.geometry("800x600") 

    date_label = ttk.Label(main_window, text='Date:')
    date_label.grid(row=0, column=0, padx=10, pady=10)
    selected_date = DateEntry(main_window, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    selected_date.grid(row=0, column=1, padx=10, pady=10)

    # Function to format date before storing
    def get_formatted_date():
        return selected_date.get_date().strftime('%Y-%m-%d')

    # Select Division Dropdown
    division_label = ttk.Label(main_window, text='Select Division:')
    division_label.grid(row=1, column=0, padx=10, pady=10)
    division_options = ['GD ENGINE', 'TNGA ENGINE', 'Auto Parts', 'Utilities']
    selected_division = ttk.Combobox(main_window, values=division_options)
    selected_division.grid(row=1, column=1, padx=10, pady=10)

    # Input Fields - Organized in 2 Columns
    input_labels = [
        ("Used oil from shopfloor", "1"),
        ("Used glove and cloth", "2"),
        ("Compressor filters", "3"),
        ("Band/oiled filter papers", "4"),
        ("Paint waste", "5"),
        ("Adhesive (FIPG)", "6"),
        ("DG Chimney", "7"),
        ("Softner resin", "8"),
        ("Carbuoys", "9"),
        ("Metal barrels", "10"),
        ("Chemical sludge", "11"),
        ("Skimmed oil", "12"),
        ("Grinding Muck", "13"),
        ("Fuel Filters", "14"),
        ("Lapping Tape", "15"),
        ("Epoxy Waste", "16"),
        ("Test Bench Chimney", "17"),
        ("Plastic Barrels", "18"),
        ("Paint Containers", "19"),
        ("Oil Emulsion", "20"),
        ("DG Filers", "21"),
        ("Prowipe Paper", "22"),
        ("Canteen Chimney", "23"),
        ("Metal Buckets", "24"),
        ("Spray Containers", "25"),
        ("Saw Dust", "26"),
        ("Residue with Oil", "27"),
        ("Plastic Buckets", "28"),
    ]

    row_counter = 2
    column_counter = 0
    input_entries = {}  # Dictionary to store input entry widgets

    for label, id in input_labels:
        label_widget = ttk.Label(main_window, text=label)
        label_widget.grid(row=row_counter, column=column_counter, padx=10, pady=5)
        input_entry = ttk.Entry(main_window)
        input_entry.grid(row=row_counter, column=column_counter + 1, padx=10, pady=5)
        input_entries[id] = input_entry  # Add entry widget to the dictionary
        column_counter += 2
        if column_counter >= 4:  # Adjust column count for every 2 fields
            column_counter = 0
            row_counter += 1

    # Submit Button
    def submit_form():
        # Get the entered date and selected division
        form_data = {
            "Date": selected_date.get(),
            "Division": selected_division.get(),
        }

        # Convert input values to floats and handle empty strings as 0
        for label, id in input_labels:
            input_value = input_entries[id].get()
            input_value = float(input_value) if input_value else 0
            form_data[label] = input_value

        # Insert form data into the MongoDB collection
        form_data_collection.insert_one(form_data)

        # Show success message and optionally clear the input fields
        messagebox.showinfo("Success", "Form data submitted and stored in MongoDB!")
        selected_date.delete(0, tk.END)
        selected_division.set('')
        for entry in input_entries.values():
            entry.delete(0, tk.END)

    submit_button = ttk.Button(main_window, text='Submit', command=submit_form)
    submit_button.grid(row=row_counter, column=0, columnspan=2, pady=10)
    logout_button = ttk.Button(main_window, text='Logout', command=window.destroy)
    logout_button.grid(row=row_counter, column=3, columnspan=2, pady=10)

def view_data_page():
    view_data_window = tk.Toplevel(window)
    view_data_window.title('View Data')
    view_data_window.geometry("800x600")
    # Retrieve data from MongoDB
    form_data_cursor = form_data_collection.find()
    form_data_list = list(form_data_cursor)
    data = pd.DataFrame(form_data_list)

    # Convert 'Date' column to datetime format
    data['Date'] = pd.to_datetime(data['Date'])

    # Display data in a structured table format using DataFrameViewer
    data_viewer = ttk.Treeview(view_data_window)
    data_viewer['columns'] = list(data.columns)
    data_viewer['show'] = 'headings'  # Show only the column headers

    # Add column headings
    for col in data_viewer['columns']:
        data_viewer.heading(col, text=col)

    # Add data rows
    for index, row in data.iterrows():
        data_viewer.insert("", "end", values=list(row))

    data_viewer.pack(expand=tk.YES, fill=tk.BOTH)

def forecast_page():
    forecast_window = tk.Toplevel(window)
    forecast_window.title('Forecast Waste')
    forecast_window.geometry("800x600")

    # Retrieve data from MongoDB
    form_data_cursor = form_data_collection.find()
    form_data_list = list(form_data_cursor)
    data = pd.DataFrame(form_data_list)

    # Convert 'Date' column to datetime format
    data['Date'] = pd.to_datetime(data['Date'])

    # Aggregate data for forecasting
    data_agg = data.groupby('Date').sum().reset_index()
    data_agg = data_agg.rename(columns={'Date': 'ds', 'Used oil from shopfloor': 'y'})

    # Initialize Prophet model
    model = Prophet()

    # Fit model with historical data
    model.fit(data_agg)

    # Create future dates for forecasting
    future_dates = model.make_future_dataframe(periods=30)  # Forecasting for next 30 days

    # Make forecasts
    forecast = model.predict(future_dates)

    # Plotting forecast
    fig = plt.figure(figsize=(12, 6))
    plt.plot(data_agg['ds'], data_agg['y'], label='Actual')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='--')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.2)
    plt.xlabel('Date')
    plt.ylabel('Waste Quantity')
    plt.title('Waste Quantity Forecast')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Display the plot in the tkinter window
    canvas = FigureCanvasTkAgg(fig, master=forecast_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Center the main window on the screen
center_window(window, 600, 400)

# Create the main menu buttons
signup_button = ttk.Button(window, text='Signup', command=signup_page)
signup_button.pack()

login_button = ttk.Button(window, text='Login', command=login_page)
login_button.pack()

# Start the tkinter main loop
window.mainloop()
