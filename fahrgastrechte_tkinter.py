import tkinter as tk
from tkinter import ttk
import functions

# based on https://stackoverflow.com/a/47985165
class Scrollable(ttk.Frame):
    def __init__(self, frame):
        self.parent = frame
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        scrollbar_x = tk.Scrollbar(frame, orient='horizontal')
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        self.canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_x.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)
        scrollbar_x.config(command=self.canvas.xview)
        self.canvas.bind('<Configure>', self.__fill_canvas)

        # Make window scrollable by mouse wheel
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Scroll in X direction with Shift+Scroll
        self.canvas.bind_all("<Shift-Button-4>", self._on_x_mousewheel)
        self.canvas.bind_all("<Shift-Button-5>", self._on_x_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_x_mousewheel)

        # base class initialization
        ttk.Frame.__init__(self, frame)

        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0,0, window=self, anchor=tk.NW)

    def __fill_canvas(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width=canvas_width)

    def update(self):
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))

    def _on_mousewheel(self, event):
        direction = 1 if event.num == 5 else -1
        self.canvas.yview_scroll(direction, "units")

    def _on_x_mousewheel(self, event):
        direction = 1 if event.num == 5 else -1
        self.canvas.xview_scroll(direction, "units")


class Application(ttk.Frame):
    def __init__(self, master, args, defaults):
        super().__init__(master)
        self.create_widgets(master, args, defaults)

    def create_widgets(self, master, args, defaults):
        self.form_fields = {}
        fields, fieldnames = functions.get_form_fields(**vars(args))
        row = 0
        for n in sorted(fieldnames, key=functions.db_fieldname_sort):
            title = ""
            if 'FieldNameAlt' in fields[n]:
                title = fields[n]['FieldNameAlt']

            if n in defaults:
                value = defaults[n]
            else:
                value = None

            if title:
                ttk.Label(master, text=title).grid(row=row)

            if 'FieldStateOption' in fields[n]:
                if value is not None:
                    i = fields[n]['FieldStateOption'].index(value)
                else:
                    i = fields[n]['FieldStateOption'].index('Off')

                self.form_fields[n] = tk.StringVar(master)
                self.form_fields[n].set(fields[n]['FieldStateOption'][i])

                if set(fields[n]['FieldStateOption']) == set(["Ja", "Off"]):
                    w = tk.Checkbutton(master, variable=self.form_fields[n], onvalue="Ja", offvalue="Off")
                else:
                    w = tk.OptionMenu(master, self.form_fields[n], *fields[n]['FieldStateOption'])
                w.grid(row=row, column=1)
            else:
                self.form_fields[n] = tk.StringVar(master)
                if value is not None:
                    self.form_fields[n].set(value)
                e = tk.Entry(master, textvariable=self.form_fields[n])
                e.grid(row=row, column=1)
            row += 1

        self.quit = ttk.Button(master, text="Generate Form",
                              command=root.destroy)
        self.quit.grid(row=row, column=1)


if __name__ == '__main__':
    args, defaults = functions.get_args()
    root = tk.Tk()
    frame = Scrollable(frame=root)
    app = Application(frame, args, defaults)
    frame.update()
    app.mainloop()
    form_values = [(n, v.get()) for n, v in app.form_fields.items()]
    print(functions.generate_form(form_values, **vars(args)))
