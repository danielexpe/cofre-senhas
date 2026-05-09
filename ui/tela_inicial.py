import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.tela_novo_cofre import TelaNovoCofre
from ui.tela_autenticacao import TelaAutenticacao
from dados.cache import carregar_cache, remover as remover_do_cache, limpar_tudo
from datetime import datetime


class TelaInicial:
    def __init__(self, master):
        self.master = master
        self._limpar()
        self._construir()

    def _limpar(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def _construir(self):
        frame = ctk.CTkFrame(self.master, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Cabeçalho
        ctk.CTkLabel(
            frame, text="🔐 Cofre de Senhas",
            font=ctk.CTkFont(size=30, weight="bold")
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            frame, text="Gerencie suas credenciais com segurança",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(pady=(0, 20))

        # Botões de ação principais
        botoes = ctk.CTkFrame(frame, fg_color="transparent")
        botoes.pack(pady=10)

        ctk.CTkButton(
            botoes, text="➕  Criar Novo Cofre",
            width=220, height=45, font=ctk.CTkFont(size=14, weight="bold"),
            command=self._criar_novo
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            botoes, text="📂  Abrir Outro Cofre",
            width=220, height=45, font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2b6cb0", hover_color="#2c5282",
            command=self._abrir_existente
        ).pack(side="left", padx=8)

        # Lista de cofres recentes
        recentes = carregar_cache()
        if recentes:
            self._construir_recentes(frame, recentes)

        # Rodapé
        ctk.CTkLabel(
            frame, text="v1.1 • Encriptação AES + SHA512 + PBKDF2",
            font=ctk.CTkFont(size=11), text_color="gray"
        ).pack(side="bottom", pady=10)

    def _construir_recentes(self, parent, recentes):
        # Cabeçalho da seção
        cab = ctk.CTkFrame(parent, fg_color="transparent")
        cab.pack(fill="x", padx=40, pady=(25, 5))

        ctk.CTkLabel(
            cab, text="🕘 Cofres Recentes",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            cab, text="🗑️ Limpar Histórico", width=140, height=28,
            fg_color="transparent", border_width=1, border_color="gray",
            text_color="gray", hover_color="#3a3a3a",
            font=ctk.CTkFont(size=11),
            command=self._limpar_historico
        ).pack(side="right")

        # Container scrollável dos cards
        lista = ctk.CTkScrollableFrame(parent, corner_radius=10, height=200)
        lista.pack(fill="both", expand=True, padx=40, pady=(5, 10))

        for entrada in recentes:
            self._render_card_recente(lista, entrada)

    def _render_card_recente(self, parent, entrada):
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("#dbdbdb", "#2d2d2d"))
        card.pack(fill="x", pady=4, padx=4)

        # Hover effect simples (muda cursor)
        card.configure(cursor="hand2")

        # Área clicável principal (informações)
        info = ctk.CTkFrame(card, fg_color="transparent", cursor="hand2")
        info.pack(side="left", fill="both", expand=True, padx=12, pady=8)

        nome_arquivo = os.path.basename(entrada["caminho"])
        ctk.CTkLabel(
            info, text=f"📁 {nome_arquivo}",
            font=ctk.CTkFont(size=14, weight="bold"),
            cursor="hand2"
        ).pack(anchor="w")

        # Caminho completo (truncado se muito longo)
        caminho_exibir = entrada["caminho"]
        if len(caminho_exibir) > 70:
            caminho_exibir = "..." + caminho_exibir[-67:]
        ctk.CTkLabel(
            info, text=caminho_exibir,
            font=ctk.CTkFont(size=10), text_color="gray",
            cursor="hand2"
        ).pack(anchor="w")

        # Último acesso formatado
        try:
            dt = datetime.fromisoformat(entrada["ultimo_acesso"])
            tempo_str = dt.strftime("%d/%m/%Y às %H:%M")
        except Exception:
            tempo_str = "—"
        ctk.CTkLabel(
            info, text=f"🕘 Último acesso: {tempo_str}",
            font=ctk.CTkFont(size=10), text_color="#60a5fa",
            cursor="hand2"
        ).pack(anchor="w")

        # Bind de clique em todos os elementos da área info
        callback_abrir = lambda e, ent=entrada: self._abrir_recente(ent)
        for widget in [card, info] + info.winfo_children():
            widget.bind("<Button-1>", callback_abrir)

        # Botão de remover (separado, não dispara o clique do card)
        ctk.CTkButton(
            card, text="✕", width=30, height=30,
            fg_color="transparent", hover_color="#c0392b",
            text_color="gray", font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda ent=entrada: self._remover_recente(ent)
        ).pack(side="right", padx=8, pady=8)

    def _abrir_recente(self, entrada):
        caminho = entrada["caminho"]
        if not os.path.isfile(caminho):
            messagebox.showwarning(
                "Arquivo não encontrado",
                f"O arquivo do cofre não existe mais:\n{caminho}\n\nA entrada será removida do histórico."
            )
            remover_do_cache(caminho)
            self._limpar()
            self._construir()
            return

        # Abre tela de autenticação com Secret ID já preenchido
        TelaAutenticacao(self.master, caminho, secret_id_sugerido=entrada["secret_id"])

    def _remover_recente(self, entrada):
        if messagebox.askyesno(
            "Remover do histórico",
            f"Remover '{os.path.basename(entrada['caminho'])}' do histórico?\n\n"
            f"O arquivo do cofre NÃO será deletado."
        ):
            remover_do_cache(entrada["caminho"])
            self._limpar()
            self._construir()

    def _limpar_historico(self):
        if messagebox.askyesno(
            "Limpar histórico",
            "Tem certeza que deseja limpar todo o histórico de cofres recentes?\n\n"
            "Os arquivos dos cofres NÃO serão deletados."
        ):
            limpar_tudo()
            self._limpar()
            self._construir()

    def _criar_novo(self):
        TelaNovoCofre(self.master)

    def _abrir_existente(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo do cofre",
            filetypes=[("Cofre", "*.vault"), ("Todos", "*.*")],
            initialdir=os.path.expanduser("~"),
        )
        if caminho:
            TelaAutenticacao(self.master, caminho)
