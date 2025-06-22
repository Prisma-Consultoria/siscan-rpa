# RPA SISCAN

Este projeto implementa uma automação (RPA) para interação com o sistema SIScan utilizando Playwright e FastAPI.

## Estrutura do projeto

- **run.py** – ponto de entrada que carrega variáveis de ambiente e executa o servidor FastAPI via Uvicorn.
- **src/main.py** – inicializa a aplicação FastAPI e registra as rotas.
- **src/routes.py** – define os endpoints da API:
  - `/cadastrar-usuario` – cadastro de usuários com senha criptografada em SQLite.
  - `/preencher-solicitacao-mamografia` – inicia o RPA para preencher uma solicitação de exame.
  - `/preencher-laudo-mamografia` – inicia o RPA para preencher um laudo de mamografia.
  Utiliza Playwright para abrir o navegador e ainda possui *TODOs* de implementação.
- **src/scrapping.py** – script de exemplo que executa o fluxo de requisição de mamografia diretamente.
- **src/siscan/** – código principal de automação:
  - `context.py` controla o navegador e coleta mensagens informativas.
  - `siscan_webpage.py` define lógica comum de login e navegação.
  - `requisicao_exame.py` abstrai o preenchimento do formulário de exame.
  - `requisicao_exame_mamografia.py` especializa o fluxo para mamografia.
  - `webtools/` e `utils/` contêm classes de apoio (XPathConstructor, validação de esquemas, etc.).
  - `schemas/` guarda arquivos JSON Schema para validação dos dados.
- **tests/** – casos de teste em pytest para os endpoints da API.

## Gerar chaves RSA

Necessário pra serviço de criptografia de senhas do banco de dados.

```bash
openssl genpkey -algorithm RSA -out rsa_private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in rsa_private_key.pem -out rsa_public_key.pem
```

## Variáveis de ambiente


```bash
cp .env.example .env
```

## Executando

Para rodar localmente:

```bash
conda create -n siscan python=3.11
conda activate siscan
python run.py
```

Ou com Docker Compose:

```bash
docker compose up -d --build
```

Para rodar apenas o teste de scrapping

```bash
pytest # Gera o json teste faker dentre os testes, necessário para
python -m src.scrapping # rodar o scrapping
```

## Rodando testes

```bash
pytest
```