# Relatório de Segurança e Infraestrutura - VM2 (Portal Administrativo)
**Projeto:** Telemetria IoT Resiliente (Maricá)
**Autor:** Daniel
**Ambiente:** Oracle Cloud Infrastructure (Ubuntu Server) / Docker Containers

---

## 📌 Sumário Executivo
Este documento detalha a arquitetura de segurança da Máquina Virtual 2 (VM2), responsável pela camada relacional, painel administrativo (Django) e persistência de metadados (PostgreSQL). A segurança deste nó baseia-se num modelo de **Defesa em Profundidade (Defense in Depth)**, utilizando isolamento por contêineres (Docker), blindagem de proxy reverso (Nginx) e políticas rigorosas de aplicação.

---

## 🛡️ 1. Proteções e Mitigações Ativas (Infraestrutura e Rede)

### 1.1. Isolamento de Rede via Docker (Containerization)
A aplicação não roda diretamente no sistema operativo hospedeiro.
* **Banco de Dados Blindado:** O PostgreSQL 16 opera numa rede interna isolada do Docker (`portal_network`). A porta `5432` não está mapeada para a interface pública do servidor, tornando varreduras de porta (*port scanning*) externas ineficazes.
* **Application Server Oculto:** O Gunicorn (servidor WSGI) roda internamente na porta `8000`, aceitando ligações exclusivamente do `localhost` (127.0.0.1) redirecionadas pelo Nginx.

### 1.2. Proxy Reverso e Criptografia (Nginx + Let's Encrypt)
O Nginx atua como a única porta de entrada para a aplicação web, gerindo o tráfego antes de este atingir o Python.
* **Terminação TLS/SSL:** Todo o tráfego HTTP (porta 80) é forçosamente redirecionado (Código 301) para HTTPS (porta 443). Os certificados são geridos e auto-renovados via Let's Encrypt.
* **Rate Limiting (Proteção Anti-Brute Force):** Implementação de limites rigorosos de requisição na rota crítica `/admin/login/` (`limit_req zone=login_limit burst=5`). Se um atacante tentar automatizar tentativas de senha, o Nginx bloqueia o IP instantaneamente na sexta tentativa por minuto.

### 1.3. Cabeçalhos de Segurança HTTP (HSTS & Anti-Sniffing)
O Nginx injeta cabeçalhos de segurança padronizados pela indústria em todas as respostas:
* `Strict-Transport-Security (HSTS)`: Força navegadores a utilizarem apenas conexões seguras por 1 ano.
* `X-Frame-Options: SAMEORIGIN`: Previne ataques de *Clickjacking*, impedindo que o portal seja embutido em *iframes* de sites maliciosos.
* `X-Content-Type-Options: nosniff`: Evita ataques de confusão de tipo MIME.

---

## 🔒 2. Segurança a Nível de Aplicação (Django)

### 2.1. Gestão Criptográfica de Chaves IoT
A VM2 atua como a *Single Source of Truth* (Fonte Única de Verdade) para a rede IoT.
* **Alta Entropia:** Chaves dos sensores (`X-API-Key`) são geradas utilizando `secrets.token_urlsafe(48)`, criando tokens robustos contra ataques de dicionário.
* **Auditoria Imutável:** O modelo `SensorApiKeyAudit` regista todas as rotações e revogações de chaves. As permissões de adição, edição e exclusão estão desativadas no painel de administração, garantindo um log forense inviolável.

### 2.2. Proteção de Sessão e Cookies
O ambiente de produção (`settings_production.py`) impõe flags restritas aos cookies:
* `SESSION_COOKIE_SECURE = True` e `CSRF_COOKIE_SECURE = True`: Garantem que os tokens de autenticação de administradores nunca trafeguem em conexões não-criptografadas.

---

## ⚠️ 3. Vulnerabilidades Conhecidas e Riscos Residuais

Para manter a estabilidade a curto prazo (Feature Freeze) antes do lançamento da Prova de Conceito, algumas camadas de segurança do Sistema Operativo (Host) foram temporariamente desativadas.

1. **Firewall do Sistema Operativo (UFW) Inativa:**
   * **Risco:** O sistema confia integralmente nas Ingress Rules da Oracle Cloud para bloqueio de portas.
   * **Justificativa Arquitetural:** O Docker manipula ativamente as regras de `iptables` do Linux. Ativar o UFW sem uma configuração avançada de roteamento frequentemente quebra a comunicação entre contêineres e a internet.
2. **Ausência de IPS a Nível de Host (Fail2ban):**
   * **Risco:** Ao contrário da VM1, a VM2 não tem o Fail2ban instalado para monitorizar os logs do SSH (porta 22) e banir bots que tentem acesso remoto ao servidor.

---

## 🚀 4. Trabalhos Futuros e Roadmap de Segurança

Para a evolução do sistema para um ambiente de Produção *Enterprise* definitivo, as seguintes correções estão planeadas:

* **Integração Docker-UFW:** Implementar o script `ufw-docker` para permitir que a firewall do Ubuntu filtre o tráfego bloqueando tentativas de acesso direto ao Docker, sem corromper as redes internas dos contêineres.
* **Instalação do Fail2ban no Host:** Ativar a monitorização da porta 22 (SSH) para banir proativamente IPs maliciosos que realizem *port scanning* na VM2.
* **Implementação de WAF (Web Application Firewall):** Interpor um serviço como Cloudflare na frente do Nginx para filtrar ataques de injeção de SQL (SQLi), Cross-Site Scripting (XSS) e DDoS volumétricos antes mesmo de o pacote chegar à Oracle Cloud.
* **Rotinas de Backup Off-site:** Criação de *cronjobs* para despejo (`pg_dump`) do PostgreSQL e envio automatizado e criptografado para um *bucket* S3 externo, garantindo resiliência em caso de perda total do servidor.