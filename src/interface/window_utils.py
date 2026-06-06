def bring_to_front(window, master):
    window.transient(master)
    window.lift()
    window.attributes("-topmost", True)
    window.after(200, lambda: window.attributes("-topmost", False))
    window.focus_force()
