import customtkinter as ctk
from tabs.log_finder import LogFinder

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PWLRX automation tool")
        self.geometry("900x700")
        self._build_ui()

    def _build_ui(self):
        tabview = ctk.CTkTabview(self, width=1000, height=750)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)

        tabview.add("log finder")
        log_finder_tab = LogFinder(tabview.tab("log finder"))
        log_finder_tab.pack(fill="both", expand=True)

        tabview.add("Tab 2")
        tabview.add("Tab 3")




if __name__ == "__main__":
    app = App()
    app.mainloop()