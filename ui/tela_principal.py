import os
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox

from seguranca.encriptacao import encriptar_cofre
from dados.armazenamento import buscar_registros
from ui.formulario_registro import FormularioRegistro
from ui.dialogos_exportacao import (
    DialogoProgresso,
    DialogoRelatorio,
    DialogoResumoImportacao,
    DialogoSenhaPDF,
)
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

        # Ações de exportação/importação (agrupadas à esquerda, junto do título)
        self.btn_export_json = ctk.CTkButton(
            topo, text="⬆️ Exportar JSON", width=140, height=32,
            font=ctk.CTkFont(size=12), command=self._exportar_json
        )
        self.btn_export_json.pack(side="left", padx=4, pady=15)

        self.btn_import_json = ctk.CTkButton(
            topo, text="⬇️ Importar JSON", width=140, height=32,
            font=ctk.CTkFont(size=12), command=self._importar_json
        )
        self.btn_import_json.pack(side="left", padx=4, pady=15)

        self.btn_export_pdf = ctk.CTkButton(
            topo, text="📄 Exportar PDF", width=140, height=32,
            font=ctk.CTkFont(size=12), command=self._exportar_pdf
        )
        self.btn_export_pdf.pack(side="left", padx=4, pady=15)

        self.btn_sair = ctk.CTkButton(
            topo,
            text="🚪 Sair",
            width=80,
            fg_color="#c0392b",
            hover_color="#922b21",
            command=self._sair
        )
        self.btn_sair.pack(side="right", padx=10)

        self.btn_novo = ctk.CTkButton(
            topo,
            text="➕ Novo Registro",
            width=140,
            command=self._novo_registro
        )
        self.btn_novo.pack(side="right", padx=5)

        self._botoes_operacao = [
            self.btn_export_json, self.btn_import_json,
            self.btn_export_pdf, self.btn_novo,
        ]

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

    # ------------------------------------------------------------------
    # Exportar / Importar (JSON e PDF)
    # ------------------------------------------------------------------
    def _definir_botoes_habilitados(self, habilitado):
        estado = "normal" if habilitado else "disabled"
        for botao in getattr(self, "_botoes_operacao", []):
            try:
                botao.configure(state=estado)
            except Exception:
                pass

    def _executar_em_thread(self, texto, trabalho, ao_sucesso, ao_erro):
        """Roda `trabalho` em thread de fundo e devolve o resultado na thread Tk.

        A thread de fundo NÃO toca em widgets: apenas deposita o resultado em um
        dicionário. A thread principal faz polling com `after` e entrega o
        resultado/erro aos callbacks.
        """
        self._definir_botoes_habilitados(False)
        progresso = DialogoProgresso(self.master, texto)
        estado = {}

        def runner():
            try:
                estado["valor"] = trabalho()
            except Exception as e:  # noqa: BLE001
                estado["erro"] = e

        threading.Thread(target=runner, daemon=True).start()

        def verificar():
            if "valor" not in estado and "erro" not in estado:
                self.master.after(80, verificar)
                return
            try:
                progresso.fechar()
            except Exception:
                pass
            self._definir_botoes_habilitados(True)
            if "erro" in estado:
                ao_erro(estado["erro"])
            else:
                ao_sucesso(estado["valor"])

        self.master.after(80, verificar)

    def _diretorio_do_cofre(self):
        pasta = os.path.dirname(os.path.abspath(self.caminho))
        return pasta if os.path.isdir(pasta) else None

    def _exportar_json(self):
        from servicos.exportacao_json import (
            escrever_json_atomico,
            montar_payload,
            registros_invalidos_para_import,
        )

        base = os.path.splitext(os.path.basename(self.caminho))[0]
        caminho = filedialog.asksaveasfilename(
            parent=self.master,
            title="Exportar registros para JSON",
            defaultextension=".json",
            initialfile=f"{base}.json",
            initialdir=self._diretorio_do_cofre(),
            filetypes=[("JSON", "*.json"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        if not messagebox.askyesno(
            "Atenção",
            "O arquivo JSON conterá as senhas em TEXTO PURO.\n\n"
            "Guarde-o com segurança e apague-o após o uso.\n\nDeseja continuar?",
            parent=self.master,
        ):
            return

        payload = montar_payload(self.registros)
        invalidos = registros_invalidos_para_import(payload)
        total = len(self.registros)

        def trabalho():
            return escrever_json_atomico(caminho, payload)

        def sucesso(destino):
            linhas = [
                f"Cofre: {self.caminho}",
                f"Arquivo: {destino}",
                f"Registros: {total}",
                "",
                "⚠️  Contém senhas em TEXTO PURO. Guarde com segurança e apague após o uso.",
            ]
            if invalidos:
                linhas += ["", "--- Avisos de round-trip (não serão reimportados) ---"]
                linhas += [f"[inválido] #{i}  motivo: {m}" for i, m in invalidos]
            DialogoRelatorio(self.master, "Exportação JSON concluída", linhas)

        def erro(e):
            messagebox.showerror("Erro", f"Falha ao exportar JSON:\n{e}", parent=self.master)

        self._executar_em_thread("Exportando JSON...", trabalho, sucesso, erro)

    def _importar_json(self):
        from servicos.importacao import carregar_json, planejar_importacao

        caminho = filedialog.askopenfilename(
            parent=self.master,
            title="Importar registros de JSON",
            initialdir=self._diretorio_do_cofre(),
            filetypes=[("JSON", "*.json"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        def trabalho():
            itens = carregar_json(caminho)
            return planejar_importacao(self.registros, itens)

        def sucesso(resumo):
            if not resumo.importaveis:
                linhas = self._linhas_resultado_import(caminho, resumo)
                linhas += ["", "Nada a importar. Nenhuma alteração foi feita."]
                DialogoRelatorio(self.master, "Importação", linhas)
                return
            dialogo = DialogoResumoImportacao(self.master, caminho, resumo)
            self.master.wait_window(dialogo)
            if dialogo.resultado:
                self._aplicar_importacao(caminho, resumo)

        def erro(e):
            messagebox.showerror("Erro", f"Falha ao ler o JSON:\n{e}", parent=self.master)

        self._executar_em_thread("Lendo JSON...", trabalho, sucesso, erro)

    def _aplicar_importacao(self, caminho_json, resumo):
        from servicos.arquivos import fazer_backup

        novos = list(self.registros) + list(resumo.importaveis)

        def trabalho():
            backup = fazer_backup(self.caminho)
            encriptar_cofre(self.caminho, self.secret_id, self.senha, novos)
            return backup

        def sucesso(backup):
            self.registros = novos
            self._renderizar_lista()
            linhas = self._linhas_resultado_import(caminho_json, resumo)
            linhas += ["", f"Backup: {backup}"]
            DialogoRelatorio(self.master, "Importação concluída", linhas)

        def erro(e):
            messagebox.showerror("Erro", f"Falha ao importar:\n{e}", parent=self.master)

        self._executar_em_thread("Importando...", trabalho, sucesso, erro)

    def _linhas_resultado_import(self, caminho_json, resumo):
        linhas = [
            f"Arquivo: {caminho_json}",
            f"Itens lidos: {resumo.total_lidos}",
            "",
            f"  ✓ Importados ........: {len(resumo.importaveis)}",
            f"  ↷ Pulados (existente): {len(resumo.duplicados)}",
            f"  ↷ Pulados (repetido) : {len(resumo.repetidos)}",
            f"  ✗ Inválidos ..........: {len(resumo.invalidos)}",
        ]
        return linhas + self._linhas_nao_importados(resumo)

    def _linhas_nao_importados(self, resumo):
        itens = (
            [("inválido", i, m) for i, m in resumo.invalidos]
            + [("duplicado", i, m) for i, m in resumo.duplicados]
            + [("repetido", i, m) for i, m in resumo.repetidos]
        )
        if not itens:
            return []
        linhas = ["", "--- Itens não importados ---"]
        linhas += [
            f"[{tipo}] #{indice}  motivo: {motivo}"
            for tipo, indice, motivo in sorted(itens, key=lambda x: x[1])
        ]
        return linhas

    def _exportar_pdf(self):
        from servicos.exportacao_pdf import gerar_pdf, ordenar_registros

        base = os.path.splitext(os.path.basename(self.caminho))[0]
        caminho = filedialog.asksaveasfilename(
            parent=self.master,
            title="Exportar relatório PDF",
            defaultextension=".pdf",
            initialfile=f"{base}.pdf",
            initialdir=self._diretorio_do_cofre(),
            filetypes=[("PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        dialogo = DialogoSenhaPDF(self.master)
        self.master.wait_window(dialogo)
        if dialogo.resultado is None:
            return
        senha_pdf = dialogo.resultado
        cifrado = bool(senha_pdf)

        registros = ordenar_registros(self.registros)
        nome_cofre = os.path.basename(self.caminho)

        def trabalho():
            return gerar_pdf(caminho, registros, nome_cofre, senha_pdf)

        def sucesso(destino):
            linhas = [
                f"Cofre: {self.caminho}",
                f"Arquivo: {destino}",
                f"Registros: {len(registros)}",
                f"Cifrado: {'sim (AES)' if cifrado else 'NÃO'}",
                "",
            ]
            if cifrado:
                linhas.append(
                    "O PDF contém senhas em TEXTO PURO; a proteção é a senha de abertura."
                )
            else:
                linhas.append(
                    "⚠️  ATENÇÃO: PDF SEM CIFRA contendo senhas em TEXTO PURO."
                )
            DialogoRelatorio(self.master, "Exportação PDF concluída", linhas)

        def erro(e):
            messagebox.showerror("Erro", f"Falha ao gerar o PDF:\n{e}", parent=self.master)

        self._executar_em_thread("Gerando PDF...", trabalho, sucesso, erro)

    def _sair(self):
        self._cancelar_after("_render_job")
        self._unbind_mousewheel()
        self.senha = None
        self.secret_id = None
        self.registros = None
        from ui.tela_inicial import TelaInicial
        TelaInicial(self.master)
