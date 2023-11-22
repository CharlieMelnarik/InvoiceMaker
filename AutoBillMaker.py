import csv
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess


# Function to create or load the CSV file
def create_or_load_csv(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Customer Name", "Vehicle", "Hours", "Price Per Hour", "Part Name", "Price Per Part", "Shop Supplies", "Notes"])

# Function to add a new invoice entry
def add_invoice(file_path, customer_name, vehicle, hours, price_per_hour, part_name, price_per_part, shop_supplies, notes):
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([customer_name, vehicle, hours, price_per_hour, part_name, price_per_part, shop_supplies, notes])
    messagebox.showinfo("Success", "Invoice added successfully!")

# Function to update an existing invoice entry
def update_invoice(file_path, customer_name, new_hours=None, new_price_per_hour=None, new_part_name=None, new_price_per_part=None, new_shop_supplies=None, new_notes=None, new_vehicle=None):
    rows = []
    customer_exists = False
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        if "Notes" not in header:
            # If "Notes" column doesn't exist, add it to the header
            header.append("Notes")
        if "Vehicle" not in header:
            # If "Vehicle" column doesn't exist, add it to the header
            header.insert(1, "Vehicle")
        if "Shop Supplies" not in header:
            # If "Shop Supplies" column doesn't exist, add it to the header
            header.insert(6, "Shop Supplies")
        rows.append(header)
        for row in reader:
            if row[0].lower() == customer_name.lower():
                customer_exists = True
                # Update the specified fields
                if new_hours is not None:
                    row[2] = str(float(row[2]) + float(new_hours)) if row[2] and row[2] != 'none' else str(new_hours)
                if new_price_per_hour is not None:
                    row[3] = str(new_price_per_hour)
                if new_part_name is not None:
                    if row[4]:
                        row[4] += f", {new_part_name}"
                    else:
                        row[4] = new_part_name
                if new_price_per_part is not None:
                    if row[5]:
                        row[5] += f", {new_price_per_part}"
                    else:
                        row[5] = str(new_price_per_part)
                if new_shop_supplies is not None:
                    row[6] = str(new_shop_supplies)
                if new_notes is not None:
                    if len(row) <= 7:
                        # If "Notes" column doesn't exist, add it to the row
                        row.append(new_notes)
                    else:
                        existing_notes = row[7] if len(row) > 7 else ""
                        row[7] = existing_notes + (", " + new_notes) if existing_notes else new_notes
                if new_vehicle is not None:
                    row[1] = new_vehicle if new_vehicle else row[1]  # Retain existing vehicle if new vehicle is empty
            rows.append(row)

    if not customer_exists:
        messagebox.showinfo("Info", "Existing customer does not exist. This name will be entered as a new customer.")
        add_invoice(file_path, customer_name, new_vehicle, new_hours, new_price_per_hour, new_part_name, new_price_per_part, new_shop_supplies, new_notes)
    else:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        messagebox.showinfo("Success", "Invoice updated successfully!")

# Function to check if a customer exists and print information
def check_customer(file_path, customer_name):
    info_text = ""
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if row[0].lower() == customer_name.lower():
                info_text += f"Customer Name: {row[0]}\n"
                info_text += f"Vehicle: {row[1]}\n"
                info_text += f"Hours: {row[2]}\n"
                info_text += f"Price Per Hour: ${row[3]}\n"
                parts_info = ", ".join([f"{part}: ${price}" for part, price in zip(row[4].split(", "), row[5].split(", "))])
                info_text += f"Part Name: {parts_info}\n"
                info_text += f"Shop Supplies: ${row[6]}\n"
                break
        else:
            info_text = f"No information found for customer: {customer_name}"

    messagebox.showinfo("Customer Information", info_text)

# Function to generate a PDF invoice
def generate_pdf(file_path, customer_name):
    pdf_filename = f"Invoice_{customer_name.replace(' ', '_')}.pdf"
    customer_found = False

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if row[0].lower() == customer_name.lower():
                customer_found = True
                c = canvas.Canvas(pdf_filename, pagesize=letter)
                width, height = letter

                # Set font and size for the title
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(width / 2, height - 50, "Invoice")

                # Set font and size for the customer information
                c.setFont("Helvetica", 12)
                c.drawRightString(width - 50, height - 80, f"Customer Name: {row[0]}")
                c.drawString(50, height - 80, f"Vehicle: {row[1]}")
                c.drawRightString(width - 50, height - 120, f"Hours: {row[2]}")
                c.drawRightString(width - 50, height - 140, f"Price Per Hour: ${row[3]}")

                # Set font and size for the part information
                c.drawString(50, height - 160, "Parts:")
                y_position = height - 180
                if row[4] and row[5]:
                    for part, price in zip(row[4].split(", "), row[5].split(", ")):
                        if part.strip():
                            c.drawString(70, y_position, f"{part}")
                            if price.strip() and price.lower() != 'none':
                                try:
                                    c.drawRightString(width - 50, y_position, f"${float(price)}")
                                except ValueError:
                                    c.drawRightString(width - 50, y_position, f"{price}")
                            y_position -= 20

                # Set font and size for the shop supplies information
                c.drawString(50, y_position - 80, f"Shop Supplies: ${row[6]}")

                # Calculate and display the total cost
                try:
                    total_cost = float(row[2]) * float(row[3])
                except ValueError:
                    total_cost = 0.0

                if row[5]:
                    for price in row[5].split(", "):
                        if price.strip() and price.lower() != 'none':
                            try:
                                total_cost += float(price)
                            except ValueError:
                                pass

                # Add shop supplies cost to the total cost
                total_cost += float(row[6])

                # Round the total cost to two decimal places
                total_cost = round(total_cost, 2)

                # Set font and size for the total cost
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y_position - 120, f"Total Cost:")
                c.drawRightString(width - 50, y_position - 120, f"${total_cost}")

                # Set font and size for the notes
                notes = row[7] if len(row) > 7 else "No notes available"
                c.setFont("Helvetica", 10)
                c.drawString(50, y_position - 180, f"Notes: {notes}")

                c.save()
                messagebox.showinfo("Success", f"PDF invoice generated: {pdf_filename}")
                break  # Break out of the loop after generating PDF for the customer

    if not customer_found:
        messagebox.showinfo("Info", f"No invoice found for customer: {customer_name}")




