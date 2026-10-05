"""Diálogos modais usados pela integração de exportação/importação na GUI."""
import customtkinter as ctk


class _DialogoBase(ctk.CTkToplevel):
    """Base para diálogos modais centralizados (mesmo padrão do FormularioRegistro)."""

    def __init__(self, master, titulo, largura, altura):
        super().__init__(master)
        self.title(titulo)
        self.geometry(f"{largura}x{altura}")
        self.configure(fg_color=("#ebebeb", "#2b2b2b"))
        self.resultado = None

        self._construir()

        self.update_idletasks()
        self.after(100, self._tornar_modal)
        self._centralizar(master)

    def _construir(self):
        raise NotImplementedError

    def _tornar_modal(self):
        try:
            self.transient(self.master)
            self.lift()
            self.focus_force()
            self.grab_set()
        except Exception:
            pass

    def _centralizar(self, master):
        try:
            self.update_idletasks()
            mx, my = master.winfo_x(), master.winfo_y()
            mw, mh = master.winfo_width(), master.winfo_height()
            w, h = self.winfo_width(), self.winfo_height()
            self.geometry(f"+{mx + (mw - w) // 2}+{my + (mh - h) // 2}")
        except Exception:
            pass


class DialogoSenhaPDF(_DialogoBase):
    """Pede a senha de abertura do PDF (vazio = sem cifra). None = cancelado."""

    def __init__(self, master):
        super().__init__(master, "Senha de abertura do PDF", 460, 240)

    def _construir(self):
        ctk.CTkLabel(
            self, text="🔒 Senha de abertura do PDF",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 4))

        ctk.CTkLabel(
            self, text="Deixe em branco para gerar SEM cifra.",
            text_color="gray", font=ctk.CTkFont(size=12),
        ).pack(pady=(0, 10))

        box = ctk.CTkFrame(self, fg_color="transparent")
        box.pack(fill="x", padx=30)
        self.entrada = ctk.CTkEntry(box, height=38, show="•")
        self.entrada.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.entrada.bind("<Return>", lambda e: self._ok())
        self.btn_olho = ctk.CTkButton(box, text="👁️", width=42, command=self._toggle)
        self.btn_olho.pack(side="left")

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.pack(pady=20)
        ctk.CTkButton(
            botoes, text="Cancelar", width=120, fg_color="gray", command=self._cancelar
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            botoes, text="Continuar", width=140,
            font=ctk.CTkFont(weight="bold"), command=self._ok,
        ).pack(side="left", padx=8)

        self.bind("<Escape>", lambda e: self._cancelar())
        self.entrada.focus()

    def _toggle(self):
        atual = self.entrada.cget("show")
        self.entrada.configure(show="" if atual else "•")
        self.btn_olho.configure(text="🙈" if atual else "👁️")

    def _ok(self):
        self.resultado = self.entrada.get()
        self.destroy()

    def _cancelar(self):
        self.resultado = None
        self.destroy()


class DialogoResumoImportacao(_DialogoBase):
    """Mostra o resumo do lote e confirma a importação. resultado = True/False."""

    def __init__(self, master, caminho_json, resumo):
        self.caminho_json = caminho_json
        self.resumo = resumo
        super().__init__(master, "Confirmar importação", 520, 340)

    def _construir(self):
        ctk.CTkLabel(
            self, text="⬇️ Confirmar importação",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(18, 6))

        ctk.CTkLabel(
            self, text=self.caminho_json, text_color="gray",
            font=ctk.CTkFont(size=11), wraplength=460,
        ).pack(pady=(0, 10))

        texto = (
            f"{'Itens lidos: ' + str(self.resumo.total_lidos):>0}\n\n"
            f"  ✓ A importar ........: {len(self.resumo.importaveis)}\n"
            f"  ↷ Pulados (existente): {len(self.resumo.duplicados)}\n"
            f"  ↷ Pulados (repetido) : {len(self.resumo.repetidos)}\n"
            f"  ✗ Inválidos ..........: {len(self.resumo.invalidos)}"
        )
        ctk.CTkLabel(
            self, text=texto, justify="left", font=ctk.CTkFont(size=13),
        ).pack(pady=6)

        ctk.CTkLabel(
            self, text="Um backup do cofre será criado antes de gravar.",
            text_color="gray", font=ctk.CTkFont(size=11),
        ).pack(pady=(4, 0))

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.pack(pady=18)
        ctk.CTkButton(
            botoes, text="Cancelar", width=120, fg_color="gray", command=self._cancelar
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            botoes, text="Importar", width=140, fg_color="#16a085",
            font=ctk.CTkFont(weight="bold"), command=self._confirmar,
        ).pack(side="left", padx=8)

        self.bind("<Escape>", lambda e: self._cancelar())

    def _confirmar(self):
        self.resultado = True
        self.destroy()

    def _cancelar(self):
        self.resultado = False
        self.destroy()


class DialogoRelatorio(_DialogoBase):
    """Mostra o relatório final de uma operação (somente leitura)."""

    def __init__(self, master, titulo, linhas):
        self.linhas = linhas
        super().__init__(master, titulo, 560, 400)

    def _construir(self):
        ctk.CTkLabel(
            self, text=self.title(), font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(16, 8))

        caixa = ctk.CTkTextbox(self, font=ctk.CTkFont(size=12), wrap="word")
        caixa.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        caixa.insert("1.0", "\n".join(self.linhas))

        ctk.CTkButton(
            self, text="Fechar", width=140, command=self.destroy,
        ).pack(pady=(0, 16))

        self.bind("<Escape>", lambda e: self.destroy())


class DialogoProgresso(ctk.CTkToplevel):
    """Indicador indeterminado enquanto uma operação roda em segundo plano."""

    def __init__(self, master, texto="Processando..."):
        super().__init__(master)
        self.title("Aguarde")
        self.geometry("380x130")
        self.resizable(False, False)
        self.configure(fg_color=("#ebebeb", "#2b2b2b"))
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        ctk.CTkLabel(
            self, text=texto, font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(28, 14))

        self.barra = ctk.CTkProgressBar(self, mode="indeterminate", width=300)
        self.barra.pack(pady=4)
        self.barra.start()

        self.update_idletasks()
        self._centralizar(master)
        self.after(100, self._modal)

    def _modal(self):
        try:
            self.transient(self.master)
            self.lift()
            self.focus_force()
            self.grab_set()
        except Exception:
            pass

    def _centralizar(self, master):
        try:
            mx, my = master.winfo_x(), master.winfo_y()
            mw, mh = master.winfo_width(), master.winfo_height()
            w, h = self.winfo_width(), self.winfo_height()
            self.geometry(f"+{mx + (mw - w) // 2}+{my + (mh - h) // 2}")
        except Exception:
            pass

    def fechar(self):
        try:
            self.barra.stop()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
