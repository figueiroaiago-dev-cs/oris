# ORIS na AWS (EC2 + Docker + HTTPS)

Arquitetura: internet -> **Caddy** (80/443, HTTPS Let's Encrypt, HSTS) -> **app** (gunicorn, só na rede interna) -> **MySQL 8** (só na rede interna, volume em disco EBS criptografado). O servidor usa o `LabInstanceProfile` para falar com o S3, sem chave de acesso em arquivo.

## Servidor (Ubuntu 24.04, t3.medium, IP elástico)

```bash
sudo apt-get update && sudo apt-get install -y git docker.io docker-compose-v2
sudo systemctl enable --now docker
git clone --branch iago-etapa11-seguranca https://github.com/figueiroaiago-dev-cs/oris.git
cd oris
```

## Segredos (`.env.aws`, nunca vai para o Git)

```bash
cat > .env.aws <<EOT
ORIS_DOMAIN=54-174-10-29.sslip.io
DB_PASSWORD=$(openssl rand -hex 16)
DB_ROOT_PASSWORD=$(openssl rand -hex 16)
SECRET_KEY=$(openssl rand -hex 32)
ORIS_DEMO_SENHA=<escolha uma senha forte para os usuários de demonstração>
EOT
chmod 600 .env.aws
```

## Subir

```bash
sudo docker compose -f docker-compose.aws.yml --env-file .env.aws up -d --build
sudo docker compose -f docker-compose.aws.yml ps
sudo docker compose -f docker-compose.aws.yml logs app | tail
```

Abrir `https://<ORIS_DOMAIN>`. A primeira emissão do certificado leva ~1 minuto e exige as portas 80 e 443 abertas no security group.

## Cuidados

- O **Learner Lab desliga o servidor** ao fim da sessão (~4 h). Ao religar, o IP elástico e os dados continuam; os contêineres sobem sozinhos (`restart: unless-stopped`).
- Os usuários `@oris.example` usam a senha de `ORIS_DEMO_SENHA`, nunca a do repositório.
- SSH aberto para o mundo (porta 22) é aceitável só durante o laboratório; restringir ao seu IP depois.

## Validação da implantação (10/11/2026)

- Contêineres `db` (healthy), `app` (healthy) e `caddy` em execução; certificado Let's Encrypt emitido.
- HTTPS com HSTS; senha pública dos usuários demo recusada; login falho registrado na auditoria.
- S3: bucket privado com versionamento e SSE-S3; exportação pelo ORIS gerou URL pré-assinada; acesso direto ao objeto retornou `AccessDenied`.
- Pendente: LDAP e OIDC reais; restringir o SSH; testar o religamento do servidor após o fim da sessão do laboratório.
