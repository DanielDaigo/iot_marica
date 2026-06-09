# IoT Maricá - Plataforma de Telemetria

Uma plataforma robusta para monitoramento de sensores IoT em tempo real, construída com **Django**, **PostgreSQL** e **InfluxDB**. O sistema conta com um Dashboard interativo e um Painel de Administração altamente customizado, focado em alta usabilidade, segurança e estética premium.

## 🚀 Tecnologias e Stack

- **Backend:** Django (Python)
- **Banco de Dados Relacional:** PostgreSQL (via Docker) ou SQLite (local)
- **Série Temporal (Time-Series):** InfluxDB (Hospedado em uma VM Oracle Cloud)
- **Frontend / Dashboard:** Tailwind CSS, Chart.js, HTML5 e JavaScript (AJAX/Fetch API).
- **Painel de Administração:** Django-Unfold (Tema avançado para Django Admin).
- **Infraestrutura:** Docker & Docker Compose.

---

## 🌟 Principais Funcionalidades

### 1. Dashboard de Monitoramento (Tempo Real)
- **Estética Premium:** Interface rica utilizando efeitos de *Glassmorphism* (fundo de vidro translúcido), tipografia moderna (fonte *Inter*), e gradientes fluídos de renderização nativa (Canvas do Chart.js).
- **Atualização Sem "Flicker" (AJAX):** O front-end consulta os dados a cada 5 segundos através de requisições JSON invisíveis. Os medidores (Gauges) e os gráficos de linha se atualizam de forma sedosa, sem forçar um incômodo recarregamento total da página.
- **Medidores Inteligentes:** Exibição precisa de Temperatura e Umidade Relativa atuais com cálculo de valores Máximos e Mínimos.
- **Séries Temporais:** Análise do histórico térmico baseado em queries avançadas no InfluxDB agrupadas por tempo (`GROUP BY time()`).

### 2. Painel de Administração (Admin Panel)
- **Experiência de Uso Aprimorada (UX):** Painel alimentado pela biblioteca `django-unfold`.
- **Botões Dinâmicos de Ação:** O painel conta com atalhos injetados diretamente na tela de detalhes do Sensor, permitindo **"↻ Girar Chave"** ou **"⚠ Revogar Chave"** de API com apenas um clique.
- **Indicadores Visuais (Badges):** Um selo permanente no topo avisa se a aplicação está rodando em ambiente de **Desenvolvimento** ou **Produção**, prevenindo desastres operacionais. Na listagem, os status operacionais (*is_active*) ganham *badges* coloridos (Verde para Ativo, Vermelho para Inativo).
- **Organização Clara (Fieldsets & Sidebar):** Menu lateral elegantemente organizado por categorias e ícones (Material Symbols). Formulários pesados divididos em seções visuais limpas (Identificação, Hardware e Local, Segurança e API).
- **Segurança (Audit Trail):** Registro rígido das alterações críticas (Geração e Revogação de Chaves), mantendo histórico inalterável do quem fez e quando.

---

## ⚙️ Pré-requisitos

Para rodar o projeto, você precisará ter em sua máquina:
- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) instalados **(Recomendado)**.
- *Ou* Python 3.10+ para rodar nativamente através do seu ambiente virtual (`venv`).

---

## 🛠️ Como executar o projeto localmente

### Método 1: Usando Docker (Recomendado)
Este método garante que a sua máquina local espelhe da forma mais idêntica possível as dependências de Produção.

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd iot_marica
   ```

2. **Configure as variáveis de ambiente:**
   Copie o arquivo de exemplo para gerar o seu arquivo oculto `.env`.
   ```bash
   cp .env.example .env
   ```
   *(Caso queira conectar ao InfluxDB real para ter gráficos preenchidos com dados reais, insira as credenciais no bloco final do `.env`).*

3. **Suba a infraestrutura de containers:**
   ```bash
   docker-compose up --build
   ```

4. **Crie seu usuário Administrador:**
   Em um outro terminal paralelo (ou parando o servidor com `Ctrl+C` e voltando a subir com a tag `-d`), execute:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
   *Responda as perguntas no terminal com usuário, email e senha.*

5. **Acesse a Plataforma:**
   - **Dashboard Inicial:** [http://localhost:8000](http://localhost:8000)
   - **Painel de Admin:** [http://localhost:8000/admin](http://localhost:8000/admin) (Autentique-se com os dados do passo 4).

### Método 2: Ambiente Local Nativo (Python + SQLite)
Se você não deseja instalar o Docker, é possível rodar o Django diretamente via Python.

1. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   
   # No Windows:
   .\venv\Scripts\activate
   
   # No Linux/Mac:
   source venv/bin/activate
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuração de Variáveis (`.env`):**
   ```env
   DATABASE_URL=sqlite:///db.sqlite3
   DJANGO_DEBUG=True
   # Insira aqui os dados do InfluxDB localizados no seu .env.example
   ```

4. **Prepare o Banco de Dados Relacional:**
   ```bash
   python manage.py migrate
   ```

5. **Crie o Super Usuário:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Inicie o Servidor:**
   ```bash
   python manage.py runserver
   ```

---

## 🔌 Arquitetura de Comunicação (Hardwares -> Aplicação)

1. **Ingestão de Dados:** O microcontrolador responsável pela leitura local (ex: um ESP32) envia regularmente os parâmetros lidos para a nuvem.
2. **Armazenamento Temporal:** Esses parâmetros (série temporal) caem diretamente dentro da base do **InfluxDB**, que está provisionado remotamente em uma VM na nuvem da Oracle. O InfluxDB é uma base projetada exatamente para gravar eventos por segundo em altíssima velocidade.
3. **Plataforma Web (Dashboard):** O Django, por sua vez, age como visualizador e ponte. Ele consulta o InfluxDB para varrer a base de dados em tempo real, agrupar essas dezenas de marcações por hora e despejá-las filtradas para os gráficos (Chart.js) no Front-end de forma mastigada.
4. **Relacional:** As senhas de autenticação de API, regras de bloqueio, usuários e o cadastro do parque de equipamentos em si (nomes e tipos) ficam blindados no **PostgreSQL** ou no **SQLite**.

---
*Documentação gerada após refatoração completa de UX/UI.*
