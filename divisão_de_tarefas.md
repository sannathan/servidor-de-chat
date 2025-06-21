
---

# ✅ 2. Divisão das Tarefas para 3 Pessoas  

| Pessoa        | Tarefa                                                                                                          | Descrição                                                                                          |
|----------------|----------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| **Pessoa 1**  | 📦 Infraestrutura do Servidor                                                                                  | - Criar `servidor.py`.<br>- Implementar socket UDP, receber pacotes, reconstruir arquivos e retransmitir.<br>- Implementar formatação das mensagens.<br>- Notificar entradas e saídas. |
| **Pessoa 2**  | 💻 Cliente - Envio de Mensagens                                                                                | - Criar `cliente.py`.<br>- Implementar socket UDP para envio.<br>- Implementar conversão de mensagens para `.txt`.<br>- Fragmentar arquivos e enviar ao servidor.                   |
| **Pessoa 3**  | 🔊 Cliente - Recepção de Mensagens + Threading + README                                                        | - Criar a parte do cliente responsável por escutar mensagens do servidor.<br>- Implementar threading para envio e recepção simultânea.<br>- Documentar (`README.md`).               |

### ✔️ Sugestão de Workflow
- Pessoa 1 e Pessoa 2 podem começar em paralelo (servidor e envio do cliente).  
- Pessoa 3 entra logo depois que a comunicação básica servidor-cliente funciona, para implementar a recepção e threading.  

---

