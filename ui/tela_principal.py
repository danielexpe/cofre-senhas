import os
import customtkinter as ctk
from tkinter import messagebox
from seguranca.encriptacao import encriptar_cofre
from dados.armazenamento import buscar_registros
from ui.formulario_registro import FormularioRegistro
from utils.helpers import copiar_clipboard


class TelaPrincipal:
    def __init__(self, master, caminho, secret_id, senha, registros):
        self.master = master
        self.caminho = caminho
        self.secret_id = secret_id
        self.senha = senha
        self.registros = registros
        self.senha_visivel = {}

        # Registra/atualiza no cache de cofres recentes
        from dados.cache import adicionar_ou_atualizar
        adicionar_ou_atualizar(caminho, secret_id)
        
        self._limpar()
        self._construir()

    def _limpar(self):
        for w in self.master.winfo_children():
            w.destroy()

    def _construir(self):
        # Topo
        topo = ctk.CTkFrame(self.master, corner_radius=0, height=70)
        topo.pack(fill="x")

        ctk.CTkLabel(topo, text=f"🔐 {os.path.basename(self.caminho)}",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=20, pady=15)

        ctk.CTkButton(topo, text="🚪 Sair", width=80, fg_color="#c0392b",
                      hover_color="#922b21", command=self._sair).pack(side="right", padx=10)
        ctk.CTkButton(topo, text="➕ Novo Registro", width=140,
                      command=self._novo_registro).pack(side="right", padx=5)

        # Busca
        busca_frame = ctk.CTkFrame(self.master, corner_radius=0)
        busca_frame.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(busca_frame, text="🔍").pack(side="left", padx=(10, 5))
        self.busca_entry = ctk.CTkEntry(busca_frame, placeholder_text="Buscar por nome, login ou URL...")
        self.busca_entry.pack(side="left", fill="x", expand=True, padx=5, pady=8)
        self.busca_entry.bind("<KeyRelease>", lambda e: self._renderizar_lista())

        # Lista (scrollable)
        self.lista_frame = ctk.CTkScrollableFrame(self.master, corner_radius=10)
        self.lista_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Rodapé
        self.status = ctk.CTkLabel(self.master, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.status.pack(side="bottom", pady=5)

        self._renderizar_lista()

    def _renderizar_lista(self):
        for w in self.lista_frame.winfo_children():
            w.destroy()

        termo = self.busca_entry.get() if hasattr(self, "busca_entry") else ""
        filtrados = buscar_registros(self.registros, termo)

        if not filtrados:
            ctk.CTkLabel(self.lista_frame,
                         text="📭 Nenhum registro encontrado.\nClique em '➕ Novo Registro' para começar.",
                         font=ctk.CTkFont(size=14), text_color="gray").pack(pady=60)
        else:
            for reg in filtrados:
                self._render_card(reg)

        self.status.configure(text=f"Total: {len(self.registros)} registro(s) | Exibindo: {len(filtrados)}")

    def _render_card(self, reg):
        card = ctk.CTkFrame(self.lista_frame, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(info, text=f"🏷️  {reg['nome']}",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(info, text=f"👤  {reg['login']}",
                     font=ctk.CTkFont(size=12), text_color="#9ca3af").pack(anchor="w", pady=2)

        if reg.get("url"):
            ctk.CTkLabel(info, text=f"🔗  {reg['url']}",
                         font=ctk.CTkFont(size=11), text_color="#60a5fa").pack(anchor="w")

        senha_visivel = self.senha_visivel.get(reg["id"], False)
        senha_txt = reg["senha"] if senha_visivel else "•" * 10
        ctk.CTkLabel(info, text=f"🔑  {senha_txt}",
                     font=ctk.CTkFont(size=12, family="Courier")).pack(anchor="w", pady=2)

        # Botões de ação
        botoes = ctk.CTkFrame(card, fg_color="transparent")
        botoes.pack(side="right", padx=10, pady=10)

        olho = "🙈" if senha_visivel else "👁️"
        ctk.CTkButton(botoes, text=olho, width=40,
                      command=lambda r=reg: self._toggle_senha(r["id"])).pack(side="left", padx=2)
        ctk.CTkButton(botoes, text="📋", width=40, fg_color="#16a085",
                      command=lambda r=reg: self._copiar_senha(r)).pack(side="left", padx=2)
        ctk.CTkButton(botoes, text="✏️", width=40, fg_color="#d68910",
                      command=lambda r=reg: self._editar(r)).pack(side="left", padx=2)
        ctk.CTkButton(botoes, text="🗑️", width=40, fg_color="#c0392b",
                      command=lambda r=reg: self._deletar(r)).pack(side="left", padx=2)

    def _toggle_senha(self, rid):
        self.senha_visivel[rid] = not self.senha_visivel.get(rid, False)
        self._renderizar_lista()

    def _copiar_senha(self, reg):
        copiar_clipboard(self.master, reg["senha"])
        self.status.configure(text=f"✓ Senha de '{reg['nome']}' copiada para área de transferência.")

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
        # Limpa dados sensíveis da memória
        self.senha = None
        self.secret_id = None
        self.registros = None
        from ui.tela_inicial import TelaInicial
        TelaInicial(self.master)

