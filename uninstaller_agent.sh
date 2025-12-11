#!/bin/bash

set -e

echo "==========================================================="
echo "  UNINSTALLER: Node Exporter, Prometheus, Promtail & Loki"
echo "==========================================================="
sleep 1

###################################
# REMOVE NODE EXPORTER
###################################
remove_node_exporter() {
  echo "[1/4] Removing Node Exporter..."

  systemctl stop node_exporter 2>/dev/null || true
  systemctl disable node_exporter 2>/dev/null || true
  rm -f /etc/systemd/system/node_exporter.service
  systemctl daemon-reload

  rm -f /usr/local/bin/node_exporter
  userdel node_exporter 2>/dev/null || true

  echo "Node Exporter removed."
}

remove_prometheus(){

  echo "[2/4] Removing Prometheus...."

  systemctl stop prometheus 2>/dev/null || true
  systemctl disable promtheus 2>/dev/null || true
  rm -f /etc/systemd/system/prometheus.service
  systemctl daemon-reload

  rm -f /usr/local/bin/promtheus
  rm -rf /etc/prometheus
  rm -rf /var/lib/prometheus
  userdel prometheus 2>/dev/null || true

  echo "Prometheus removed..."
}

###################################
# REMOVE LOKI
###################################
remove_loki() {
  echo "[3/4] Removing Loki..."

  systemctl stop loki 2>/dev/null || true
  systemctl disable loki 2>/dev/null || true
  rm -f /etc/systemd/system/loki.service
  systemctl daemon-reload

  rm -f /usr/local/bin/loki
  rm -rf /etc/loki
  rm -rf /var/lib/loki
  userdel loki 2>/dev/null || true

  echo "Loki removed."
}

###################################
# REMOVE PROMTAIL
###################################
remove_promtail() {
  echo "[4/4] Removing Promtail..."

  systemctl stop promtail 2>/dev/null || true
  systemctl disable promtail 2>/dev/null || true
  rm -f /etc/systemd/system/promtail.service
  systemctl daemon-reload

  rm -f /usr/local/bin/promtail
  rm -rf /etc/promtail
  rm -f /var/log/positions.yaml
  userdel promtail 2>/dev/null || true

  echo "Promtail removed."
}

###################################
# MENU UNINSTALLER
###################################

echo ""
echo "Pilih agent yang ingin di-uninstall:"
echo "1) Remove Node Exporter"
echo "2) Remove Prometheus"
echo "3) Remove Loki"
echo "4) Remove Promtail"
echo "5) Remove Semua"
echo "6) Exit"
echo ""

read -p "Masukkan pilihan [1-6]: " CHOICE

case $CHOICE in
  1) remove_node_exporter ;;
  2) remove_prometheus ;;
  3) remove_loki ;;
  4) remove_promtail ;;
  5) remove_node_exporter; remove_prometheus; remove_loki; remove_promtail ;;
  6) exit 0 ;;
  *) echo "Input tidak valid!"; exit 1 ;;
esac

echo "==============================================="
echo " UNINSTALL COMPLETE!"
echo "==============================================="
