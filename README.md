# Empório da Música — agente de atendimento

Protótipo de agente conversacional em Python para responder dúvidas sobre instrumentos, pedidos e políticas da loja. O projeto foi iniciado a partir dos CSVs e dos dois PDFs fornecidos no desafio.

## Rodar localmente

Requer Python 3.11 ou superior.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m app
```

Sem `GEMINI_API_KEY`, o agente usa um modo local simples que permite experimentar as consultas sem instalar nem chamar um provedor externo. Para habilitar o Gemini, preencha `GEMINI_API_KEY` no `.env`. `GEMINI_MODEL` é opcional e, por padrão, usa `gemini-3.6-flash`.

Exemplos:

```text
Você: Quais violões vocês têm até R$ 1.000?
Você: Qual o endereço e horário da loja?
Você: Quero consultar o pedido 8. Meu e-mail é ...
Você: Posso devolver uma compra online?
```

Digite `sair` para encerrar. O histórico fica apenas na memória do processo e não é persistido.

## Decisões técnicas

- **Python e CLI:** a restrição obrigatória é Python; uma CLI reduz dependências e deixa o fluxo do agente fácil de reproduzir e inspecionar.
- **Abordagem híbrida com ferramentas:** o modelo entende a intenção e escolhe entre `search_products`, `get_order_status` e `search_policy`. A aplicação executa consultas locais determinísticas nos CSVs e no manual estruturado. O modelo não recebe permissão para inventar preços ou estoque. O status do pedido exige número do pedido e confirmação por telefone ou e-mail cadastrado.
- **Gemini:** o SDK oficial `google-genai` e function calling são adequados para este protótipo: o modelo decide quando consultar o catálogo, pedidos ou políticas, enquanto as funções Python mantêm os dados como fonte da verdade. O modelo Flash é uma escolha de baixa latência/custo para conversas curtas. Consulte a [documentação de function calling](https://ai.google.dev/gemini-api/docs/function-calling) e a [lista de modelos](https://ai.google.dev/gemini-api/docs/models); modelos e disponibilidade podem mudar. Sem chave, o fallback local permite validar as ferramentas, mas oferece compreensão de linguagem mais limitada.
- **Dados e políticas:** os CSVs são lidos em tempo de execução, sem indexação vetorial porque são pequenos e tabulares. O PDF de políticas foi transcrito para uma referência Markdown por tópicos; a busca lexical retorna trechos para a resposta. Disponibilidade e preço são consultados no catálogo a cada solicitação. Promoções expiradas ou inativas não são oferecidas como vigentes.
- **Privacidade:** telefone e e-mail detectados na mensagem são ocultados antes do envio ao Gemini. O identificador fica temporariamente em memória para a função Python verificar o vínculo do pedido com o cadastro; não é incluído na resposta nem gravado em histórico persistente.
- **Instruções do modelo:** a persona é acolhedora e profissional. O prompt exige apoio nas ferramentas para fatos operacionais, transparência quando faltam dados, recusa cordial fora do escopo e escalonamento humano para situações que dependam de decisão da gerência.
- **Histórico:** mantido apenas durante a sessão da CLI; não há persistência, para evitar guardar dados pessoais em um protótipo.

## Estrutura

```text
app/
  __main__.py        entrada da CLI
  agent.py           orquestração, Gemini e fallback local
  data_store.py      consultas determinísticas aos CSVs
  policy_search.py   recuperação lexical de políticas
  settings.py        configuração por variáveis de ambiente
data/
  ...                arquivos fornecidos no desafio
  politicas.md       referência consultável extraída do PDF
examples/            conversas representativas
```

## Conversas de exemplo

Há quatro conversas em [`examples/`](examples/): busca de produto, dados da loja, verificação de pedido e aplicação da política de devolução. A resposta do modelo pode variar; os exemplos registram o comportamento pretendido e os dados que as ferramentas devem fornecer.

## Limitações e próximos passos

- Os CSVs são dados de demonstração fornecidos para o desafio, não um sistema de pedidos conectado em tempo real. Alterações precisam ser refletidas nesses arquivos.
- O manual lista contatos diferentes na capa e na seção de dados da empresa (telefone e e-mail). O protótipo preserva a divergência na referência e não presume qual contato é o canal correto.
- O modo local é intencionalmente simples e não substitui o modelo para linguagem natural variada.
- A busca de políticas é lexical; uma base maior justificaria busca semântica ou RAG com avaliação de recuperação.
- Com mais tempo, eu adicionaria testes de regressão para regras críticas, logs sem dados pessoais, uma interface HTTP e integração com o sistema real da loja.

## Uso de assistentes de código

Codex foi usado para ler os materiais do desafio, estruturar o projeto, implementar o protótipo e documentar decisões. O código foi organizado para que as consultas operacionais sejam executadas por funções Python explícitas; respostas do modelo devem ser conferidas contra os dados e regras fornecidos.



## Segurança e verificação

- O prompt de sistema é enviado pelo campo `system_instruction` do Gemini, separado das mensagens do cliente.
- Mensagens e resultados de ferramentas são tratados como dados não confiáveis; não há ferramenta para executar código, alterar pedidos ou acessar a rede.
- Chamadas de ferramenta aceitam apenas argumentos esperados e validam tipos, tamanhos, faixas de preço e número do pedido.
- Mensagens acima de 2.000 caracteres são recusadas; o histórico enviado ao modelo é limitado a 8 turnos; cada turno admite no máximo 4 chamadas de ferramenta e 4 rodadas.
- E-mail, telefone, CPF, cartão e credenciais detectados são mascarados antes de enviar a conversa ao modelo. A verificação do pedido ocorre localmente contra o CSV, sem devolver dados cadastrais.
- A chave permanece no `.env`, ignorado pelo Git. `store=False` e timeout de 45 segundos são usados nas chamadas do SDK.

Essas medidas reduzem a superfície de ataque, mas não garantem imunidade total a prompt injection: respostas ainda são geradas por um modelo probabilístico. O impacto é limitado pela ausência de ferramentas com efeitos externos e pela validação local dos dados.

Verificações automatizadas locais, sem chamada ao Gemini:

```powershell
python -m unittest discover -s tests -v
```

## Aderência ao enunciado

O projeto usa Python, oferece uma CLI, define a persona da loja, consulta CSVs para produto/pedido, recupera regras do manual, trata perguntas fora do escopo e inclui quatro exemplos de conversa. O histórico local contém commits incrementais. A publicação do repositório no GitHub ainda precisa ser feita para cumprir o item de repositório público.
