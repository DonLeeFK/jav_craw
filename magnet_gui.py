import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import logging
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import time

start_time = float
#keep only the 3 most recent log including the current one
log_files = [f for f in os.listdir('./log') if f.endswith('.log')]
log_files.sort(key=lambda x: os.path.getmtime(os.path.join('./log', x)))
if len(log_files) > 4:
    for file in log_files[:-4]:
        os.remove(os.path.join('./log', file))
import time
logging.basicConfig(filename=f'./log/magnet_{time.strftime("%Y%m%d-%H%M%S")}.log', level=logging.WARNING)

def fetchMagnet0Mag(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    #link = soup.find('a')['href']
    table = soup.find('div',{'class':'container'})\
        .find('table').find('tbody').find_all('tr')
    links = []
    
    for tr in table:
        try:
            link = 'https://0mag.net'+tr.find('a')['href']
            links.append(link)
        except:
            continue
    mags = []
    #limit the number of magnet links to 3
    links = links[:3]
    if links:
        for link in links:
            response = requests.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')
            mag = soup.find('input', {'id': 'input-magnet'})['value']
            mags.append(mag)
    mags = '\n'.join(mags)
    #print(mags)
    return mags
    


#takes only file without '_verbose'
csv_files = [f for f in os.listdir('./data') if f.endswith('.csv') \
             and '_verbose' not in f]

file_var = None
def select_file():
    global file_var
    selected_file = filedialog.askopenfilename(initialdir="./data", title="Select a file", filetypes=(("CSV files", "*.csv"),))
    if selected_file and '_verbose' not in selected_file:
        file_var = selected_file
        return selected_file
    else:
        messagebox.showerror("Error", "No file selected.")
        return None

def process_file(progress_bar):
    selected_file = file_var
    if selected_file:
        global start_time
        start_time = time.time() # Define start_time here
        try:
            df = pd.read_csv(selected_file)
            df['magnet'] = pd.Series(dtype='object')
            df['magnet'].fillna(value='', inplace=True)

            from tqdm import tqdm

            for bango in tqdm(df['bango']):
                url = f"https://0mag.net/search?q={bango}"
                try:
                    response = requests.get(url)
                    mags_0mag = fetchMagnet0Mag(response)
                    df.loc[df['bango'] == bango, 'magnet'] = mags_0mag
                except requests.exceptions.ConnectionError:
                    logging.warning(f"Couldn't connect to {url}")
                    continue
                progress_bar.step(100/len(df['bango']))
                progress_bar.update()
            if '_magnet' not in selected_file:
                df.to_csv(f'{selected_file[:-4]}_magnet.csv', index=False)
            else:
                df.to_csv(f'{selected_file}', index=False)
            messagebox.showinfo("Success", "File processed successfully.")
        except pd.errors.EmptyDataError:
            messagebox.showerror("Error", "Selected file is empty.")
        except pd.errors.ParserError:
            messagebox.showerror("Error", "Selected file is not a valid CSV file.")
    else:
        messagebox.showerror("Error", "No file selected.")
        
def update_progress_labels(progress_bar, progress_percent_label, progress_eta_label):
    global start_time
    progress_percent = progress_bar["value"] / progress_bar["maximum"] * 100
    progress_percent_label.config(text=f"{progress_percent:.2f}%")
    if progress_percent > 0:
        elapsed_time = time.time() - start_time
        eta = elapsed_time / progress_percent * 100 - elapsed_time
        progress_eta_label.config(text=f"ETA: {eta:.2f}s")
    else:
        progress_eta_label.config(text="")
        progress_bar.update()


def gui():
    root = tk.Tk()
    root.title("Magnet Link Extractor")
    root.geometry("400x200")

    file_var = tk.StringVar()

    select_file_button = tk.Button(root, text="Select File", command=lambda: file_var.set(select_file()))
    select_file_button.pack(pady=10)

    progress_bar_frame = tk.Frame(root)
    progress_bar_frame.pack(pady=10)

    progress_bar_label = tk.Label(progress_bar_frame, text="Progress:")
    progress_bar_label.pack(side=tk.LEFT)

    progress_bar = tk.ttk.Progressbar(progress_bar_frame, orient="horizontal", length=200, mode="determinate")
    progress_bar.pack(side=tk.LEFT)

    
    


    start_time = time.time()
    process_file_button = tk.Button(root, text="Fetch Magnet", command=lambda: [process_file(progress_bar), progress_bar.start()])
    process_file_button.pack(pady=10)

    root.mainloop()


    


if __name__ == '__main__':
    gui()
