
# 🛰️ Projeto de Redes - Etapa 2  
**Disciplina:** IF975 - Redes de Computadores — 2025.1  
**Tema:** Chat UDP com transmissão confiável via RDT 3.0 e fragmentação de arquivos `.txt`.  

---

## 📑 Descrição  
Esta segunda etapa do projeto expande o sistema de chat UDP com múltiplos clientes para suportar **transmissão confiável** por meio da implementação do protocolo **RDT 3.0** (Reliable Data Transfer), conforme descrito no livro de Kurose e Ross.

Cada mensagem é enviada como um arquivo `.txt`, **fragmentado em pacotes de até 1024 bytes**. O protocolo RDT 3.0 garante a entrega confiável desses pacotes através do uso de **ACKs**, **números de sequência**, **timeouts** e **retransmissões**, mesmo sobre o protocolo UDP, que não é confiável por natureza.

---

## 🚀 Funcionalidades  
- ✅ Comunicação UDP entre servidor e múltiplos clientes.  
- ✅ Envio de mensagens na forma de arquivos `.txt`.  
- ✅ Fragmentação de arquivos em pacotes de 1024 bytes.  
- ✅ Reconstrução dos arquivos no servidor e nos clientes.  
- ✅ Implementação do protocolo RDT 3.0:  
- ✅ Checksum (verificação de integridade)  
- ✅ ACKs (confirmações de recebimento)  
- ✅ Timeouts e retransmissões  
- ✅ Controle por número de sequência  
- ✅ Exibição das mensagens no terminal com metadados:  
  ```
  <IP>:<PORTA>/~<nome_usuario>: <mensagem> <hora-data>
  ```
- ✅ Suporte a comandos básicos de entrada e saída.  

---

## 🛠️ Tecnologias  
- 🐍 Python 3 (bibliotecas padrão):  
  - socket  
  - threading  
  - os  
  - datetime  
  - uuid  
  - json  
  - hashlib  
  - random  

---

## 📁 Estrutura do Projeto  
```
servidor-de-chat/
├── cliente.py               # Cliente com envio confiável (RDT 3.0)
├── servidor.py              # Servidor que escuta e retransmite mensagens
├── protocolrdt3.py          # Implementação do protocolo RDT 3.0
├── arquivos/                # Arquivos .txt temporários
├── README.md                # Documentação da segunda entrega
└── requirements.txt         # (Vazio - só libs padrão)
```

---

## 💻 Comandos Disponíveis  

| Comando                           | Descrição                  |
| --------------------------------- | -------------------------- |
| hi, meu nome eh `<nome>`         | Conecta o cliente à sala   |
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

### ✔️ 4. Executar os clientes (em terminais separados)  
```bash
python3 cliente.py
```

### ✔️ 5. Interagir no chat  
Use `hi, meu nome eh <nome>` para entrar.  
Digite qualquer mensagem para enviar.  
Use `bye` para sair da sala.

---

## 🔁 Como funciona o RDT 3.0 neste projeto  

### 📦 Formato dos pacotes (via `protocolrdt3.py`)
Cada pacote contém:
- Número de sequência (`seq_num`)  
- Dados (`data`)  
- Checksum (`checksum`) para verificação de integridade

### ✅ Funcionamento
- O cliente envia pacotes com controle de sequência.
- A cada pacote enviado, aguarda-se um ACK correspondente.
- Se um ACK incorreto ou nenhum ACK for recebido em até 2 segundos, o pacote é retransmitido.
- O servidor, ao receber, verifica se o pacote está corrompido e responde com um ACK válido.
- A mensagem é reconstruída ao final da recepção de todos os pacotes.

---

## 🧪 Simulação de Erros
A função `simulate_corruption` em `protocolrdt3.py` permite **simular perda ou corrupção de pacotes** com uma certa probabilidade, útil para testes de robustez do protocolo.

---

## 🎯 Exemplo de saída no terminal  
```bash
192.168.0.123:67890/~renato: Nosso estoque de comida está acabando. 14:31:26 03/02/2023
```

---

## 👥 Equipe  
- Nathan Barbosa  
- Igor Vasconcelos  


---

## 📜 Licença  
Uso educacional para a disciplina de Redes de Computadores - CIN/UFPE.
