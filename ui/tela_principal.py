import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

from seguranca.encriptacao import encriptar_cofre
from dados.armazenamento import buscar_registros
from ui.formulario_registro import FormularioRegistro
from utils.helpers import copiar_clipboard


DEBOUNCE_BUSCA_MS = 250
COR_CARD_PAR = "#2f2f2f"
COR_CARD_IMPAR = "#262626"


class TelaPrincipal:
    def __init__(self, master, caminho, secret_id, senha, registros):
        self.master = master
        self.caminho = caminho
        self.secret_id = secret_id
        self.senha = senha
        self.registros = registros
        self.senha_visivel = {}

        # Lista virtualizada: só os cards visíveis existem de fato.
        self._container = None
        self.canvas = None
        self.scrollbar = None
        self._vazio_label = None
        self._pool = []
        self._filtrados = []
        self._row_h = None
        self._largura = 0
        self._render_job = None

        # Registra/atualiza no cache de cofres recentes
        from dados.cache import adicionar_ou_atualizar
        adicionar_ou_atualizar(caminho, secret_id)

        self._limpar()
        self._construir()

    def _limpar(self):
        for w in self.master.winfo_children():
            w.destroy()

    def _construir(self):
        topo = ctk.CTkFrame(self.master, corner_radius=0, height=70)
        topo.pack(fill="x")

        ctk.CTkLabel(
            topo,
            text=f"🔐 {os.path.basename(self.caminho)}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", padx=20, pady=15)

        ctk.CTkButton(
            topo,
            text="🚪 Sair",
            width=80,
            fg_color="#c0392b",
            hover_color="#922b21",
            command=self._sair
        ).pack(side="right", padx=10)

        ctk.CTkButton(
            topo,
            text="➕ Novo Registro",
            width=140,
            command=self._novo_registro
        ).pack(side="right", padx=5)

        busca_frame = ctk.CTkFrame(self.master, corner_radius=0)
        busca_frame.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(busca_frame, text="🔍").pack(side="left", padx=(10, 5))

        self.busca_entry = ctk.CTkEntry(
            busca_frame,
            placeholder_text="Buscar por nome, login ou URL..."
        )
        self.busca_entry.pack(side="left", fill="x", expand=True, padx=5, pady=8)
        self.busca_entry.bind("<KeyRelease>", lambda e: self._renderizar_lista(debounce=True))

        self._container = ctk.CTkFrame(self.master, corner_radius=10, fg_color="transparent")
        self._container.pack(fill="both", expand=True, padx=2, pady=2)

        fundo = self.master.cget("fg_color")
        if isinstance(fundo, (tuple, list)):
            fundo = fundo[1] if ctk.get_appearance_mode() == "Dark" else fundo[0]
        self._fundo = fundo

        self.canvas = tk.Canvas(self._container, highlightthickness=0, bd=0, bg=fundo)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(self._container, command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self._on_scroll)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_mousewheel()

        self._vazio_label = ctk.CTkLabel(
            self.canvas,
            text="📭 Nenhum registro encontrado.\nClique em '➕ Novo Registro' para começar.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )

        self.status = ctk.CTkLabel(
            self.master,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status.pack(side="bottom", pady=2)

        self._renderizar_lista()

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
        while widget is not None:
            if widget is self._container:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _on_mousewheel(self, event):
        if self.canvas is None or not self.canvas.winfo_exists():
            return

        if not self._widget_na_lista(event.widget):
            return

        if event.num == 4 or getattr(event, "delta", 0) > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or getattr(event, "delta", 0) < 0:
            self.canvas.yview_scroll(1, "units")

    def _on_scroll(self, first, last):
        self.scrollbar.set(first, last)
        self._atualizar_janela()

    def _on_canvas_configure(self, event):
        self._largura = event.width
        self._atualizar_scrollregion()
        self._atualizar_janela()

    def _cancelar_after(self, attr):
        job = getattr(self, attr)
        if job is not None:
            try:
                self.master.after_cancel(job)
            except Exception:
                pass
            setattr(self, attr, None)

    def _renderizar_lista(self, debounce=False):
        if debounce:
            self._cancelar_after("_render_job")
            self._render_job = self.master.after(
                DEBOUNCE_BUSCA_MS, self._renderizar_lista
            )
            return

        self._render_job = None

        if self.canvas is None or not self.canvas.winfo_exists():
            return

        termo = self.busca_entry.get() if hasattr(self, "busca_entry") else ""
        self._filtrados = buscar_registros(self.registros, termo)

        self.status.configure(
            text=f"Total: {len(self.registros)} registro(s) | Exibindo: {len(self._filtrados)}"
        )

        self._garantir_altura_card()
        self.canvas.yview_moveto(0)
        self._atualizar_scrollregion()

        if not self._filtrados:
            for card in self._pool:
                card["frame"].place_forget()
            self._vazio_label.place(relx=0.5, rely=0.5, anchor="center")
            return

        self._vazio_label.place_forget()
        self._atualizar_janela()

    def _garantir_altura_card(self):
        if self._row_h is not None:
            return
        card = self._criar_card()
        card["frame"].update_idletasks()
        self._row_h = max(card["frame"].winfo_reqheight() + 4, 44)
        self._pool.append(card)

    def _atualizar_scrollregion(self):
        if self._row_h is None:
            return
        largura = self._largura or self.canvas.winfo_width() or 400
        altura = max(self._row_h, len(self._filtrados) * self._row_h)
        self.canvas.configure(scrollregion=(0, 0, largura, altura))

    def _atualizar_janela(self):
        if self._row_h is None or not self._filtrados:
            return

        topo = self.canvas.canvasy(0)
        altura_visivel = self.canvas.winfo_height()
        primeiro = max(0, int(topo // self._row_h))
        quantidade = int(altura_visivel // self._row_h) + 2
        ultimo = min(len(self._filtrados), primeiro + quantidade)

        for card in self._pool:
            card["frame"].place_forget()

        largura = self._largura or self.canvas.winfo_width() or 400
        for posicao, indice in enumerate(range(primeiro, ultimo)):
            card = self._obter_card(posicao)
            y = indice * self._row_h - topo
            self._preencher_card(card, self._filtrados[indice], indice, y, largura)

    def _obter_card(self, posicao):
        while len(self._pool) <= posicao:
            self._pool.append(self._criar_card())
        return self._pool[posicao]

    def _criar_card(self):
        # Wrapper nativo: aceita width/height no place (o CTkFrame não aceita).
        wrapper = tk.Frame(self.canvas, bd=0, highlightthickness=0, bg=self._fundo)
        card = ctk.CTkFrame(wrapper, corner_radius=10, fg_color=COR_CARD_PAR)
        card.pack(fill="both", expand=True)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        nome = ctk.CTkLabel(
            info, text="", font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        )
        nome.pack(anchor="w", fill="x")

        login = ctk.CTkLabel(
            info, text="", font=ctk.CTkFont(size=12),
            text_color="#9ca3af", anchor="w"
        )
        login.pack(anchor="w", pady=2, fill="x")

        url = ctk.CTkLabel(
            info, text="", font=ctk.CTkFont(size=11),
            text_color="#60a5fa", anchor="w"
        )
        url.pack(anchor="w", fill="x")

        botoes = ctk.CTkFrame(card, fg_color="transparent")
        botoes.pack(side="right", padx=2, pady=2)

        copiar = ctk.CTkButton(botoes, text="📋 Copiar", width=80, fg_color="#16a085")
        copiar.pack(side="left", padx=2)

        editar = ctk.CTkButton(botoes, text="✏️ Editar", width=80, fg_color="#d68910")
        editar.pack(side="left", padx=2)

        excluir = ctk.CTkButton(botoes, text="🗑️ Excluir", width=80, fg_color="#c0392b")
        excluir.pack(side="left", padx=2)

        return {
            "frame": wrapper,
            "card": card,
            "nome": nome,
            "login": login,
            "url": url,
            "copiar": copiar,
            "editar": editar,
            "excluir": excluir,
        }

    def _preencher_card(self, card, reg, indice, y, largura):
        card["card"].configure(
            fg_color=COR_CARD_PAR if indice % 2 == 0 else COR_CARD_IMPAR
        )
        card["nome"].configure(text=f"🏷️  {reg['nome']}")
        card["login"].configure(text=f"👤  {reg['login']}")
        card["url"].configure(text=f"🔗  {reg['url']}" if reg.get("url") else "")
        card["copiar"].configure(command=lambda r=reg: self._copiar_senha(r))
        card["editar"].configure(command=lambda r=reg: self._editar(r))
        card["excluir"].configure(command=lambda r=reg: self._deletar(r))
        card["frame"].place(x=0, y=y, width=largura, height=self._row_h)

    def _toggle_senha(self, rid):
        self.senha_visivel[rid] = not self.senha_visivel.get(rid, False)
        self._renderizar_lista()

    def _copiar_senha(self, reg):
        copiar_clipboard(self.master, reg["senha"])
        self.status.configure(
            text=f"✓ Senha de '{reg['nome']}' copiada para área de transferência."
        )

    def _novo_registro(self):
        FormularioRegistro(self.master, self._adicionar_callback)

    def _adicionar_callback(self, novo):
        self.registros.append(novo)
        self._salvar()
        self._renderizar_lista()

    def _editar(self, reg):
        FormularioRegistro(self.master, self._editar_callback, registro=reg)

    def _editar_callback(self, atualizado):
        for i, r in enumerate(self.registros):
            if r["id"] == atualizado["id"]:
                self.registros[i] = atualizado
                break
        self._salvar()
        self._renderizar_lista()

    def _deletar(self, reg):
        if messagebox.askyesno("Confirmar", f"Deletar o registro '{reg['nome']}'?"):
            self.registros = [r for r in self.registros if r["id"] != reg["id"]]
            self._salvar()
            self._renderizar_lista()

    def _salvar(self):
        try:
            encriptar_cofre(self.caminho, self.secret_id, self.senha, self.registros)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar cofre:\n{e}")

    def _sair(self):
        self._cancelar_after("_render_job")
        self._unbind_mousewheel()
        self.senha = None
        self.secret_id = None
        self.registros = None
        from ui.tela_inicial import TelaInicial
        TelaInicial(self.master)
