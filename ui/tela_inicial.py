import os
from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog, messagebox

from ui.tela_novo_cofre import TelaNovoCofre
from ui.tela_autenticacao import TelaAutenticacao
from dados.cache import carregar_cache, remover as remover_do_cache, limpar_tudo


COR_CARD = "#2d2d2d"
COR_CARD_HOVER = "#3a3a3a"
COR_TEXTO_SECUNDARIO = "#9ca3af"
COR_AZUL_CLARO = "#60a5fa"


class TelaInicial:
    def __init__(self, master):
        self.master = master
        self.lista_scroll = None
        self._limpar()
        self._construir()

    def _limpar(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def _construir(self):
        self._construir_rodape()
        self._construir_cabecalho()
        self._construir_secao_recentes()
        self._construir_lista()

    def _construir_rodape(self):
        ctk.CTkLabel(
            self.master,
            text="v2.0.0 • Encriptação AES + SHA512 + PBKDF2",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(side="bottom", pady=6)

    def _construir_cabecalho(self):
        cabecalho = ctk.CTkFrame(self.master, fg_color="transparent")
        cabecalho.pack(fill="x", padx=16, pady=(14, 6))

        # Botões à direita (na mesma linha do título)
        ctk.CTkButton(
            cabecalho,
            text="📂 Abrir",
            width=110,
            height=36,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2b6cb0",
            hover_color="#2c5282",
            command=self._abrir_existente
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            cabecalho,
            text="➕ Novo",
            width=100,
            height=36,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._criar_novo
        ).pack(side="right", padx=(8, 0))

        titulos = ctk.CTkFrame(cabecalho, fg_color="transparent")
        titulos.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            titulos,
            text="🔐 Cofre de Senhas",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            titulos,
            text="Gerencie suas credenciais com segurança",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).pack(anchor="w")

    def _construir_secao_recentes(self):
        secao = ctk.CTkFrame(self.master, fg_color="transparent")
        secao.pack(fill="x", padx=16, pady=(8, 4))

        ctk.CTkButton(
            secao,
            text="🗑️ Limpar",
            width=110,
            height=26,
            fg_color="transparent",
            border_width=1,
            border_color="#5a5a5a",
            text_color="gray",
            hover_color="#3a3a3a",
            font=ctk.CTkFont(size=12),
            command=self._limpar_historico
        ).pack(side="right")

        ctk.CTkLabel(
            secao,
            text="🕘 Cofres Recentes",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(side="left")

    def _construir_lista(self):
        self.lista_scroll = ctk.CTkScrollableFrame(
            self.master, corner_radius=8, fg_color="transparent"
        )
        self.lista_scroll.pack(fill="both", expand=True, padx=16, pady=(2, 8))

        self._bind_mousewheel()

        recentes = carregar_cache()
        self._atualizar_scrollbar(len(recentes))

        if not recentes:
            ctk.CTkLabel(
                self.lista_scroll,
                text="📭 Nenhum cofre recente ainda.\n"
                     "Clique em '➕ Novo' para criar seu primeiro cofre.",
                font=ctk.CTkFont(size=14),
                text_color="gray",
                justify="center"
            ).pack(pady=40, padx=20)
            return

        for entrada in recentes:
            self._render_card_recente(self.lista_scroll, entrada)

    def _atualizar_scrollbar(self, quantidade):
        if self.lista_scroll is None:
            return
        scrollbar = getattr(self.lista_scroll, "_scrollbar", None)
        if scrollbar is None:
            return
        if quantidade > 5:
            scrollbar.grid()
        else:
            scrollbar.grid_remove()

    def _bind_mousewheel(self):
        self._unbind_mousewheel()
        self.master.bind_all("<Button-4>", self._on_mousewheel, add="+")
        self.master.bind_all("<Button-5>", self._on_mousewheel, add="+")
        self.master.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _unbind_mousewheel(self):
        self.master.unbind_all("<Button-4>")
        self.master.unbind_all("<Button-5>")
        self.master.unbind_all("<MouseWheel>")

    def _widget_na_lista(self, widget):
        if self.lista_scroll is None:
            return False
        alvo = self.lista_scroll._parent_frame
        while widget is not None:
            if widget is alvo:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _on_mousewheel(self, event):
        if self.lista_scroll is None or not self.lista_scroll._parent_canvas.winfo_exists():
            return

        if not self._widget_na_lista(event.widget):
            return

        canvas = self.lista_scroll._parent_canvas
        if event.num == 4 or getattr(event, "delta", 0) > 0:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5 or getattr(event, "delta", 0) < 0:
            canvas.yview_scroll(1, "units")

    def _render_card_recente(self, parent, entrada):
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=COR_CARD)
        card.pack(fill="x", pady=3, padx=2)

        remover = ctk.CTkButton(
            card,
            text="✕",
            width=28,
            height=28,
            fg_color="transparent",
            hover_color="#c0392b",
            text_color="gray",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda ent=entrada: self._remover_recente(ent)
        )
        remover.pack(side="right", padx=(0, 8), pady=6)
        remover.bind(
            "<Enter>",
            lambda e, c=card: c.configure(fg_color=COR_CARD_HOVER)
        )
        remover.bind(
            "<Leave>",
            lambda e, c=card: c.configure(fg_color=COR_CARD)
        )

        conteudo = ctk.CTkFrame(card, fg_color="transparent")
        conteudo.pack(side="left", fill="both", expand=True, padx=12, pady=6)

        linha1 = ctk.CTkFrame(conteudo, fg_color="transparent")
        linha1.pack(fill="x")

        nome_arquivo = self._truncar_nome(
            os.path.splitext(os.path.basename(entrada["caminho"]))[0]
        )
        nome_lbl = ctk.CTkLabel(
            linha1,
            text=f"📁 {nome_arquivo}",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        nome_lbl.pack(side="left")

        acesso_lbl = ctk.CTkLabel(
            linha1,
            text=f"Último acesso: {self._formatar_tempo(entrada)}",
            font=ctk.CTkFont(size=12),
            text_color=COR_AZUL_CLARO
        )
        acesso_lbl.pack(side="right")

        caminho_lbl = ctk.CTkLabel(
            conteudo,
            text=self._truncar_caminho(entrada["caminho"]),
            font=ctk.CTkFont(size=12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w"
        )
        caminho_lbl.pack(fill="x", anchor="w", pady=(2, 0))

        alvos = [card, conteudo, linha1, nome_lbl, acesso_lbl, caminho_lbl]
        callback_abrir = lambda e, ent=entrada: self._abrir_recente(ent)

        for widget in alvos:
            widget.configure(cursor="hand2")
            widget.bind("<Button-1>", callback_abrir)
            widget.bind(
                "<Enter>",
                lambda e, c=card: c.configure(fg_color=COR_CARD_HOVER)
            )
            widget.bind(
                "<Leave>",
                lambda e, c=card: c.configure(fg_color=COR_CARD)
            )

    def _truncar_nome(self, nome):
        if len(nome) <= 42:
            return nome
        return nome[:39] + "..."

    def _truncar_caminho(self, caminho):
        if len(caminho) <= 90:
            return caminho
        return "..." + caminho[-(90 - 3):]

    def _formatar_tempo(self, entrada):
        try:
            dt = datetime.fromisoformat(entrada["ultimo_acesso"])
            return dt.strftime("%d/%m/%Y às %H:%M")
        except Exception:
            return "—"

    def _abrir_recente(self, entrada):
        caminho = entrada["caminho"]

        if not os.path.isfile(caminho):
            messagebox.showwarning(
                "Arquivo não encontrado",
                f"O arquivo do cofre não existe mais:\n{caminho}\n\n"
                "A entrada será removida do histórico."
            )
            remover_do_cache(caminho)
            self._limpar()
            self._construir()
            return

        TelaAutenticacao(self.master, caminho, secret_id_sugerido=entrada["secret_id"])

    def _remover_recente(self, entrada):
        if messagebox.askyesno(
            "Remover do histórico",
            f"Remover '{os.path.basename(entrada['caminho'])}' do histórico?\n\n"
            "O arquivo do cofre NÃO será deletado."
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
