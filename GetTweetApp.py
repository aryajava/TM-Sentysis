#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
# import tkinter as tk
from tkinter import *
from tkinter import ttk, scrolledtext
from tkinter.messagebox import *
import pandas as pd
import snscrape.modules.twitter as sntw
from tqdm import tqdm # see progress bar of iteration
from datetime import datetime

class TwitterCrawlerApp(Tk):
    def __init__(self):
        # UI
        super().__init__()
        self.title('Mengambil Tweet Twitter')
        
        # path
        self.current_path = os.path.abspath(os.getcwd())
        
        # icon
        # self.iconbitmap(current_path + '/gui/icon.ico')
        
        # frame
        self.resizable(False, False)
        window_height = 500
        window_width = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        self.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        box_width = window_width - ((window_width * 90) / 100)
        btn_width = box_width / 2
        box_length = window_width - (box_width / 2)
        # convert float to int
        box_width= int(box_width)
        btn_width= int(btn_width)
        box_length = int(box_length)
        
        # default since dan util
        text1 = StringVar()
        text2 = StringVar()
        val = IntVar()
        val.set(0)
        text1.set("2022-09-03")
        text2.set("2022-09-04")

        # membuat widget
        self.label_query = Label(self, text='Cari:')
        self.entry_query = Entry(self, width=box_width, justify='center')
        self.label_limit = Label(self, text='Batas (0 = No limit)')
        self.entry_limit = Entry(self, textvariable = val, width=box_width, justify='center')
        self.label_since = Label(self, text='Sejak (YYYY-MM-DD)')
        self.entry_since = Entry(self, textvariable = text1, width=box_width, justify='center')
        self.label_until = Label(self, text='Sampai (YYYY-MM-DD)')
        self.entry_until = Entry(self, textvariable = text2, width=box_width, justify='center')
        self.button_crawl = Button(self, text='Mulai', command=self.start_crawling, width=btn_width, justify='center')
        self.button_export = Button(self, text='Export ke CSV', command=self.export_to_csv, width=btn_width, justify='center', state='disabled')
        self.progress = ttk.Progressbar(self, orient='horizontal', length=box_length, mode='determinate', maximum=100 )
        self.text_tweets = scrolledtext.ScrolledText(self, wrap = WORD)
    
        # menampilkan widget
        self.label_query.pack(pady=(10, 0))
        self.entry_query.pack()
        self.label_limit.pack(pady=(10, 0))
        self.entry_limit.pack()
        self.label_since.pack(pady=(10, 0))
        self.entry_since.pack()
        self.label_until.pack(pady=(10, 0))
        self.entry_until.pack()
        self.button_crawl.pack(pady=(10, 0))
        self.button_export.pack(pady=(10, 0))
        self.progress.pack(pady=(10, 0))
        self.text_tweets.pack(padx=10, pady=10, anchor=S, expand=True)
        
        
    def export_to_csv(self):
        try:
            # ambil variabel instance dataframe
            df = self.df
            
            # mengecek apakah folder 'export' sudah tersedia
            if not os.path.exists('export'):
                os.makedirs('export')
                
            # mendapatkan tanggal saat ini dalam format DD-MM-YYYY
            now = datetime.now()
            date = now.strftime('%d-%m-%Y')
            
            # namafile
            name_query = str(self.entry_query.get())
            name_query = name_query.replace(' ', '-')
            name_file = f'raw_tweet_{name_query}_{date}.csv'
            
            # menyimpan dataframe ke file CSV
            df.to_csv(self.current_path + f'/export/{name_file}', index=False, encoding='utf_8', sep=',')
            
            
            # info
            showinfo(title='Pesan',message='Export ke CSV Berhasil Disimpan!\nNama File: '+str(name_file))
        except Exception as e:
            # info error
            print(e)
            showerror(title='Pesan',message='Error: '+e)

    def start_crawling(self):
        # membaca input dari form
        query = str(self.entry_query.get())
        limit = self.entry_limit.get()
        since = str(self.entry_since.get())
        until = str(self.entry_until.get())
        
        # cek input
        if not query:
            showwarning(title='Pesan',message='Input Cari Kosong!')
            return
        if not limit:
            showwarning(title='Pesan',message='Input Batas Kosong!')
            return
        else:
            try:
                limit = int(limit)
            except ValueError:
                showwarning(title='Pesan',message='Input Batas Bukan Angka!')
                return
        if not since:
            showwarning(title='Pesan',message='Input Sejak Kosong!')
            return
        if not until:
            showwarning(title='Pesan',message='Input Sampai Kosong!')
            return
    
        # mengambil tweet dari Twitter
        cari = f"({query}) lang:id since:{since} until:{until}"
        tweets = []
        print('Kueri Cari:', cari)
        print('Batas Tweets:', limit)

        # menampilkan tweet di widget teks
        self.text_tweets.delete('1.0', END)
        
        # menampilkan progress bar saat crawling tweet
        i = 0
        self.progress.config(value=i)
        
        try:
            # disable widget ketika selesai proses
            self.entry_query.config(state='disable')
            self.entry_limit.config(state='disable')
            self.entry_since.config(state='disable')
            self.entry_until.config(state='disable')
            self.button_crawl.config(state='disable')
            self.button_export.config(state='disable')
            
            # progress bar
            self.progress.config(maximum=100)
            
            for tweet in tqdm(sntw.TwitterSearchScraper(query=cari).get_items()):
                # cek limit adakah ada value
                if limit > 0:
                    # progress bar
                    self.progress.config(maximum=limit)
                    
                    if len(tweets) == limit:
                        break
                    else:
                        tweets.append([tweet.user.username, tweet.content])
                        self.text_tweets.insert(END, f'{tweet.user.username} ({tweet.date}): {tweet.content}\n\n')
                        
                        # update value progress bar
                        i += 1
                        self.progress.config(value=i)
                else:
                    # update value progress bar
                    self.progress.step(99)
                    
                    tweets.append([tweet.user.username, tweet.content])
                    self.text_tweets.insert(END, f'{tweet.user.username} ({tweet.date}): {tweet.content}\n\n')
                
                # update
                self.update()
                
            # mengubah tweet menjadi dataframe pandas
            df = pd.DataFrame(tweets, columns=['username','text'])
            
            # stop progress bar
            self.progress.stop()
            
            # info
            showinfo(title='Pesan',message='Tweets yang berhasil didapatkan: '+str(len(tweets)))
            
            # enable widget ketika selesai proses
            self.entry_query.config(state='normal')
            self.entry_limit.config(state='normal')
            self.entry_since.config(state='normal')
            self.entry_until.config(state='normal')
            self.button_crawl.config(state='normal')
            self.button_export.config(state='normal')
            
        except Exception as e:
            # info error
            print(e)
            showerror(title='Pesan',message='Error: '+e)
        
        # menyimpan dataframe ke dalam variabel instance
        self.df = df

# membuat objek aplikasi
app = TwitterCrawlerApp()

# menjalankan aplikasi
app.mainloop()


# In[ ]:




