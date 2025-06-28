import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from PyPDF2 import PdfReader

def is_pdf_ocrd(filepath):
    """
    Checks if a PDF file contains any extractable (searchable) text.
    Returns True if at least one page has text, indicating the PDF is OCR'd.
    """
    try:
        reader = PdfReader(filepath)  # Open the PDF file
        for page in reader.pages:     # Iterate through each page
            text = page.extract_text()
            if text and text.strip(): # Check if there is any non-empty text
                return True           # Found searchable text, likely OCR'd
        return False                  # No searchable text found
    except Exception:
        # If there's an error reading the PDF, assume it's not OCR'd
        return False

def rename_ocr_pdfs(subdirectory, recursive, output_widget=None):
    """
    Scans the subdirectory for PDF files.
    If recursive is True, scans all subdirectories recursively.
    If a PDF is OCR'd and not already renamed, appends '_OCR' to its filename.
    Optionally outputs the result to a Tkinter text widget.
    """
    renamed_files = []  # List to keep track of renamed files for reporting

    if recursive:
        # Walk through all directories and files recursively
        for root, _, files in os.walk(subdirectory):
            for filename in files:
                if filename.lower().endswith('.pdf'):
                    full_path = os.path.join(root, filename)
                    name, ext = os.path.splitext(filename)
                    if '_OCR' not in name and is_pdf_ocrd(full_path):
                        new_name = f"{name}_OCR{ext}"
                        new_path = os.path.join(root, new_name)
                        os.rename(full_path, new_path)
                        renamed_files.append(f"{filename} -> {new_name}")
    else:
        # Only scan the specified directory, not subdirectories
        for filename in os.listdir(subdirectory):
            if filename.lower().endswith('.pdf'):
                full_path = os.path.join(subdirectory, filename)
                name, ext = os.path.splitext(filename)
                if '_OCR' not in name and is_pdf_ocrd(full_path):
                    new_name = f"{name}_OCR{ext}"
                    new_path = os.path.join(subdirectory, new_name)
                    os.rename(full_path, new_path)
                    renamed_files.append(f"{filename} -> {new_name}")

    # Output results to the GUI if a widget is provided
    if output_widget is not None:
        output_widget.delete(1.0, tk.END)  # Clear previous output
        if renamed_files:
            output_widget.insert(tk.END, "Renamed files:\n" + "\n".join(renamed_files))
        else:
            output_widget.insert(tk.END, "No OCR'd PDFs found to rename.")

def select_directory():
    """
    Opens a folder picker dialog for the user to select a directory.
    Asks if the user wants to run recursively via a checkbox.
    Shows a confirmation message before renaming.
    Calls the rename function and displays the results in the GUI.
    """
    folder_selected = filedialog.askdirectory()  # Show folder picker dialog
    if folder_selected:
        # Get the state of the recursive checkbox
        recursive = recursive_var.get()

        # Show confirmation message before running the operation
        confirm_message = (
            "All PDFs that have been OCR'd will have their file name updated with '_OCR'.\n"
            f"Run recursively: {'Yes' if recursive else 'No'}\n"
            "Do you want to continue?"
        )
        if not messagebox.askyesno("Confirm Rename", confirm_message):
            return  # User cancelled

        # Clear previous output and show scanning message
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, f"Scanning: {folder_selected}\n")
        root.update()  # Update GUI to show message immediately

        # Start the renaming process
        rename_ocr_pdfs(folder_selected, recursive, output_text)

# --- GUI Setup ---

root = tk.Tk()
root.title("OCR PDF Renamer")  # Set window title

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# Checkbox for recursive option
recursive_var = tk.BooleanVar(value=False)
recursive_checkbox = tk.Checkbutton(
    frame, text="Run recursively", variable=recursive_var
)
recursive_checkbox.pack(pady=5)

# Button to select folder and start process
pick_button = tk.Button(
    frame, 
    text="Select Folder and Rename OCR PDFs", 
    command=select_directory
)
pick_button.pack(pady=5)

# Scrolled text widget to display output/results
output_text = scrolledtext.ScrolledText(frame, width=60, height=15)
output_text.pack(pady=5)

root.mainloop()