# Main GUI window
class InvoiceApp:
    def __init__(self, master):
        self.master = master
        master.title("Invoice Management")

        # Set window size to be mostly full screen
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        master.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Add a blueish background color
        master.configure(bg="#3498db")

        self.file_path = 'invoices.csv'
        create_or_load_csv(self.file_path)

        self.label = tk.Label(master, text="Select an option:", font=("Helvetica", 16, "bold"), bg="#3498db", fg="white")
        self.label.pack(pady=20)

        button_style = {"font": ("Helvetica", 14), "bg": "#2980b9", "fg": "black", "padx": 20, "pady": 10, "borderwidth": 2}

        self.add_button = tk.Button(master, text="Add New Invoice", command=self.add_invoice_gui, **button_style)
        self.add_button.pack(pady=10)

        self.update_button = tk.Button(master, text="Update Existing Invoice", command=self.update_invoice_gui, **button_style)
        self.update_button.pack(pady=10)

        self.pdf_button = tk.Button(master, text="Generate PDF Invoice", command=self.generate_pdf_gui, **button_style)
        self.pdf_button.pack(pady=10)

        self.check_button = tk.Button(master, text="Check Customer Information", command=self.check_customer_gui, **button_style)
        self.check_button.pack(pady=10)

        self.notes_button = tk.Button(master, text="Add Notes", command=self.add_notes_gui, **button_style)
        self.notes_button.pack(pady=10)

        self.exit_button = tk.Button(master, text="Exit", command=self.master.destroy, **button_style)
        self.exit_button.pack(pady=20)

    def add_invoice_gui(self):
        customer_name = simpledialog.askstring("Customer Name", "Enter customer name:")
        vehicle = simpledialog.askstring("Vehicle", "Enter vehicle:")
        hours = float(simpledialog.askstring("Hours", "Enter hours worked:"))
        price_per_hour = float(simpledialog.askstring("Price Per Hour", "Enter price per hour:"))
        price_per_part = float(simpledialog.askstring("Price Per Part", "Enter price per part:"))
        part_name = simpledialog.askstring("Part Name", "Enter part name:")
        shop_supplies = float(simpledialog.askstring("Shop Supplies", "Enter shop supplies cost:"))
        notes = simpledialog.askstring("Notes", "Enter notes:")
        add_invoice(self.file_path, customer_name, vehicle, hours, price_per_hour, part_name, price_per_part, shop_supplies, notes)

    def update_invoice_gui(self):
        customer_name = simpledialog.askstring("Customer Name", "Enter customer name for updating:")
        new_hours = simpledialog.askstring("New Hours", "Enter new hours (press Enter to skip):")
        new_price_per_hour = simpledialog.askstring("New Price Per Hour", "Enter new price per hour (press Enter to skip):")
        new_part_name = simpledialog.askstring("New Part Name", "Enter new part name (press Enter to skip):")
        new_price_per_part = simpledialog.askstring("New Price Per Part", "Enter new price per part (press Enter to skip):")
        new_shop_supplies = simpledialog.askstring("New Shop Supplies", "Enter new shop supplies cost (press Enter to skip):")
        new_notes = simpledialog.askstring("New Notes", "Enter new notes (press Enter to skip):")
        new_vehicle = simpledialog.askstring("New Vehicle", "Enter new vehicle (press Enter to skip):")

        try:
            if any(value.strip() for value in [new_hours, new_price_per_hour, new_price_per_part, new_shop_supplies]):
                new_hours = float(new_hours) if new_hours.strip() else None
                new_price_per_hour = float(new_price_per_hour) if new_price_per_hour.strip() else None
                new_price_per_part = float(new_price_per_part) if new_price_per_part.strip() else None
                new_shop_supplies = float(new_shop_supplies) if new_shop_supplies.strip() else None
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid number.")
            return

        update_invoice(self.file_path, customer_name, new_hours, new_price_per_hour, new_part_name, new_price_per_part, new_shop_supplies, new_notes, new_vehicle)

    def generate_pdf_gui(self):
        customer_name = simpledialog.askstring("Customer Name", "Enter customer name to generate PDF invoice:")
        pdf_filename = f"Invoice_{customer_name.replace(' ', '_')}.pdf"
        generate_pdf(self.file_path, customer_name)

        # Open the generated PDF file
        try:
            subprocess.run(["open", pdf_filename], check=True)  # For macOS
        except subprocess.CalledProcessError:
            try:
                subprocess.run(["xdg-open", pdf_filename], check=True)  # For Linux
            except subprocess.CalledProcessError:
                try:
                    subprocess.run(["start", "", pdf_filename], check=True, shell=True)  # For Windows
                except subprocess.CalledProcessError:
                    messagebox.showwarning("Info", "Could not open the PDF file. Please open it manually.")

    def check_customer_gui(self):
        customer_name = simpledialog.askstring("Customer Name", "Enter customer name to check information:")
        check_customer(self.file_path, customer_name)

    def add_notes_gui(self):
        customer_name = simpledialog.askstring("Customer Name", "Enter customer name to add notes:")
        notes = simpledialog.askstring("Notes", "Enter notes:")
        update_invoice(self.file_path, customer_name, new_notes=notes)

# Create and run the GUI
root = tk.Tk()
app = InvoiceApp(root)
root.mainloop()


