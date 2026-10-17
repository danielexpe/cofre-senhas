Você é um desenvolvedor Python sênior, especialista em CustomTkinter, e vai implementar melhorias de layout e UX na tela inicial do aplicativo "Cofre de Senhas" (v1.5.0). Essa é a tela que lista os cofres recentes (arquivos .vault). Pelos erros de execução, ela provavelmente está em ui/tela_inicial.py, mas confirme no código. Um designer/UX já definiu o que mudar. Cabe a você descobrir onde e como alterar no código.

## OBJETIVO
Aproveitar melhor o espaço da tela, deixar o layout mais compacto, moderno e eficiente, e mostrar mais cofres sem rolar. Hoje só 2 cofres aparecem por vez, porque há margens grandes, frames aninhados e cards altos.

## PROBLEMAS ATUAIS
- Existe um frame externo arredondado com margens grandes, e dentro dele outro frame para a lista. Isso desperdiça espaço.
- Cada item da lista tem 3 linhas (nome, caminho e data de último acesso) e ocupa cerca de 125 px de altura. Só 2 cofres cabem na tela.
- A lista não ocupa todo o espaço vertical livre da janela.
- O cabeçalho (título, subtítulo e dois botões grandes empilhados) consome muita altura.
- Os paddings são excessivos.

## MELHORIAS A IMPLEMENTAR

1. **Estrutura geral**
   - Remova o frame externo arredondado e os containers aninhados desnecessários. Use a própria janela como container principal.
   - Reduza as margens externas para cerca de 12 a 16 px e os espaçamentos internos entre seções para 6 a 10 px.
   - A lista de cofres deve ocupar todo o espaço vertical restante, entre o cabeçalho e o rodapé. Ela deve expandir e encolher junto com a janela.

2. **Cabeçalho em uma única linha**
   - Título "Cofre de Senhas" com ícone de cadeado à esquerda, com o subtítulo "Gerencie suas credenciais com segurança" logo abaixo, em fonte pequena e cinza.
   - À direita, na mesma linha, os botões "Novo" (criar novo cofre) e "Abrir" (abrir outro cofre). Devem ser compactos, de largura moderada, com ícone e texto curtos, e manter a cor azul atual.

3. **Cabeçalho da seção "Cofres Recentes"**
   - À esquerda, o ícone de relógio e o texto "Cofres Recentes" em negrito.
   - À direita, na mesma linha, o botão "Limpar Histórico" menor e discreto, em estilo contorno ou texto, com ícone de lixeira.

4. **Cards compactos de 2 linhas**
   - Cada card deve ter apenas 2 linhas, com altura total aproximada de 50 a 60 px.
   - Linha 1: ícone de pasta e nome do arquivo em negrito à esquerda. À direita, na mesma linha, o texto "Último acesso: dd/mm/aaaa às hh:mm" em fonte pequena e azul-claro.
   - Linha 2: caminho completo do arquivo em fonte pequena e cinza, alinhado à esquerda. Se for longo, trunque com reticências sem quebrar o layout.
   - À direita, centralizado verticalmente, o botão "✕" (remover do histórico) pequeno, de fundo transparente, com hover discreto.
   - Cantos arredondados menores (cerca de 8 px) e espaçamento de 4 a 6 px entre cards.
   - O card inteiro deve mostrar feedback visual de hover, como uma cor de fundo ligeiramente mais clara, e o cursor de mão.
   - Resultado esperado: de 5 a 6 cofres visíveis ao mesmo tempo numa janela de tamanho padrão.

5. **Interação**
   - Um clique ou duplo clique em qualquer parte do card (nome, caminho, data ou fundo) abre o cofre, com o mesmo comportamento do fluxo atual. Escolha a opção mais coerente com o funcionamento existente.
   - O botão "✕" deve remover apenas o item do histórico e não pode disparar a abertura do cofre.

6. **Janela**
   - Torne a janela redimensionável, se ainda não for, com um tamanho inicial confortável (cerca de 900x600) e um tamanho mínimo (cerca de 700x450).
   - Garanta que o layout se adapte bem ao redimensionar, sem cortes e sem espaços vazios exagerados.

7. **Rodapé**
   - Mantenha o texto "v1.5.0 • Encriptação AES + SHA512 + PBKDF2" centralizado, com fonte menor (cerca de 10) e margens mínimas.

## REGRAS E RESTRIÇÕES
- Não altere nenhuma lógica de negócio: criação, abertura e encriptação de cofres, histórico, persistência e módulos de segurança (pasta seguranca/) devem permanecer intactos.
- Mude apenas o necessário na interface. Preserve nomes de métodos, callbacks e integrações com as outras telas (por exemplo, a tela de novo cofre).
- Mantenha o tema escuro e a identidade visual atual: fundo cinza-escuro, cards em cinza um pouco mais claro, botões azuis, fonte Roboto e ícones atuais.
- Mantenha todos os textos em português do Brasil.
- Não adicione dependências novas além das já usadas (customtkinter, cryptography etc.), a menos que seja indispensável. Se for, avise.
- Garanta bom desempenho caso o histórico tenha dezenas de cofres, por exemplo evitando recriar toda a lista de forma custosa a cada tecla digitada na busca.
- Trate os casos de borda: lista vazia (mostre uma mensagem amigável), nomes ou caminhos muito longos, e arquivos do histórico que não existem mais (mantenha o comportamento atual, ou indique visualmente de forma discreta, sem quebrar nada).

## ENTREGA
1. Primeiro, localize e leia o código da tela inicial e liste brevemente quais arquivos e trechos pretende alterar.
2. Implemente as mudanças.
3. Ao final, resuma o que foi alterado e aponte qualquer decisão que tenha tomado onde este briefing deixava margem. Informe também como testar (executar com "py main.py") e confirme que as outras telas continuam funcionando.

## CRITÉRIOS DE ACEITE
- Pelo menos 5 cofres visíveis ao mesmo tempo, na janela padrão, sem rolar.
- Cabeçalho com título e botões na mesma linha.
- Cards com 2 linhas, hover e clique para abrir, e o "✕" remove sem abrir.
- A lista acompanha o redimensionamento da janela.
- Nenhuma regressão nas funções de criar, abrir e remover cofres do histórico.

