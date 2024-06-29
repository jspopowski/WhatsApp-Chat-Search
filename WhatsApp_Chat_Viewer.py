import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime
import os
from PIL import Image, ImageTk
import time
import re

class WhatsAppChatViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("Visualiseur de Chat WhatsApp")
        self.master.geometry("800x600")
        self.master.configure(bg='#6fa0ac')  # Set background color to RGB(111,160,172)

        self.chat_content = []
        self.media_folder = ""

        self.create_widgets()

    def create_widgets(self):
        # Create GUI elements (buttons, entry fields, listbox, etc.)
        self.load_button = tk.Button(self.master, text="Charger le Chat", command=self.load_chat, bg='#6fa0ac')
        self.load_button.pack(pady=10)

        self.search_frame = ttk.Frame(self.master)
        self.search_frame.pack(fill="x", padx=10, pady=5)

        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side="left", expand=True, fill="x")

        self.search_button = tk.Button(self.search_frame, text="Rechercher", command=self.search_chat, bg='#6fa0ac')
        self.search_button.pack(side="left")

        self.date_entry = tk.Entry(self.search_frame)
        self.date_entry.pack(side="left")
        self.date_entry.insert(0, "JJ/MM/AAAA")

        self.date_search_button = tk.Button(self.search_frame, text="Rechercher Date", command=self.search_by_date, bg='#6fa0ac')
        self.date_search_button.pack(side="left")

        # Create a frame for the listbox and scrollbar
        self.results_frame = ttk.Frame(self.master)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.results_list = tk.Listbox(self.results_frame, width=70, height=20)
        self.results_list.pack(side="left", fill="both", expand=True)

        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.results_list.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.results_list.config(yscrollcommand=self.scrollbar.set)

        # Bind double-click event
        self.results_list.bind('<Double-1>', self.show_context)

        self.image_label = tk.Label(self.master, bg='#6fa0ac')
        self.image_label.pack()

    def load_chat(self):
        chat_file = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt")])
        if chat_file:
            self.media_folder = os.path.join(os.path.dirname(chat_file), "Media")
            with open(chat_file, "r", encoding="utf-8") as file:
                self.chat_content = file.readlines()
            messagebox.showinfo("Import Terminé", "Le chat a été importé avec succès!")

    def search_chat(self):
        query = self.search_entry.get().lower()
        self.results_list.delete(0, tk.END)
        for line in self.chat_content:
            if query in line.lower():
                self.results_list.insert(tk.END, line.strip())

    def search_by_date(self):
        date_str = self.date_entry.get()
        try:
            search_date = datetime.strptime(date_str, "%d/%m/%Y")
            
            # Create a progress bar window
            progress_window = tk.Toplevel(self.master)
            progress_window.title("Recherche en cours")
            progress_window.geometry("300x100")
            progress_window.configure(bg='#6fa0ac')

            progress_label = tk.Label(progress_window, text="Recherche des messages...", bg='#6fa0ac')
            progress_label.pack(pady=10)

            progress_bar = ttk.Progressbar(progress_window, length=200, mode='determinate')
            progress_bar.pack(pady=10)

            self.results_list.delete(0, tk.END)
            matching_lines = []

            # Prepare the search pattern
            search_pattern = search_date.strftime("%#m/%#d/%y")  # Remove leading zeros
            
            # Simulate progress
            for i in range(101):
                progress_bar['value'] = i
                progress_window.update()
                time.sleep(0.02)  # Adjust this value to make the progress slower or faster

                if i % 10 == 0:  # Check for matches every 10th iteration
                    for line in self.chat_content:
                        if line.startswith(search_pattern):
                            matching_lines.append(line.strip())

            # Close progress window
            progress_window.destroy()

            # Remove duplicates while preserving order
            seen = set()
            unique_matching_lines = []
            for line in matching_lines:
                if line not in seen:
                    seen.add(line)
                    unique_matching_lines.append(line)

            # Sort unique matching lines by time
            def extract_time(line):
                match = re.search(r'\d+/\d+/\d+, (\d+:\d+ [AP]M)', line)
                if match:
                    return datetime.strptime(match.group(1), "%I:%M %p")
                return datetime.min  # Return minimum datetime if no match found

            unique_matching_lines.sort(key=extract_time)

            # Display results
            for line in unique_matching_lines:
                self.results_list.insert(tk.END, line)

            # Show completion message
            messagebox.showinfo("Recherche Terminée", f"{len(unique_matching_lines)} messages trouvés pour la date {date_str}")

        except ValueError:
            messagebox.showerror("Erreur", "Format de date invalide. Utilisez JJ/MM/AAAA.")

    def show_context(self, event):
        selected_index = self.results_list.curselection()[0]
        selected_line = self.results_list.get(selected_index)

        # Find the index of the selected line in the full chat content
        full_index = self.chat_content.index(selected_line + '\n')

        # Get the context (10 messages before and after)
        start_index = max(0, full_index - 10)
        end_index = min(len(self.chat_content), full_index + 11)

        context_window = tk.Toplevel(self.master)
        context_window.title("Contexte du message")
        context_window.geometry("600x400")
        context_window.configure(bg='#6fa0ac')

        context_frame = ttk.Frame(context_window)
        context_frame.pack(fill="both", expand=True, padx=10, pady=10)

        context_list = tk.Listbox(context_frame, width=70, height=20)
        context_list.pack(side="left", fill="both", expand=True)

        context_scrollbar = ttk.Scrollbar(context_frame, orient="vertical", command=context_list.yview)
        context_scrollbar.pack(side="right", fill="y")
        context_list.config(yscrollcommand=context_scrollbar.set)

        for i, line in enumerate(self.chat_content[start_index:end_index]):
            context_list.insert(tk.END, line.strip())
            if i == (full_index - start_index):
                context_list.itemconfig(tk.END, {'bg':'yellow'})

    def show_media(self, event):
        selected_line = self.results_list.get(self.results_list.curselection())
        media_match = re.search(r'<attached: (.+)>', selected_line)
        if media_match and self.media_folder:
            media_file = os.path.join(self.media_folder, media_match.group(1))
            if os.path.exists(media_file):
                try:
                    image = Image.open(media_file)
                    image.thumbnail((300, 300))
                    photo = ImageTk.PhotoImage(image)
                    self.image_label.config(image=photo)
                    self.image_label.image = photo
                except:
                    self.image_label.config(image=None, text="Impossible d'afficher ce type de média")
        else:
            self.image_label.config(image=None, text="")

root = tk.Tk()
root.configure(bg='#6fa0ac')  # Set background color to RGB(111,160,172)
app = WhatsAppChatViewer(root)
root.mainloop()