#!/bin/bash
set -e

echo "=== EMMA BOT DEPLOY ==="
echo "Fecha: $(date)"

cd /root/emma

echo "Instalando dependencias..."
pip3 install -r requirements.txt --break-system-packages -q

echo "Creando directorios..."
mkdir -p logs data

echo "Instalando emma-bot.service..."
cp emma-bot.service /etc/systemd/system/emma-bot.service
systemctl daemon-reload
systemctl enable emma-bot

echo "Reiniciando emma-bot..."
systemctl restart emma-bot

sleep 3
systemctl status emma-bot --no-pager -l

echo ""
echo "=== DEPLOY COMPLETADO ==="
echo "Logs en vivo:  journalctl -u emma-bot -f"
echo "Status:        systemctl status emma-bot"
echo "Bot logs:      tail -f /root/emma/logs/bot.log"
