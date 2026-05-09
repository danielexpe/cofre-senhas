import os
import customtkinter as ctk
from tkinter import messagebox
from seguranca.encriptacao import decriptar_cofre


class TelaAutenticacao:
    def __init__(self, master, caminho_cofre, secret_id_sugerido: str = ""):
        self.master = master
        self.caminho = caminho_cofre
        self.secret_id_sugerido = secret_id_sugerido
        self._limpar()
        self._construir()

    def _limpar(self):
        for w in self.master.winfo_children():
            w.destroy()

    def _construir(self):
        frame = ctk.CTkFrame(self.master, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=40, pady=40)

        ctk.CTkLabel(frame, text="🔓 Autenticação",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(40, 5))
        ctk.CTkLabel(frame, text=f"📁 {os.path.basename(self.caminho)}",
                     font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 5))

        # Aviso quando o Secret ID veio do cache
        if self.secret_id_sugerido:
            ctk.CTkLabel(
                frame,
                text="✓ Secret ID carregado do histórico",
                font=ctk.CTkFont(size=11), text_color="#27ae60"
            ).pack(pady=(0, 20))
        else:
            ctk.CTkLabel(frame, text="").pack(pady=(0, 15))

        ctk.CTkLabel(frame, text="🔑 Secret ID:",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=80)
        self.sid_entry = ctk.CTkEntry(frame, height=40, font=ctk.CTkFont(family="Courier"))
        self.sid_entry.pack(fill="x", padx=80, pady=(5, 15))

        # Pré-preenche se veio do cache
        if self.secret_id_sugerido:
            self.sid_entry.insert(0, self.secret_id_sugerido)

        ctk.CTkLabel(frame, text="🔒 Senha Mestra:",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=80)
        self.senha_entry = ctk.CTkEntry(frame, show="•", height=40)
        self.senha_entry.pack(fill="x", padx=80, pady=(5, 20))
        self.senha_entry.bind("<Return>", lambda e: self._autenticar())

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(pady=10)
        ctk.CTkButton(btns, text="← Voltar", width=120, fg_color="gray",
                      command=self._voltar).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="🔓 Abrir Cofre", width=160,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._autenticar).pack(side="left", padx=10)

        # Foco inteligente: se Secret ID já está preenchido, foca direto na senha
        if self.secret_id_sugerido:
            self.senha_entry.focus()
        else:
            self.sid_entry.focus()

    def _autenticar(self):
        sid = self.sid_entry.get().strip()
        senha = self.senha_entry.get()

        if not sid or not senha:
            messagebox.showerror("Erro", "Preencha Secret ID e Senha Mestra.")
            return

        try:
            registros = decriptar_cofre(self.caminho, sid, senha)
            from ui.tela_principal import TelaPrincipal
            TelaPrincipal(self.master, self.caminho, sid, senha, registros)
        except ValueError as e:
            messagebox.showerror("Falha", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado:\n{e}")

    def _voltar(self):
        from ui.tela_inicial import TelaInicial
        TelaInicial(self.master)
