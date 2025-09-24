# ...existing code...
import customtkinter as ctk

ctk.set_appearance_mode("dark")

root = ctk.CTk()
root.geometry("480x240")

# external margin: the widget size stays the same, space is added outside it
lbl_pad = ctk.CTkLabel(root, text="padx=40 (external margin)", width=120)
lbl_pad.pack(padx=40, pady=10)

# internal padding: the widget itself grows horizontally to add space around the text
lbl_ipad = ctk.CTkLabel(root, text="ipadx=40 (internal padding)", width=120)
lbl_ipad.pack(pady=10, ipadx=40)

print("pad pack_info:", lbl_pad.pack_info())
print("ipad pack_info:", lbl_ipad.pack_info())

root.mainloop()
# ...existing code...