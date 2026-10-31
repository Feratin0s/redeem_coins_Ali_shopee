#!/usr/bin/env bash
# install-adb-service.sh
# Instala (ou atualiza) o serviço systemd "adb-server", que mantém o servidor
# ADB do host rodando na porta 5037. Pode ser executado várias vezes sem problema.
#
# Uso: sudo ./install-adb-service.sh

set -euo pipefail

SERVICE_NAME="adb-server"
UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
ADB_PORT="5037"

# --- Verificações ---------------------------------------------------------
if [[ $EUID -ne 0 ]]; then
  echo "Erro: execute com sudo ->  sudo $0" >&2
  exit 1
fi

if [[ -z "${SUDO_USER:-}" || "${SUDO_USER}" == "root" ]]; then
  echo "Erro: rode com sudo a partir do seu usuário normal (não como root direto)." >&2
  echo "A chave de autorização do celular fica em ~/.android do usuário." >&2
  exit 1
fi

ADB_BIN="$(command -v adb || true)"
if [[ -z "$ADB_BIN" ]]; then
  echo "Erro: 'adb' não encontrado. Instale com: sudo apt install adb" >&2
  exit 1
fi

if ! command -v systemctl >/dev/null 2>&1; then
  echo "Erro: systemd não encontrado neste sistema." >&2
  exit 1
fi

# --- Gera a unit e só substitui se mudou ----------------------------------
TMP_UNIT="$(mktemp)"
trap 'rm -f "$TMP_UNIT"' EXIT

cat > "$TMP_UNIT" <<EOF
[Unit]
Description=ADB server
After=network.target

[Service]
Type=simple
User=${SUDO_USER}
ExecStartPre=-${ADB_BIN} kill-server
ExecStart=${ADB_BIN} -a -P ${ADB_PORT} nodaemon server start
ExecStop=${ADB_BIN} kill-server
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

if [[ -f "$UNIT_PATH" ]] && cmp -s "$TMP_UNIT" "$UNIT_PATH"; then
  echo "Unit já está atualizada: $UNIT_PATH"
else
  install -m 644 "$TMP_UNIT" "$UNIT_PATH"
  systemctl daemon-reload
  echo "Unit instalada/atualizada: $UNIT_PATH"
fi

# --- Libera a porta ocupada por um adb avulso e sobe o serviço ------------
# (um "adb devices" solto cria um daemon que impede o -a de funcionar)
sudo -u "$SUDO_USER" "$ADB_BIN" kill-server >/dev/null 2>&1 || true

systemctl enable "${SERVICE_NAME}" >/dev/null 2>&1
systemctl restart "${SERVICE_NAME}"

sleep 2

if systemctl is-active --quiet "${SERVICE_NAME}"; then
  echo "Serviço '${SERVICE_NAME}' ativo."
else
  echo "Erro: o serviço não subiu. Veja: journalctl -u ${SERVICE_NAME} -n 50" >&2
  exit 1
fi

echo
echo "Dispositivos detectados:"
sudo -u "$SUDO_USER" "$ADB_BIN" devices

echo
echo "AVISO: o servidor ADB escuta em todas as interfaces (porta ${ADB_PORT})."
echo "Restrinja o acesso, por exemplo:"
echo "  sudo ufw allow from 172.16.0.0/12 to any port ${ADB_PORT} proto tcp"
echo "  sudo ufw deny ${ADB_PORT}/tcp"