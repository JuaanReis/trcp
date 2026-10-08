# TRCP

Ferramenta de terminal para descobrir estabelecimentos por categoria e área geográfica, salvar leads em SQLite, consultar contatos, aplicar filtros, acompanhar estatísticas e exportar os registros.

Os dados de descoberta vêm do OpenStreetMap, consultado pela API Overpass. A interface interativa utiliza Questionary.

## Sumário

- [Instalação](#instalação)
- [Navegação no terminal](#navegação-no-terminal)
- [Dados de um lead](#dados-de-um-lead)
- [New prospecting — nova prospecção](#new-prospecting--nova-prospecção)
- [My leads — leads salvos](#my-leads--leads-salvos)
- [Search lead — pesquisa e filtros](#search-lead--pesquisa-e-filtros)
- [Statistics — estatísticas](#statistics--estatísticas)
- [Export leads — exportação](#export-leads--exportação)
- [Configuração e organização](#configuração-e-organização)
- [Problemas comuns](#problemas-comuns)
- [Limitações](#limitações)

## Instalação

### Requisitos

- Python 3.10 ou superior para a sintaxe utilizada nos trechos apresentados. Eventuais requisitos mais altos do projeto completo prevalecem.
- Terminal interativo com suporte a teclado e caracteres UTF-8.
- Internet para descobrir novos estabelecimentos.
- Projeto completo, incluindo modelo de lead, banco, menu e módulo de conexão HTTP.

Consultar leads já salvos, filtrar, calcular estatísticas e exportar são operações locais nos códigos apresentados.

### Ambiente virtual no Windows

Abra o terminal na pasta do projeto:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Se a ativação não estiver disponível, use diretamente o executável do ambiente:

```powershell
.venv\Scripts\python.exe -m pip install httpx questionary openpyxl python-docx
```

Com o ambiente ativado:

```powershell
python -m pip install httpx questionary openpyxl python-docx
```

Se o projeto tiver `requirements.txt` ou instruções de instalação no `pyproject.toml`, prefira essas dependências: a lista acima cobre somente as bibliotecas identificadas nos códigos apresentados. Questionary utiliza Prompt Toolkit, importado pela pesquisa com autocomplete. SQLite faz parte da biblioteca padrão do Python.

| Biblioteca | Uso |
| --- | --- |
| `httpx` | Comunicação HTTP com a Overpass |
| `questionary` | Menus, perguntas e autocomplete |
| `prompt_toolkit` | Sugestões personalizadas durante a digitação |
| `openpyxl` | Exportação Excel |
| `python-docx` | Exportação Word |

### Iniciar

Execute o ponto de entrada definido pelo projeto, a partir da raiz. Se ele for um arquivo, use `python caminho_do_arquivo.py`; se for um pacote com `__main__.py`, use `python -m nome_do_pacote`. Esses nomes são exemplos de formato, não comandos confirmados para esta distribuição.

O ZIP de descoberta isolado não inicia o menu: ele depende de arquivos externos.

## Navegação no terminal

Embora este guia esteja em português, os rótulos das telas compartilhadas estão em inglês.

| Tecla ou ação | Comportamento |
| --- | --- |
| Setas para cima e para baixo | Navegar nas opções ou sugestões |
| `ENTER` | Confirmar uma opção ou campo |
| `ESPAÇO` na seleção de categorias | Marcar ou desmarcar uma categoria |
| Digitar em campo de pesquisa | Atualizar as sugestões |
| Campo vazio na busca de leads + `ENTER` | Voltar ao menu da pesquisa |
| `Back to main menu` | Retornar ao menu principal |
| `Ctrl+C` em pergunta Questionary | Cancela a pergunta; as telas apresentadas tratam retorno `None` |

Interromper uma pergunta é diferente de interromper uma requisição em andamento. O encerramento das tarefas de rede pode aguardar as threads que já começaram. Os prompts comuns de `input()` não possuem o mesmo tratamento de cancelamento do Questionary.

## Dados de um lead

| Campo | Conteúdo |
| --- | --- |
| `name` | Nome informado no OpenStreetMap |
| `category` | Categorias selecionadas que correspondem às tags do objeto, separadas por vírgula |
| `location` | Cidade e estado digitados na prospecção |
| `website` | Valor de `website` ou, como alternativa, `contact:website` |
| `phone` | Valor de `phone` ou, como alternativa, `contact:phone` |
| `social_profiles` | Lista usada pela integração apresentada para guardar Instagram |
| `score` | Pontuação armazenada pelo modelo/banco |
| `status` | Status armazenado pelo modelo/banco |
| `created_at` | Data de criação do registro |

`Not informed` significa que o campo não foi informado nos dados consultados. Não comprova que a empresa não possui site, telefone ou Instagram.

A localização exibida não é um endereço verificado: é o rótulo digitado para a área pesquisada. O significado da pontuação e os valores possíveis de status dependem do modelo e de regras não incluídos no ZIP. Os trechos apresentados não implementam cálculo de score nem edição de status.

## New prospecting — nova prospecção

Busca novos estabelecimentos na internet e salva os resultados no banco.

### 1. Prioridades opcionais

`Configure optional result priorities?` permite escolher quais resultados aparecem primeiro.

| Preferência | Opções apresentadas |
| --- | --- |
| Site | Sem preferência; informado primeiro; não informado primeiro |
| Telefone | Sem preferência; informado primeiro; não informado primeiro; 9 dígitos começando com 9 primeiro; 8 dígitos primeiro |

Essas prioridades organizam a exibição em `Matching preferences` e `Other results`. Todos os leads encontrados são enviados a `save_leads()` antes da separação. Portanto, prioridade não exclui registros do banco.

O comportamento exato de classificação depende de `prioritize_leads()`, cujo código não está no ZIP. Os filtros da tela Search lead, descritos abaixo, têm implementação própria e efetivamente restringem a lista exibida.

### 2. Categorias

Em `Search categories (blank shows all):`, digite um termo, como `roupa` ou `bicicleta`. A busca de categorias compara palavras com ID, nome, grupo e palavras-chave, ignorando maiúsculas e acentos.

Deixe o campo vazio para mostrar as categorias disponíveis, respeitando o limite de sugestões configurado na chamada. O catálogo fornecido possui 186 categorias.

Na lista `Select categories:`, marque com `ESPAÇO` e confirme com `ENTER`. Depois escolha:

- `Search more categories`: pesquisar outro termo mantendo as seleções anteriores.
- `Continue`: avançar; exige pelo menos uma categoria.
- `Cancel`: cancelar a prospecção.

Ao revisar uma lista de sugestões, desmarcar uma categoria anteriormente selecionada remove essa seleção. Categorias que não aparecem na lista atual continuam selecionadas.

Selecionar várias categorias amplia a consulta. Um estabelecimento pode corresponder a mais de uma e receber todas as categorias correspondentes no mesmo lead.

### 3. Cidade e estado

Preencha `City:` e `State:`. Nos trechos apresentados, ambos sugerem São Paulo e exigem texto não vazio.

Esses campos rotulam os resultados. Digitar outra cidade não muda a área automaticamente; é necessário alterar as coordenadas.

### 4. Bounding box

`Bounding box (south, west, north, east):` define um retângulo geográfico, na ordem:

```text
sul, oeste, norte, leste
```

Exemplo:

```text
-23.56, -46.65, -23.54, -46.63
```

Use ponto decimal e vírgula entre os quatro valores. O exemplo representa uma pequena área, não toda a cidade de São Paulo.

A validação exige números finitos, latitude entre -90 e 90, longitude entre -180 e 180, sul menor que norte e oeste menor que leste. O código não aceita um retângulo que atravesse o antimeridiano.

Escolha inicialmente uma área pequena. Retângulos muito grandes podem aumentar o tempo de resposta ou ultrapassar os recursos disponíveis na Overpass.

### 5. Modo de busca

| Modo | Funcionamento |
| --- | --- |
| `Single request` | Uma região e um worker |
| `Parallel` | Divide o retângulo em faixas de latitude; usa `parts` regiões e até `threads` workers |

Divisão não aumenta a cobertura: as faixas compõem o mesmo retângulo original. O número real de workers não excede a quantidade de regiões. Mais threads não garantem busca mais rápida; a capacidade do servidor também influencia.

### 6. Resultado e salvamento

A tela mostra:

| Indicador | Significado |
| --- | --- |
| `Time` | Tempo de busca e salvamento, medido no trecho apresentado |
| `Found` | Quantidade de leads produzidos pela descoberta |
| `Saved` | Valor retornado por `save_leads()` |

Cada lead é exibido com os dados disponíveis. Sem prioridades, aparece em `Results`; com prioridades ativas, em dois grupos.

A descoberta aceita objetos OSM `node`, `way` e `relation`, exige nome e correspondência com pelo menos um filtro de categoria. Dentro da mesma busca, objetos com o mesmo tipo e ID são reunidos, inclusive quando aparecem em regiões sobrepostas. Objetos OSM distintos podem representar a mesma empresa; filiais com o mesmo nome permanecem distintas.

Não confunda essa deduplicação com a do banco: repetir uma prospecção pode gerar novos registros, dependendo das regras de `save_leads()`. Os códigos anteriores da conversa tratavam registros repetidos entre pesquisas como possíveis.

### Instagram

Com a alteração apresentada aplicada, a criação de leads lê `contact:instagram` e `instagram` e preenche `social_profiles`. Valores idênticos são evitados na lista; uma URL e um nome de usuário equivalentes ainda podem ser strings distintas.

O perfil pode vir como URL, `@usuario` ou nome de usuário. Não há pesquisa externa do Instagram, visita ao site para localizar links nem verificação de titularidade nos trechos apresentados. O `mapping.py` original do ZIP não inclui essa alteração.

## My leads — leads salvos

Esta opção se destina à visualização dos registros persistidos. A integração discutida usa `list_leads()` e a exibição compartilhada `show_lead()` para manter os dados consistentes, incluindo Instagram.

O arquivo completo dessa tela não está no ZIP, portanto paginação, ordenação e eventuais ações adicionais precisam ser conferidas na implementação instalada. Este guia não pressupõe funções de editar, apagar ou marcar um lead como contatado.

## Search lead — pesquisa e filtros

Consulta os leads já salvos. Não executa uma nova busca na Overpass.

Ao abrir a tela, `list_leads()` carrega os registros em memória. O menu mostra `Matching leads: X / Y`, sendo X a quantidade após os filtros e Y o total carregado.

| Opção | Ação |
| --- | --- |
| `Search matching leads` | Abrir autocomplete sobre os resultados filtrados |
| `Show all matching leads` | Exibir todos os resultados filtrados |
| `Configure filters` | Definir filtros de site, telefone e Instagram |
| `Clear filters` | Restaurar a lista completa carregada |
| `Back to main menu` | Encerrar a tela |

### Combinar filtros

| Campo | Filtros |
| --- | --- |
| Site | `Any`, `Website informed`, `Website not informed` |
| Telefone | `Any`, `Phone informed`, `Phone not informed`, `9 digits starting with 9`, `8 digits` |
| Instagram | `Any`, `Instagram informed`, `Instagram not informed` |

Os critérios de campos diferentes se combinam: um lead precisa atender a todos. `Any` não restringe aquele campo. Configurar novamente substitui os filtros anteriores, usando a lista completa carregada como base.

Exemplo para encontrar empresas com contato disponível e site não informado:

1. Escolha `Configure filters`.
2. Selecione `Website not informed`.
3. Selecione `9 digits starting with 9`.
4. Selecione `Any` para Instagram.
5. Abra `Show all matching leads` ou `Search matching leads`.

Cancelar uma pergunta de filtros mantém a seleção anterior. Se nenhum lead atender aos filtros, a tela informa isso e permite reconfigurá-los.

### Como o telefone é interpretado

O filtro remove caracteres de formatação e reconhece números locais, com DDD e com código brasileiro `55` ou `0055`.

| Valor salvo | Número local considerado |
| --- | --- |
| `99999-1234` | `999991234` |
| `(11) 99999-1234` | `999991234` |
| `+55 (11) 99999-1234` | `999991234` |
| `0055 11 99999-1234` | `999991234` |
| `(11) 3333-1234` | `33331234` |

O filtro de nove dígitos também exige que o número local comece com `9`. Vários telefones são separados por ponto e vírgula ou quebra de linha; basta um corresponder. Separadores diferentes, ramais ou prefixos de operadora não são tratados especificamente e podem impedir a classificação.

Telefone informado significa texto não vazio, não número validado. Nove dígitos não confirma WhatsApp; oito dígitos é uma classificação por comprimento.

### Autocomplete

Digite parte do nome, categoria, localização, telefone, site ou Instagram. A busca textual ignora acentos e diferenças entre maiúsculas e minúsculas. O `@` é removido na comparação, permitindo buscar `@usuario` quando o cadastro contém uma URL.

Todas as palavras digitadas precisam aparecer no texto combinado do lead, mas podem corresponder a campos diferentes. A busca textual do telefone não remove sua pontuação: o filtro por formato faz esse tratamento separadamente.

Use as setas para escolher uma sugestão e confirme com `ENTER`. É necessário selecionar um item válido; texto livre sem correspondência selecionada não abre detalhes. O índice na opção distingue registros com nomes iguais.

A tela de detalhes utiliza `show_lead()`. Depois de visualizar, pressione `ENTER` para voltar à pesquisa; deixe a busca vazia para retornar ao menu de filtros.

Os registros são carregados uma vez ao entrar. Saia e abra novamente para consultar mudanças posteriores no banco.

## Statistics — estatísticas

Consulta agregações do SQLite sobre os registros salvos. A tela inicial mostra `Total saved` e `Average score`.

| Opção | Conteúdo |
| --- | --- |
| `Contact coverage` | Disponibilidade de site e telefone |
| `By status` | Quantidade por status |
| `By category` | Quantidade por categoria |
| `Refresh` | Consultar novamente o banco |
| `Back to main menu` | Retornar ao menu principal |

### Contact coverage

- `Website informed`: site preenchido.
- `Website not informed`: site ausente ou vazio.
- `Phone informed`: telefone preenchido.
- `Phone not informed`: telefone ausente ou vazio.
- `Website and phone`: os dois preenchidos.
- `Neither informed`: nenhum dos dois preenchido.

Cada linha mostra quantidade e percentual sobre o total de registros. As linhas se sobrepõem: um lead com site e telefone conta nas duas coberturas e também em `Website and phone`. Não some todas como se fossem grupos exclusivos.

A ausência de contato nessa estatística considera apenas site e telefone. A função de estatísticas apresentada não mede Instagram.

### Status, categorias e score

`By status` agrupa pelo valor salvo e ordena pela quantidade decrescente, depois pelo status.

`By category` separa o campo de categorias por vírgula e conta cada categoria uma vez por registro. Um lead com várias categorias participa de vários grupos; os percentuais podem somar mais de 100%. A ordenação é por quantidade decrescente e depois nome.

`Average score` é a média dos valores armazenados. Sem um mecanismo de pontuação, ela não representa uma avaliação comercial automática. Os totais contabilizam registros, não necessariamente empresas únicas. Com banco vazio, a tela informa que não há leads.

## Export leads — exportação

Exporta todos os registros retornados por `list_leads()`. Os filtros da pesquisa não são compartilhados com essa tela.

### Passo a passo

1. Abra `Export leads`.
2. Escolha CSV, JSON, Excel ou Word.
3. Confirme ou altere o caminho do arquivo.
4. Se o arquivo já existir, confirme a substituição ou cancele.
5. Confira `Exported` e `File`.

O destino sugerido segue este padrão na pasta de trabalho atual:

```text
exports/leads_AAAAMMDD_HHMMSS.extensao
```

A extensão deve corresponder ao formato escolhido. Pastas de destino são criadas se necessário. Destinos existentes que não sejam arquivos regulares são rejeitados. Cancelar não gera um novo arquivo; o código apresentado ainda pode pedir `ENTER` ao sair por causa do bloco `finally`.

### Formatos

| Formato | Organização e uso |
| --- | --- |
| CSV `.csv` | Tabela com separador `;`, codificação UTF-8 com BOM e cabeçalho; útil para importar em planilhas |
| JSON `.json` | Lista de objetos com valores originais; útil para integração e processamento |
| Excel `.xlsx` | Planilha `Leads`, filtros, cabeçalho fixo e formatação |
| Word `.docx` | Relatório com título, data, total e seção por lead |

Todos incluem `name`, `category`, `location`, `website`, `phone`, `social_profiles`, `score`, `status` e `created_at`. A data é serializada em formato ISO. Listas de redes sociais aparecem como JSON no CSV e Excel; o JSON preserva a estrutura da lista.

O CSV prefixa determinados textos com apóstrofo para evitar interpretação como fórmula. Isso pode afetar a aparência de telefones começando com `+`. O Excel força strings como texto, inclusive valores começando com `=`.

O Word identifica o campo como `Social profiles` no código original. Para usar `Instagram`, aplique a alteração do rótulo discutida na integração. Ausências são exibidas como `Not informed`.

Excel requer `openpyxl`; Word requer `python-docx`. A exportação não elimina duplicatas, não seleciona apenas um grupo e não atualiza o banco. PDF não foi implementado nos códigos apresentados. Se houver erro durante a escrita, confira o destino: não existe garantia de gravação atômica na implementação apresentada.

## Configuração e organização

### Parâmetros do input

Os trechos de prospecção usam um objeto `system` com estas chaves:

| Chave | Uso |
| --- | --- |
| `bounding_box` | Texto sugerido para as coordenadas |
| `parts` | Quantidade de faixas no modo paralelo |
| `threads` | Limite de workers no modo paralelo |

A origem desse objeto e o arquivo que o armazena não estão disponíveis no ZIP. Não altere um arquivo de configuração presumido sem conferir onde `system` é carregado.

Na API Python da descoberta, `search_businesses()` utiliza por padrão `parts=2` e `max_workers=2`; a interface pode substituir esses valores.

### Módulo de descoberta

| Arquivo | Responsabilidade |
| --- | --- |
| `core/lead/discovery/catalog.py` | Carregar catálogo e buscar/selecionar categorias |
| `core/lead/discovery/categories.json` | Catálogo de categorias |
| `core/lead/discovery/geography.py` | Validar coordenadas e dividir o retângulo |
| `core/lead/discovery/query.py` | Montar consulta Overpass |
| `core/lead/discovery/transport.py` | Requisições, tentativas e interpretação da resposta |
| `core/lead/discovery/mapping.py` | Reunir objetos OSM e criar leads |
| `core/lead/discovery/service.py` | Coordenar buscas e workers |
| `core/lead/discovery/search.py` | Exportar a interface pública |

O transporte depende de `network.connection.request`, que deve aceitar os argumentos utilizados, retornar `httpx.Response` e ser seguro para chamadas simultâneas. A criação depende de `core.models.lead_model.Lead`. Banco e telas ficam fora desse pacote.

### Catálogo de categorias

Cada entrada possui ID, rótulo, grupo, palavras-chave e filtros OSM. Exemplo presente no catálogo:

```json
{
  "id": "shop:bicycle",
  "label": "Bicicletarias",
  "group": "Comércio",
  "keywords": ["bicicleta bike"],
  "filters": [{"key": "shop", "value": "bicycle"}]
}
```

Os filtros de uma categoria são alternativas: basta uma correspondência de chave e valor. Eles não formam uma condição em que todas as tags precisam estar presentes. Preserve JSON válido, IDs únicos e filtros preenchidos. O catálogo é localizado ao lado de `catalog.py`; substituí-lo altera as opções de descoberta.

### Rede

O módulo fornecido consulta `https://overpass-api.de/api/interpreter`. Faz até três tentativas por consulta em erros de rede e nos HTTP 429, 502, 503 e 504. Esperas entre tentativas são de 10 e 20 segundos, podendo ser maiores quando o servidor informa `Retry-After`.

O timeout HTTP é configurado com 60 segundos e 10 segundos para conexão. A consulta Overpass declara 30 segundos de timeout no servidor. Esses valores não representam um limite único para a duração total, pois há tentativas, esperas e tarefas paralelas.

Se uma região falhar, o serviço lança erro; não retorna silenciosamente apenas as regiões bem-sucedidas. Tarefas pendentes são canceladas quando possível, mas as já executando podem terminar antes do encerramento do pool.

### Banco e cópia de segurança

O armazenamento utiliza SQLite nas telas apresentadas. Instagram deve ser salvo como JSON em `social_profiles` e reconstruído como lista ao carregar o lead. Exportar não modifica esse conteúdo.

O caminho exato do banco depende do módulo de conexão não fornecido. Para uma cópia completa, identifique o arquivo usado pela aplicação e faça backup com a ferramenta encerrada; se usar WAL, prefira a API de backup do SQLite para copiar um banco em uso. Exportações não substituem necessariamente o backup do banco, pois não preservam toda a estrutura e configuração.

## Problemas comuns

| Situação | O que conferir |
| --- | --- |
| Nenhuma empresa encontrada | Coordenadas, tamanho da área, categorias e disponibilidade de cadastro no OSM |
| Cidade exibida parece incorreta | Cidade/estado são rótulos digitados; confira o bbox |
| Busca demora | Área, quantidade de categorias, tentativas e carga da Overpass |
| HTTP 429 ou 503 | Servidor ocupado ou limitando consultas; aguarde e reduza área/concor­rência |
| `No leads found yet` | Não há registros retornados pelo banco consultado |
| Nenhum resultado após filtros | Use `Clear filters` e teste critérios separadamente |
| Telefone não entra no filtro de nove dígitos | Formato salvo, DDD, prefixos, ramais e separadores |
| Instagram aparece como `Not informed` | Lista vazia, tags ausentes ou integração ainda não aplicada |
| Linha de Instagram não aparece | Confira se a tela utiliza o `show_lead()` atualizado |
| Lead antigo sem Instagram | Atualizar a coleta não preenche registros antigos automaticamente |
| `ModuleNotFoundError` | Ambiente virtual, dependências e execução a partir da raiz |
| Categoria desconhecida | ID utilizado não existe no catálogo carregado |
| Falha ao exportar | Extensão, permissões, destino e arquivo aberto em outro programa |
| Dependência de exportação ausente | Instale `openpyxl` e/ou `python-docx` no ambiente que executa a ferramenta |

## Limitações

- A ferramenta consulta o cadastro disponível no OpenStreetMap; não representa todas as empresas existentes.
- Contatos e nomes podem estar incompletos ou desatualizados.
- Ausência de site no resultado é um indício de cadastro incompleto, não prova de ausência de presença digital.
- Instagram é coletado de tags na integração apresentada, sem descoberta externa ou confirmação do perfil.
- Os filtros restringem a visualização, mas não removem registros nem alteram a exportação.
- A pesquisa com autocomplete carrega a lista completa em memória.
- A deduplicação da descoberta ocorre por objeto OSM dentro de uma busca; não garante unicidade comercial.
- Os trechos apresentados não implementam envio de mensagens, validação de WhatsApp, geração de propostas, cálculo comercial de score ou exportação PDF.

Antes de usar um contato em uma proposta, confira se ele pertence ao estabelecimento e se as informações ainda estão atuais.
