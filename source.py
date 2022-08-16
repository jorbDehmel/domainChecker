import tkinter as tk
from tkinter import filedialog as fd
from tkinter.ttk import Progressbar

import requests as r
import requests.exceptions

from regex import split

"""
Todo:
-Make checkboxes go in 9 collumns, wrap to next row (use .grid())
"""

class Checkbox:
    def __init__(self, root, text, coords):
        self.text = text
        self.state = tk.IntVar()
        temp = tk.Checkbutton(root, text=self.text, variable=self.state)
        temp.grid(column=coords[0], row=coords[1])
        return

    def __call__(self):
        if self.state.get() == 1:
            return self.text
        else:
            return ''

def to_time(queries, q_time):
    seconds = queries * q_time

    minutes = seconds // 60
    seconds %= 60

    hours = minutes // 60
    minutes %= 60

    out = 'About '
    if hours != 0:
        out += str(hours) + 'h '
    if minutes != 0:
        out += str(minutes) + 'm '
    if seconds != 0:
        out += str(seconds) + 's'
    out += ' total'

    return out


class Window:
    def __init__(self, sites_inp):
        CHECKBOX_COLS = 7
        self.output, self.links, self.words, self.csv = {}, [], [], ''

        self.root = tk.Tk()
        self.root.title('Domain availability test')

        # Main label
        self.label = tk.Label(self.root, text='Domain availability tester')
        self.label.grid(column=0, row=0, columnspan=CHECKBOX_COLS)

        # Instructions label
        tk.Label(self.root,
                 text='Enter comma-seperated words in the box below,\nthen check the domains to check')\
                    .grid(column=0, row=1, columnspan=CHECKBOX_COLS)

        # Main text box
        self.text_box = tk.Text(self.root, height=10)
        self.text_box.grid(column=0, row=2, columnspan=CHECKBOX_COLS)

        # Domain checkboxes
        # row 3
        self.links = []
        for i, site in enumerate(sites_inp):
            coords = (i % CHECKBOX_COLS, 3 + (i // CHECKBOX_COLS))
            temp = Checkbox(self.root, site, coords)
            self.links.append(temp)

        # Check for availability button
        tk.Button(self.root, text='Check for availability', command=self.run)\
            .grid(column=0, row=4 + (len(sites_inp) // 5), columnspan=CHECKBOX_COLS)

        # Dev info label
        tk.Label(self.root, text='2022, jdehmel@outlook.com')\
            .grid(column=0, row=5 + (len(sites_inp) // 5), columnspan=CHECKBOX_COLS)

        self.root.mainloop()
        return

    def run(self):
        TIMEOUT = 1

        links = [i() for i in self.links]
        while '' in links:
            links.remove('')
        print(links)

        text = self.text_box.get('1.0', tk.END)
        self.words = split(r'[, ]+', text)

        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text='Performing queries...').grid(column=0, row=0)
        tk.Label(self.root, text=to_time((len(self.words) * len(links)), TIMEOUT)).grid(column=0, row=1)
        current = tk.Label(self.root, text='')
        current.grid(column=0, row=2)

        p = Progressbar(self.root, orient=tk.HORIZONTAL, length=200, mode="determinate", takefocus=True, maximum=100)
        p.grid(column=0, row=3)
        step_size = 100 / (len(self.words) * len(links))

        tk.Button(self.root, text='Quit', command=self.root.destroy).grid(column=0, row=4)

        for word in self.words:
            word = word.strip()
            self.output[word] = ''
            for site in links:
                if site[0] == '.':
                    search = 'http://www.' + word + site
                elif site[-1] == '/':
                    search = 'http://www.' + site + word
                else:
                    search = 'http://www.' + site + '.com/' + word
                current.configure(text=search)
                try:
                    if r.get(search, timeout=TIMEOUT).status_code != 200:
                        self.output[word] += ' ' + site

                except requests.exceptions.ConnectionError:
                    self.output[word] += ' ' + site

                except requests.exceptions.ReadTimeout:
                    print('Timeout')

                p['value'] += step_size
                self.root.update()

        # Write to csv
        self.csv = 'Keyword,Availability\n'
        for key in self.output:
            line = self.output[key]
            if line == '':
                line = 'NONE'
            self.csv += key + ',' + line + '\n'

        # To output screen
        self.end()
        return

    def end(self):
        # Clear window
        for w in self.root.winfo_children():
            w.destroy()

        # Table of output
        scrollbar = tk.Scrollbar(self.root)
        mylist = tk.Listbox(self.root, yscrollcommand=scrollbar.set, height=5, width=24)
        for line in self.csv.split('\n'):
            mylist.insert(tk.END, line)
        mylist.grid(column=0, row=0)

        # Save as CSV file button
        tk.Button(self.root, text='Save as', command=self.save_as).grid(column=0, row=1)

        # Quit button
        tk.Button(self.root, text='Quit', command=self.root.destroy).grid(column=0, row=2)

        return

    def save_as(self):
        with fd.asksaveasfile('w') as file:
            file.write(self.csv)
        return
