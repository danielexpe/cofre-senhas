import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from seguranca.encriptacao import gerar_secret_id, encriptar_cofre
from utils.helpers import copiar_clipboard, forca_senha


class TelaNovoCofre:
    def __init__(self, master):
        self.master = master
        self.secret_id = gerar_secret_id()
        self._limpar()
        self._construir()

    def _limpar(self):
        for w in self.master.winfo_children():
            w.destroy()

    def _construir(self):
        frame = ctk.CTkFrame(self.master, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=40, pady=30)

        ctk.CTkLabel(
            frame, text="➕ Criar Novo Cofre",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            frame, text="Anote o Secret ID em local seguro. Sem ele, o cofre não poderá ser aberto!",
            font=ctk.CTkFont(size=12), text_color="#f39c12", wraplength=600
        ).pack(pady=(0, 20))

        # Secret ID
        sid_frame = ctk.CTkFrame(frame, fg_color="#1f2937")
        sid_frame.pack(fill="x", padx=40, pady=10)

        ctk.CTkLabel(sid_frame, text="🔑 Secret ID (gerado automaticamente):",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        sid_box = ctk.CTkFrame(sid_frame, fg_color="transparent")
        sid_box.pack(fill="x", padx=15, pady=(0, 10))

        self.sid_entry = ctk.CTkEntry(sid_box, font=ctk.CTkFont(size=14, family="Courier"))
        self.sid_entry.insert(0, self.secret_id)
        self.sid_entry.configure(state="readonly")
        self.sid_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))

        ctk.CTkButton(sid_box, text="📋 Copiar", width=80,
                      command=self._copiar_sid).pack(side="right")

        # Senha mestra
        ctk.CTkLabel(frame, text="🔒 Senha Mestra:",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=40, pady=(20, 5))
        self.senha_entry = ctk.CTkEntry(frame, show="•", height=40)
        self.senha_entry.pack(fill="x", padx=40)
        self.senha_entry.bind("<KeyRelease>", self._atualizar_forca)

        self.forca_label = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=11))
        self.forca_label.pack(anchor="w", padx=40, pady=(3, 10))

        ctk.CTkLabel(frame, text="🔒 Confirmar Senha Mestra:",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=40, pady=(5, 5))
        self.senha2_entry = ctk.CTkEntry(frame, show="•", height=40)
        self.senha2_entry.pack(fill="x", padx=40)

        # Botões
        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(pady=25)

        ctk.CTkButton(btns, text="← Voltar", width=120, fg_color="gray",
                      command=self._voltar).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="✓ Criar Cofre", width=160,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._criar).pack(side="left", padx=10)

    def _atualizar_forca(self, _=None):
        senha = self.senha_entry.get()
        if not senha:
            self.forca_label.configure(text="")
            return
        _, cor, txt = forca_senha(senha)
        self.forca_label.configure(text=f"Força: {txt}", text_color=cor)

    def _copiar_sid(self):
        copiar_clipboard(self.master, self.secret_id)
        messagebox.showinfo("Copiado", "Secret ID copiado para a área de transferência.")

    def _criar(self):
        senha = self.senha_entry.get()
        senha2 = self.senha2_entry.get()

        if len(senha) < 6:
            messagebox.showerror("Erro", "A senha mestra deve ter no mínimo 6 caracteres.")
            return
        if senha != senha2:
            messagebox.showerror("Erro", "As senhas não conferem.")
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar novo cofre",
            defaultextension=".vault",
            filetypes=[("Cofre", "*.vault")],
            initialdir=os.path.expanduser("~"),
            initialfile="meu_cofre.vault",
        )
        if not caminho:
            return

        try:
            encriptar_cofre(caminho, self.secret_id, senha, [])
            messagebox.showinfo(
                "Cofre Criado",
                f"Cofre criado com sucesso!\n\n"
                f"📁 Local: {caminho}\n\n"
                f"🔑 Secret ID: {self.secret_id}\n\n"
                f"⚠️ GUARDE ESTE SECRET ID EM LOCAL SEGURO!"
            )
            from ui.tela_principal import TelaPrincipal
            TelaPrincipal(self.master, caminho, self.secret_id, senha, [])
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao criar cofre:\n{e}")

    def _voltar(self):
        from ui.tela_inicial import TelaInicial
        TelaInicial(self.master)

