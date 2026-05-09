import customtkinter as ctk
from tkinter import messagebox
from dados.armazenamento import novo_registro, atualizar_registro
from utils.helpers import gerar_senha_aleatoria, forca_senha


class FormularioRegistro(ctk.CTkToplevel):
    def __init__(self, master, callback, registro=None):
        super().__init__(master)
        self.callback = callback
        self.registro = registro

        self.title("Editar Registro" if registro else "Novo Registro")
        self.geometry("500x650")
        self.configure(fg_color=("#ebebeb", "#2b2b2b"))  # força cor de fundo

        # Constrói a UI ANTES de chamar grab_set / transient
        self._construir()

        if registro:
            self._preencher(registro)

        # Garante que a janela apareça e só DEPOIS aplica modal
        self.update_idletasks()
        self.after(100, self._tornar_modal)

        # Centraliza em relação ao master
        self._centralizar(master)

    def _tornar_modal(self):
        """Aplica transient + grab_set após a janela estar renderizada."""
        try:
            self.transient(self.master)
            self.lift()
            self.focus_force()
            self.grab_set()
        except Exception:
            pass

    def _centralizar(self, master):
        self.update_idletasks()
        try:
            mx = master.winfo_x()
            my = master.winfo_y()
            mw = master.winfo_width()
            mh = master.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = mx + (mw - w) // 2
            y = my + (mh - h) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _construir(self):
        ctk.CTkLabel(
            self,
            text="📝 " + ("Editar Registro" if self.registro else "Novo Registro"),
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=15)

        frame = ctk.CTkScrollableFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.entries = {}
        campos = [
            ("nome", "🏷️ Nome / Identificação *"),
            ("login", "👤 Login / Email *"),
            ("url", "🔗 URL"),
        ]
        for chave, label in campos:
            ctk.CTkLabel(
                frame, text=label, font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", pady=(10, 3))
            ent = ctk.CTkEntry(frame, height=35)
            ent.pack(fill="x")
            self.entries[chave] = ent

        # Senha
        ctk.CTkLabel(
            frame, text="🔑 Senha *", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 3))

        senha_box = ctk.CTkFrame(frame, fg_color="transparent")
        senha_box.pack(fill="x")
        self.entries["senha"] = ctk.CTkEntry(senha_box, height=35, show="•")
        self.entries["senha"].pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entries["senha"].bind("<KeyRelease>", self._atualizar_forca)

        self.btn_olho = ctk.CTkButton(
            senha_box, text="👁️", width=40, command=self._toggle_senha
        )
        self.btn_olho.pack(side="left", padx=2)
        ctk.CTkButton(senha_box, text="🎲", width=40, command=self._gerar).pack(
            side="left", padx=2
        )

        self.forca_label = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=11))
        self.forca_label.pack(anchor="w", pady=(3, 5))

        # Observações
        ctk.CTkLabel(
            frame, text="📄 Observações", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 3))
        self.obs_text = ctk.CTkTextbox(frame, height=100)
        self.obs_text.pack(fill="x")

        # Botões
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(pady=15)
        ctk.CTkButton(
            btns, text="Cancelar", width=120, fg_color="gray", command=self.destroy
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            btns,
            text="💾 Salvar",
            width=140,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._salvar,
        ).pack(side="left", padx=8)

    def _preencher(self, reg):
        for k in ["nome", "login", "url", "senha"]:
            self.entries[k].delete(0, "end")
            self.entries[k].insert(0, reg.get(k, ""))
        self.obs_text.delete("1.0", "end")
        self.obs_text.insert("1.0", reg.get("observacoes", ""))
        self._atualizar_forca()

    def _toggle_senha(self):
        atual = self.entries["senha"].cget("show")
        self.entries["senha"].configure(show="" if atual else "•")
        self.btn_olho.configure(text="🙈" if atual else "👁️")

    def _gerar(self):
        nova = gerar_senha_aleatoria(16, True)
        self.entries["senha"].delete(0, "end")
        self.entries["senha"].insert(0, nova)
        self._atualizar_forca()

    def _atualizar_forca(self, _=None):
        senha = self.entries["senha"].get()
        if not senha:
            self.forca_label.configure(text="")
            return
        _, cor, txt = forca_senha(senha)
        self.forca_label.configure(text=f"Força: {txt}", text_color=cor)

    def _salvar(self):
        nome = self.entries["nome"].get().strip()
        login = self.entries["login"].get().strip()
        senha = self.entries["senha"].get()
        url = self.entries["url"].get().strip()
        obs = self.obs_text.get("1.0", "end").strip()

        if not nome or not login or not senha:
            messagebox.showerror(
                "Erro", "Preencha os campos obrigatórios (*).", parent=self
            )
            return

        if self.registro:
            atualizado = atualizar_registro(
                self.registro.copy(),
                {
                    "nome": nome,
                    "login": login,
                    "senha": senha,
                    "url": url,
                    "observacoes": obs,
                },
            )
            self.callback(atualizado)
        else:
            self.callback(novo_registro(nome, login, senha, url, obs))

        self.destroy()
