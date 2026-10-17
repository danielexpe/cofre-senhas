Você é um desenvolvedor Python sênior, especialista em CustomTkinter, e vai implementar melhorias de layout e UX na tela que lista as secrets (registros) de um cofre já aberto, do aplicativo "Cofre de Senhas" (v1.5.0). Essa tela está em `ui/tela_principal.py` (confirme no código). Um designer/UX já definiu o que mudar, mantendo **coerência visual** com a tela inicial (`ui/tela_inicial.py`), que acabou de passar por uma melhoria de layout documentada em `docs/melhoria_layout_01.md`. Cabe a você descobrir onde e como alterar no código.

## OBJETIVO
Aproveitar melhor o espaço da tela, deixar o layout mais compacto, moderno e eficiente, e mostrar mais registros sem rolar. Hoje o cabeçalho concentra 5 botões largos numa única linha e cada card de registro tem 3 linhas de texto + 3 botões largos, o que desperdiça espaço horizontal e vertical.

## PROBLEMAS ATUAIS
- Cabeçalho (`topo`, altura 70) com título e 5 botões na mesma linha: "⬆️ Exportar JSON", "⬇️ Importar JSON", "📄 Exportar PDF", "➕ Novo Registro" e "🚪 Sair". Os três primeiros (140 px cada) ficam colados ao título à esquerda, espremendo o texto e consumindo largura; falta hierarquia visual.
- Cada card tem 3 linhas (nome, login, URL) + 3 botões largos (Copiar/Editar/Excluir, 80 px cada ≈ 240 px + paddings), encolhendo a área útil de texto e deixando o card alto.
- Cores de card alternadas (`#2f2f2f` / `#262626`) e `corner_radius=10`, diferentes da tela inicial (`#2d2d2d`, raio 8), quebrando a coerência visual.
- A senha do registro não é exibida nem há atalho para visualizá-la/ocultá-la (o método `_toggle_senha` existe, mas está sem uso).
- A barra de rolagem fica sempre visível, mesmo com poucos registros (a tela inicial já a oculta quando há poucos itens).
- O contador "Total/Exibindo" fica num rodapé solto, sem relação com a seção da lista.

## MELHORIAS A IMPLEMENTAR

1. **Cabeçalho em uma única linha**
   - Título "🔐 {nome do vault}" (sem a extensão `.vault`, coerente com a tela inicial) em fonte ~24 bold, com subtítulo pequeno e cinza logo abaixo (ex.: caminho do arquivo truncado ou "N registros").
   - À direita, na mesma linha, botões compactos com ícone e texto curto: "➕ Novo", "📄 PDF", "⬇️ Importar", "⬆️ Exportar" e "🚪 Sair". Agrupar visualmente os de exportar/importar/PDF; manter as cores atuais (azul para as ações, vermelho para "Sair").
   - Reduzir a altura do cabeçalho e os paddings para a faixa de 6 a 10 px.

2. **Busca + cabeçalho da seção**
   - Manter a barra de busca com ícone 🔍 e o placeholder atual; reduzir margens.
   - Título da seção "🔑 Registros" em negrito (~17), com o contador "N registros" (e "exibindo M" quando houver filtro de busca) integrado à direita, em fonte pequena e cinza, eliminando o rodapé de status solto.

3. **Cards compactos de 2 linhas**
   - Altura total aproximada de 52 a 60 px, `corner_radius=8`, cor de fundo `#2d2d2d` (igual à tela inicial).
   - Linha 1: ícone e nome do registro em negrito (~14) à esquerda; à direita, o login em fonte pequena e azul-claro (`#60a5fa`).
   - Linha 2: URL em fonte pequena e cinza (`#9ca3af`), truncada com reticências; se vazia, ocultar a linha sem quebrar o layout.
   - À direita, centralizado verticalmente, ações compactas: botões pequenos de copiar (📋), editar (✏️) e excluir (🗑️) — preferencialmente só ícone ou largura reduzida (32 a 40 px), mantendo as cores atuais (verde/âmbar/vermelho).
   - O card inteiro deve mostrar hover (fundo `#3a3a3a`) e cursor de mão, coerente com a tela inicial.

4. **Interação**
   - Manter os comportamentos atuais: copiar senha, editar e excluir, reutilizando os callbacks existentes (`_copiar_senha`, `_editar`, `_deletar`).
   - Os botões "✏️"/"🗑️" não devem disparar ações além das próprias.

5. **Lista virtualizada e rolagem**
   - Preservar a lista virtualizada (canvas + pool de cards) para manter o bom desempenho com muitos registros.
   - Mostrar a barra de rolagem apenas quando houver mais de 5 registros visíveis (coerente com a tela inicial); caso contrário, ocultá-la.

6. **Estados de borda**
   - Lista vazia: manter a mensagem amigável existente.
   - Nomes, logins ou URLs longos: truncar com reticências sem quebrar o layout.
   - Registros sem URL: ocultar a segunda linha ou exibir placeholder discreto.

## REGRAS E RESTRIÇÕES
- Não altere nenhuma lógica de negócio: encriptação, armazenamento, exportação/importação (JSON/PDF), histórico e módulos de segurança (pasta `seguranca/`) devem permanecer intactos.
- Mude apenas o necessário na interface. Preserve nomes de métodos, callbacks e integrações com as outras telas (por exemplo, `formulario_registro` e `dialogos_exportacao`).
- Mantenha o tema escuro e a identidade visual atual: fundo cinza-escuro, cards `#2d2d2d`, hover `#3a3a3a`, botões azuis, acento azul `#60a5fa`, cinza `#9ca3af`, fonte Roboto e ícones atuais.
- Mantenha todos os textos em português do Brasil.
- Não adicione dependências novas além das já usadas (customtkinter, cryptography etc.), a menos que seja indispensável. Se for, avise.
- Preserve a virtualização da lista (desempenho com dezenas de registros).

## ENTREGA
1. Primeiro, localize e leia o código de `ui/tela_principal.py` e liste brevemente quais trechos pretende alterar.
2. Implemente as mudanças.
3. Ao final, resuma o que foi alterado e aponte qualquer decisão tomada onde este briefing deixava margem. Informe também como testar (executar com `py main.py`) e confirme que as outras telas continuam funcionando.

## CRITÉRIOS DE ACEITE
- Cabeçalho com título/subtítulo à esquerda e botões compactos à direita, na mesma linha.
- Cards com 2 linhas, hover e cursor de mão, e ações de copiar/editar/excluir funcionando sem abrir nada.
- Coerência visual com a tela inicial (cores, raio 8, fontes e espaçamentos equivalentes).
- Mais registros visíveis sem rolar na janela de tamanho padrão.
- Barra de rolagem visível apenas com mais de 5 registros.
- Nenhuma regressão nas funções de criar, editar, excluir, copiar, buscar, exportar e importar registros.
