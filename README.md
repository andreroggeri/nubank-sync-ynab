# nubank-sync-ynab
Sincronize seus gastos do Nubank com o YNAB

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Como utilizar
1. Clique no botão "Deploy to Heroku" disponível no topo deste documento
2. Faça login no Heroku
3. Preencha as infomações solicitadas
4. Clique em Deploy
5. Configure o Scheduler para sincronizar diariamente:
- Abra seu App no Heroku
- Vá na aba resources
- Clique em Heroku Scheduler
- "Add new job"
- `$ sync`
- Preecha o campo "NEXT DUE" com o horário desejado para que o sync seja executado
6. DONE ! Agora o YNAB irá sincronizar diariamente com os seus gastos do Nubank gratuitamente 🤑


## Como funciona

Este app utiliza o [pynubank](https://github.com/andreroggeri/pynubank) e o [pynYNAB](https://github.com/rienafairefr/pynYNAB) 
para sincronizar as informações entre os sistemas.

Durante o sync, a ferramenta irá tentar utilizar as categorias do Nubank para categorizar o gasto no nYNAB.
Para que isso funcione corretamente, você precisa ter cadastrado as categorias do Nubank (Transporte, Restaurante, Mercado, etc...)
 no nYNAB. Caso contrário as transações serão importadas sem categoria.

O Heroku é utilizado para executar o script `sync.py` diariamente de maneira automática.

Caso você deseje utilizar alguma outra solução para executar o sync, basta clonar esse repositório, instalar o `requirements.txt`
configurar as variáveis de ambiente e executar o arquivo `sync.py` da maneira de quiser (Manualmente, cronjobs, etc...)


## Variáveis de Ambiente

As credenciais são configuradas por variáveis de ambiente. São elas:

- **YNAB_EMAIL**: Email utilizado no login do nYNAB 
- **YNAB_PASSWORD**: Senha utilizada no login do nYNAB
- **YNAB_BUDGET**: Nome do seu orçamento
- **NUBANK_LOGIN**: Seu CPF cadastrado no Nubank (Sem pontos ou traços)
- **NUBANK_PASSWORD**: Sua senha do Nubank (A mesma que você utiliza ao acessar o site, **não é a senha do cartão**)
- **STARTING_POINT**: Data que será considerada para importar os dados do Nubank para o nYNAB,
todas as transações anteriores a essa data serão ignoradas. Idealmente essa data deve ser a data da 
ultima transação que você cadastrou no nYNAB, isso serve para que o App não duplique as transações que você já importou. 

## Contribua

Se você tem alguma idéia para melhorar esse app, abra sua PR e contribua para esse projeto !