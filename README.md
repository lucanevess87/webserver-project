# webserver-project

# Introdução

O projeto apresentado é um servidor web TCP capaz de efetuar o método GET do protocolo HTTP/1.1. A partir do uso de sockets, o cliente pode se conectar com nosso servidor que está ‘escutando’ na porta escolhida por nós (1111) os requests realizados pelos clients. Ao inicializar o servidor, como não houve requisições solicitando algum arquivo, ele retorna por padrão um HTML que tem como objetivo prover uma interface amigável para seleção dos arquivos disponíveis para solicitação. Clicando nos links, o usuário é direcionado para a visualização do arquivo, seja aparecendo na tela ou baixando no seu computador.
O código começa importando vários módulos e bibliotecas Python, incluindo o módulo socket, que fornece acesso às funcionalidades de rede do sistema operacional, e o módulo threading, que é usado para criar e gerenciar threads.
Este servidor web é capaz de lidar com vários tipos de erros HTTP, como 400 Bad Request, 403 Forbidden, 404 Not Found e 505 HTTP Version Not Supported. Ele também é capaz de fornecer uma interface amigável ao usuário para acessar os arquivos disponíveis.

## Como rodar
1. Clonar projeto.
2. Com o projeto aberto em sua IDE de preferência, você irá observar dois arquivos com terminação .txt, leia o arquivo “serverConfig.example.txt” e o tenha como guia para configurar o “serverConfig.txt”. O intuito desta etapa é colocar o seu path da pasta local e pasta errors (ambas já estão dentro do projeto) no devido lugar para que a aplicação consiga saber de onde puxar os arquivos necessários.
3. Agora é só rodar o projeto e abrir uma aba do navegador em “localhost:1111”. Desse modo, os arquivos já devem estar listados em sua tela e basta clicar em algum deles para testar.
