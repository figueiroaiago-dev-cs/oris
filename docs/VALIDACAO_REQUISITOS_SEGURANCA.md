# Validação dos requisitos de segurança e auditoria (Entrega 11)

Responsável: Iago Figueirôa Soares. Fontes: "Requisitos de segurança" (21 requisitos), slides SR1 de Governança e Auditoria (Humberto) e `docs/ORIS_Requisitos_do_Professor.pdf`.
Detalhe de cada achado: `docs/SEGURANCA.md` (SEC-016 a SEC-022).

## Situação por tema

| Tema | Situação | Evidência |
|---|---|---|
| Autenticação OIDC (assinatura, `exp`, `iat`, `iss`, `aud`, `nonce`, PKCE) | **Atende** (testado com provedor simulado) | `app/services/oidc_service.py`, `tests/test_oidc_assinatura.py` (12 testes) |
| Audit trail: quem, o quê, quando, **de onde (IP)** e **resultado**, incluindo login falho | **Atende** (IP é o da requisição; atrás de proxy/Docker mostra o do proxy) | `tests/test_auditoria_origem_resultado.py`, SEC-021 |
| Trilha de auditoria imutável | **Atende com limite** (TRUNCATE/DROP não disparam trigger; restringir privilégios do usuário do banco) | `database/etapa05_objetos.sql`, `tests/test_auditoria_imutavel.py` |
| Integridade com hash (SHA-256) | **Atende em parte** (verificação ativa só no upload ao S3; na importação o hash é só evidência) | `app/utils/integridade.py`, `tests/test_integridade_sha256.py` |
| Criptografia de arquivos exportados (S3) | **Atende** no código (SSE-S3 AES256, URL pré-assinada) | `app/services/armazenamento_service.py` |
| Senhas, CSRF, RBAC, rate limit | **Atende** (já existente) | `docs/SEGURANCA.md` |
| MFA | **Não atende** | SEC-019, pendente (SR2) |
| HTTPS/HSTS/redirecionamento | **Não atende** (depende do deploy) | SEC-020 |
| Retenção de 1 ano | **Política documentada** (a aplicação nunca apaga; expurgo é do DBA) | `docs/SEGURANCA.md` |
| Criptografia em repouso do MySQL | **Fora da aplicação** (ambiente de hospedagem) | SEC-022 |

## O que ainda não foi validado

- LDAP, OIDC e S3 contra servidores **reais**: os testes usam simulações.
- Triggers testados em MariaDB 10.6; falta rodar em MySQL 8 (`ORIS_TEST_MYSQL=1 pytest tests/test_auditoria_imutavel.py`).
- Feedback de usuários reais: ainda não coletado; só há o retorno de um colega do grupo.
- Itens de SR2 (CNES, backup testado, hospedagem) ainda não tratados.
