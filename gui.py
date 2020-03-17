#!/usr/bin/env python3
from datetime import timedelta
from platform import system
import os
import threading
from subprocess import Popen, DEVNULL
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import N, E, S, W, END
from tkinter.messagebox import askyesno
import sys

import sparkmemes

class Config:
	def __init__(self, root):
		self.root = root
		self.root.title("SparkMemes GUI")

		tk.Grid.rowconfigure(self.root, 0, weight=1)
		tk.Grid.columnconfigure(self.root, 1, weight=1)

		self.duration = ttk.Scale(self.root, command=self.update_time, from_=2, to=250, orient="vertical")
		self.duration.grid(column=0, row=0, rowspan=2, sticky=N+S)

		self.prefix = "r/"
		self.subreddits = tk.Listbox(self.root, selectmode="multiple")
		self.subreddits.bind("<<ListboxSelect>>", self.update_subreddits)
		self.subreddits.grid(column=1, row=0, sticky=N+E+S+W)
		for x in [
			"insanepeoplefacebook", "mildlyinfuriating",
			"therewasanattempt", "woooosh",
			"dankmemes", "me_irl", "meirl", "memes", "wholesomememes",
			"MemeEconomy", "BikiniBottomTwitter"
		]:
			self.subreddits.insert(END, self.prefix+x)

		self.stats = ttk.Label(self.root, anchor="center")
		self.stats.grid(column=1, row=1, sticky=E+W)
		self.duration.set("10")

		self.create = ttk.Button(self.root, text="Create", command=self.create_video, state="disabled")
		self.create.grid(column=0, row=2, columnspan=2, sticky=S+E+W)

	def create_video(self):
		self.set_state(self.root)
		self.root.update()
		sub_list = [self.subreddits.get(x) for x in self.subreddits.curselection()]
		sub_list = [x[x.startswith(self.prefix) and len(self.prefix):] for x in sub_list]
		self.meme = threading.Thread(target=self.render_video, args=(sub_list, self.duration.get()))
		self.meme.daemon = True
		self.meme.start()

	# Thread this
	def render_video(self, sub_list, duration):
		posts, imgs = sparkmemes.download_submissions(sub_list, Limit=duration)
		sparkmemes.render(posts, imgs, True)
		if askyesno(title="Video made", message="Do you want to view it?"):
			self.open_file("video.mp4")
		self.root.destroy()

	def update_subreddits(self, event):
		if len(self.subreddits.curselection()) > 0:
			self.create.config(state="enabled")
		else:
			self.create.config(state="disabled")

	def update_time(self, count):
		count = round(float(count))
		if count < 2:
			self.duration.set("2")
			return
		if count > 250:
			self.duration.set("250")
			return
		self.stats.config(text="{} Memes ({})".format(count, timedelta(seconds=(count*10)+30)))

	def set_state(self, widget, state="disabled"):
		try:
			widget.configure(state=state)
		except tk.TclError:
			pass
		for child in widget.winfo_children():
			self.set_state(child, state=state)

	def open_file(self, filepath):
		if system() == "Darwin": # macOS
			Popen(("open", filepath), start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)
		elif system() == "Windows": # Windows
			os.startfile(filepath)
		elif system() == "Linux": # Linux
			Popen(("xdg-open", filepath), start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)


if __name__ == "__main__":
	root = tk.Tk()
	config = Config(root)
	root.update()
	root.minsize(root.winfo_width(), root.winfo_height())
	root.mainloop()
	print("Goodbye...")
