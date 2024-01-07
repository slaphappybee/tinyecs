from ._component import Component, ComponentRegistry
from ._system import System
import tkinter as tk
from dataclasses import dataclass


@dataclass
class TkWindow(Component):
    window: tk.Tk


def create_inspector() -> TkWindow:
    window = tk.Tk()
    title = tk.Label(text="Inspector")
    title.pack()
    frame = tk.Frame(borderwidth=1)
    frame.pack()
    label1 = tk.Label(master=frame, text="Entity circle")
    label1.pack()
    cframe = tk.Frame(borderwidth=1, master=frame)
    cframe.pack()
    label2 = tk.Label(master=cframe, text="Position2D")
    label2.pack()
    x = tk.Entry(master=cframe)
    x.pack()
    y = tk.Entry(master=cframe)
    y.pack()

    return TkWindow(window)



class TkEventQueueSystem(System):
    def onFrame(self, cr: ComponentRegistry, dt: float) -> None:
        for window in cr.query_single(TkWindow):
            window.window.update_idletasks()
            window.window.update()
