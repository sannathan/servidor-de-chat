# 🛰️ Projeto de Redes - Etapa 1  
**Disciplina:** IF975 - Redes de Computadores — 2025.1  
**Tema:** Chat UDP com transmissão de arquivos `.txt` com fragmentação.  

---

## 📑 Descrição  
Este projeto consiste na implementação de um **chat UDP de sala única**, onde as mensagens são enviadas na forma de arquivos `.txt` que são fragmentados em pacotes de até 1024 bytes. O servidor recebe esses arquivos, lê seus conteúdos e retransmite como mensagens no terminal para todos os clientes conectados.

---

## 🚀 Funcionalidades  
- ✅ Comunicação UDP entre servidor e múltiplos clientes.  
- ✅ Envio de mensagens na forma de arquivos `.txt`.  
- ✅ Fragmentação de arquivos em pacotes de 1024 bytes.  
- ✅ Reconstrução dos arquivos no servidor e nos clientes.  
- ✅ Exibição das mensagens no seguinte formato:  

<IP>:<PORTA>/~<nome_usuario>: <mensagem> <hora-data>


- ✅ Notificação quando um usuário entra ou sai da sala.  
- ✅ Comandos básicos via terminal.  

---

## 🛠️ Tecnologias  
- 🐍 Python 3 (bibliotecas padrão):  
  - socket  
  - threading  
  - os  
  - datetime  
  - uuid  
  - json  

---

## 🗂️ Estrutura do Projeto  

servidor-de-chat/
├── cliente.py
├── servidor.py
├── arquivos/ # Arquivos .txt temporários
├── README.md # Documentação
└── requirements.txt # (Vazio - usamos só libs padrão)


---

## 💻 Comandos Disponíveis  

| Comando                           | Descrição                  |
| ---------------------------------- | -------------------------- |
| hi, meu nome eh `<nome>`          | Conecta o cliente à sala   |
| bye                               | Sai da sala                |
| `<mensagem>`                      | Envia uma mensagem         |

---

## ⚙️ Como Executar  

### ✔️ 1. Pré-requisitos  
- Python 3 instalado.  

### ✔️ 2. Clonar o repositório  
```bash
git clone https://github.com/sannathan/servidor-de-chat.git
cd servidor-de-chat
```
### ✔️ 3. Executar o servidor
```bash
python3 servidor.py
```
### ✔️ 4. Executar os clientes (em diferentes terminais)
```bash
python3 cliente.py
```
### ✔️ 5. Interagir no chat
Use o comando hi, meu nome eh <nome> para entrar.

Digite qualquer mensagem para enviar.

Use bye para sair da sala.

## 🏗️ Detalhes Técnicos
Buffer de 1024 bytes por pacote.

Fragmentação de arquivos .txt com cabeçalhos que indicam:

    ID do arquivo

    Número do pacote

    Total de pacotes

Reconstrução automática dos arquivos no servidor e nos clientes.

Threading para escutar mensagens e enviar mensagens simultaneamente.

## 🎯 Formato das Mensagens no Terminal
```ruby
<IP>:<PORTA>/~<nome_usuario>: <mensagem> <hora-data>
```
*Exemplo*
```
192.168.0.123:67890/~renato: Nosso estoque de comida está acabando. 14:31:26 03/02/2023
```

## 👥 Equipe
Nathan Barbosa

Integrante 2

Integrante 3

## 📜 Licença
Uso educacional para a disciplina de Redes de Computadores - CIN/UFPE.
