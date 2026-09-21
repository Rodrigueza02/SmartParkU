#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
#  SmartParkU — Script de instalación para EC2 Amazon Linux 2023 / Ubuntu
#  Ejecutar como: bash install.sh
# ═══════════════════════════════════════════════════════════════════════════════
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SmartParkU - Instalación en EC2"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Detectar SO ───────────────────────────────────────────────────────────────
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS="unknown"
fi

echo "▶ Sistema operativo detectado: $OS"

# ── Instalar Docker ───────────────────────────────────────────────────────────
echo "▶ Instalando Docker..."
if [ "$OS" = "amzn" ]; then
    # Amazon Linux 2023
    sudo dnf update -y
    sudo dnf install -y docker git python3
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ec2-user
elif [ "$OS" = "ubuntu" ]; then
    # Ubuntu
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg git python3
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
fi

# ── Instalar Docker Compose ───────────────────────────────────────────────────
echo "▶ Instalando Docker Compose..."
DOCKER_COMPOSE_VERSION="2.27.0"
sudo curl -SL "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64" \
    -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "▶ Verificando instalaciones..."
docker --version
docker-compose --version

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Docker instalado correctamente"
echo ""
echo "  PRÓXIMO PASO: cerrar sesión SSH y volver a entrar para"
echo "  que el grupo docker tenga efecto, luego ejecutar:"
echo ""
echo "     bash deploy.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
