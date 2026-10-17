import tkinter as tk


class Tooltip:
    """Exibe uma label flutuante ao repousar o mouse sobre um widget."""

    def __init__(self, widget, texto, delay_ms=600):
        self.widget = widget
        self.texto = texto
        self.delay_ms = delay_ms
        self._tip = None
        self._job = None

        widget.bind("<Enter>", self._agendar, add="+")
        widget.bind("<Leave>", self._cancelar_e_esconder, add="+")
        widget.bind("<Button-1>", self._cancelar_e_esconder, add="+")

    def _agendar(self, _event=None):
        self._cancelar_e_esconder()
        self._job = self.widget.after(self.delay_ms, self._mostrar)

    def _cancelar_e_esconder(self, _event=None):
        if self._job is not None:
            try:
                self.widget.after_cancel(self._job)
            except Exception:
                pass
            self._job = None

        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None

    def _mostrar(self):
        self._job = None
        if self._tip is not None:
            return

        try:
            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        except Exception:
            return

        tip = tk.Toplevel(self.widget)
        tip.wm_overrideredirect(True)
        try:
            tip.attributes("-topmost", True)
        except Exception:
            pass
        tip.geometry(f"+{x}+{y}")

        tk.Label(
            tip,
            text=self.texto,
            bg="#2b2b2b",
            fg="#e5e5e5",
            font=("Roboto", 10),
            padx=8,
            pady=4,
            highlightbackground="#4a4a4a",
            highlightthickness=1,
        ).pack()

        self._tip = tip
