# 🚀 Guía Completa de Despliegue en AWS - SmartParkU

## 📋 Índice
1. [Prerequisitos](#prerequisitos)
2. [Arquitectura AWS](#arquitectura-aws)
3. [Paso a Paso](#paso-a-paso)
4. [Costos](#costos-estimados)
5. [Comparación con Azure](#comparación-azureaws)

---

## 📦 Prerequisitos

### 1. Cuenta de AWS
- Crear cuenta: https://aws.amazon.com/free/
- Incluye **free tier** por 12 meses
- Requiere tarjeta de crédito

### 2. Instalar AWS CLI
```powershell
# Descargar desde: https://aws.amazon.com/cli/

# Verificar instalación
aws --version

# Configurar credenciales
aws configure
# AWS Access Key ID: [tu-access-key]
# AWS Secret Access Key: [tu-secret-key]
# Default region: us-east-1
# Default output format: json
```

### 3. Instalar ECS CLI (Opcional pero útil)
```powershell
# Descargar desde: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_installation.html
```

---

## 🏗️ Arquitectura AWS

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  CloudFront (CDN) + Route 53 (DNS)             │
│                     │                           │
└─────────────────────┼───────────────────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
┌───────▼────────┐         ┌────────▼─────────┐
│                │         │                  │
│  ALB (Frontend)│         │  ALB (Backend)   │
│                │         │                  │
└───────┬────────┘         └────────┬─────────┘
        │                           │
┌───────▼────────┐         ┌────────▼─────────┐
│                │         │                  │
│  ECS Fargate   │◄────────┤  ECS Fargate     │
│  (Next.js)     │         │  (FastAPI)       │
│                │         │                  │
└────────────────┘         └────────┬─────────┘
                                    │
                           ┌────────▼─────────┐
                           │                  │
                           │  RDS PostgreSQL  │
                           │  (Multi-AZ)      │
                           │                  │
                           └──────────────────┘
```

---

## 📝 Paso a Paso - AWS ECS Fargate

### **PASO 1: Crear VPC y Subnets**

```powershell
# Variables de configuración
$REGION = "us-east-1"
$PROJECT_NAME = "smartparku"
$CLUSTER_NAME = "smartparku-cluster"

# Crear VPC
aws ec2 create-vpc `
  --cidr-block 10.0.0.0/16 `
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$PROJECT_NAME-vpc}]" `
  --region $REGION

# Guardar VPC ID
$VPC_ID = (aws ec2 describe-vpcs --filters "Name=tag:Name,Values=$PROJECT_NAME-vpc" --query "Vpcs[0].VpcId" --output text)

# Crear Internet Gateway
aws ec2 create-internet-gateway `
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=$PROJECT_NAME-igw}]" `
  --region $REGION

$IGW_ID = (aws ec2 describe-internet-gateways --filters "Name=tag:Name,Values=$PROJECT_NAME-igw" --query "InternetGateways[0].InternetGatewayId" --output text)

# Adjuntar IGW a VPC
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID --region $REGION

# Crear subnets públicas (2 para alta disponibilidad)
aws ec2 create-subnet `
  --vpc-id $VPC_ID `
  --cidr-block 10.0.1.0/24 `
  --availability-zone "${REGION}a" `
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-public-1}]"

aws ec2 create-subnet `
  --vpc-id $VPC_ID `
  --cidr-block 10.0.2.0/24 `
  --availability-zone "${REGION}b" `
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-public-2}]"

# Obtener IDs de subnets
$SUBNET1_ID = (aws ec2 describe-subnets --filters "Name=tag:Name,Values=$PROJECT_NAME-public-1" --query "Subnets[0].SubnetId" --output text)
$SUBNET2_ID = (aws ec2 describe-subnets --filters "Name=tag:Name,Values=$PROJECT_NAME-public-2" --query "Subnets[0].SubnetId" --output text)
```

---

### **PASO 2: Crear Grupo de Seguridad**

```powershell
# Security group para ALB
aws ec2 create-security-group `
  --group-name "$PROJECT_NAME-alb-sg" `
  --description "Security group for ALB" `
  --vpc-id $VPC_ID

$ALB_SG_ID = (aws ec2 describe-security-groups --filters "Name=group-name,Values=$PROJECT_NAME-alb-sg" --query "SecurityGroups[0].GroupId" --output text)

# Permitir tráfico HTTP/HTTPS
aws ec2 authorize-security-group-ingress `
  --group-id $ALB_SG_ID `
  --protocol tcp `
  --port 80 `
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress `
  --group-id $ALB_SG_ID `
  --protocol tcp `
  --port 443 `
  --cidr 0.0.0.0/0

# Security group para ECS
aws ec2 create-security-group `
  --group-name "$PROJECT_NAME-ecs-sg" `
  --description "Security group for ECS tasks" `
  --vpc-id $VPC_ID

$ECS_SG_ID = (aws ec2 describe-security-groups --filters "Name=group-name,Values=$PROJECT_NAME-ecs-sg" --query "SecurityGroups[0].GroupId" --output text)

# Permitir tráfico desde ALB
aws ec2 authorize-security-group-ingress `
  --group-id $ECS_SG_ID `
  --protocol tcp `
  --port 8000 `
  --source-group $ALB_SG_ID

aws ec2 authorize-security-group-ingress `
  --group-id $ECS_SG_ID `
  --protocol tcp `
  --port 3000 `
  --source-group $ALB_SG_ID
```

---

### **PASO 3: Crear Base de Datos RDS PostgreSQL**

```powershell
$DB_NAME = "smartparku"
$DB_USERNAME = "pgadmin"
$DB_PASSWORD = "SmartParkU2026!Secure"  # Cámbiala

# Crear subnet group para RDS
aws rds create-db-subnet-group `
  --db-subnet-group-name "$PROJECT_NAME-db-subnet" `
  --db-subnet-group-description "Subnet group for SmartParkU DB" `
  --subnet-ids $SUBNET1_ID $SUBNET2_ID

# Security group para RDS
aws ec2 create-security-group `
  --group-name "$PROJECT_NAME-rds-sg" `
  --description "Security group for RDS" `
  --vpc-id $VPC_ID

$RDS_SG_ID = (aws ec2 describe-security-groups --filters "Name=group-name,Values=$PROJECT_NAME-rds-sg" --query "SecurityGroups[0].GroupId" --output text)

# Permitir conexiones desde ECS
aws ec2 authorize-security-group-ingress `
  --group-id $RDS_SG_ID `
  --protocol tcp `
  --port 5432 `
  --source-group $ECS_SG_ID

# Crear instancia RDS
aws rds create-db-instance `
  --db-instance-identifier "$PROJECT_NAME-db" `
  --db-instance-class db.t3.micro `
  --engine postgres `
  --engine-version 15.4 `
  --master-username $DB_USERNAME `
  --master-user-password $DB_PASSWORD `
  --allocated-storage 20 `
  --db-name $DB_NAME `
  --vpc-security-group-ids $RDS_SG_ID `
  --db-subnet-group-name "$PROJECT_NAME-db-subnet" `
  --backup-retention-period 7 `
  --no-publicly-accessible

Write-Host "⏳ Creando base de datos... Esto tomará 5-10 minutos"

# Esperar a que esté disponible
aws rds wait db-instance-available --db-instance-identifier "$PROJECT_NAME-db"

# Obtener endpoint
$DB_ENDPOINT = (aws rds describe-db-instances --db-instance-identifier "$PROJECT_NAME-db" --query "DBInstances[0].Endpoint.Address" --output text)

Write-Host "✅ Base de datos creada: $DB_ENDPOINT"
```

---

### **PASO 4: Crear ECR (Elastic Container Registry)**

```powershell
# Crear repositorio para backend
aws ecr create-repository `
  --repository-name "$PROJECT_NAME/backend" `
  --region $REGION

# Crear repositorio para frontend
aws ecr create-repository `
  --repository-name "$PROJECT_NAME/frontend" `
  --region $REGION

# Obtener URL de ECR
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ECR_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

Write-Host "ECR URI: $ECR_URI"

# Login en ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI
```

---

### **PASO 5: Construir y Subir Imágenes**

```powershell
cd C:\Users\helen\Downloads\SmartParkU

# Backend
docker build -t "$PROJECT_NAME/backend" ./backend
docker tag "$PROJECT_NAME/backend:latest" "$ECR_URI/$PROJECT_NAME/backend:latest"
docker push "$ECR_URI/$PROJECT_NAME/backend:latest"

# Frontend
docker build -t "$PROJECT_NAME/frontend" ./frontend
docker tag "$PROJECT_NAME/frontend:latest" "$ECR_URI/$PROJECT_NAME/frontend:latest"
docker push "$ECR_URI/$PROJECT_NAME/frontend:latest"

Write-Host "✅ Imágenes subidas a ECR"
```

---

### **PASO 6: Crear Cluster ECS**

```powershell
# Crear cluster Fargate
aws ecs create-cluster `
  --cluster-name $CLUSTER_NAME `
  --region $REGION `
  --capacity-providers FARGATE FARGATE_SPOT `
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1

Write-Host "✅ Cluster ECS creado"
```

---

### **PASO 7: Crear Task Definitions**

Necesitamos crear archivos JSON para las definiciones de tareas.

**task-definition-backend.json:**
```json
{
  "family": "smartparku-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::{account-id}:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "{ecr-uri}/smartparku/backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql+psycopg://pgadmin:SmartParkU2026!Secure@{db-endpoint}:5432/smartparku"
        },
        {
          "name": "SECRET_KEY",
          "value": "produccion-secret-key-2026"
        },
        {
          "name": "ALGORITHM",
          "value": "HS256"
        },
        {
          "name": "ACCESS_TOKEN_EXPIRE_MINUTES",
          "value": "60"
        },
        {
          "name": "MQTT_BROKER",
          "value": "7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud"
        },
        {
          "name": "MQTT_PORT",
          "value": "8883"
        },
        {
          "name": "MQTT_USERNAME",
          "value": "Juliana"
        },
        {
          "name": "MQTT_PASSWORD",
          "value": "1138524566Juli*"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/smartparku-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

```powershell
# Registrar task definition
aws ecs register-task-definition --cli-input-json file://task-definition-backend.json
```

---

### **PASO 8: Crear Application Load Balancer**

```powershell
# Crear ALB
aws elbv2 create-load-balancer `
  --name "$PROJECT_NAME-alb" `
  --subnets $SUBNET1_ID $SUBNET2_ID `
  --security-groups $ALB_SG_ID `
  --scheme internet-facing `
  --type application

$ALB_ARN = (aws elbv2 describe-load-balancers --names "$PROJECT_NAME-alb" --query "LoadBalancers[0].LoadBalancerArn" --output text)
$ALB_DNS = (aws elbv2 describe-load-balancers --names "$PROJECT_NAME-alb" --query "LoadBalancers[0].DNSName" --output text)

# Crear target group para backend
aws elbv2 create-target-group `
  --name "$PROJECT_NAME-backend-tg" `
  --protocol HTTP `
  --port 8000 `
  --vpc-id $VPC_ID `
  --target-type ip `
  --health-check-path "/docs"

$TG_BACKEND_ARN = (aws elbv2 describe-target-groups --names "$PROJECT_NAME-backend-tg" --query "TargetGroups[0].TargetGroupArn" --output text)

# Crear listener
aws elbv2 create-listener `
  --load-balancer-arn $ALB_ARN `
  --protocol HTTP `
  --port 80 `
  --default-actions Type=forward,TargetGroupArn=$TG_BACKEND_ARN

Write-Host "✅ ALB creado: http://$ALB_DNS"
```

---

### **PASO 9: Crear Servicio ECS**

```powershell
# Crear servicio backend
aws ecs create-service `
  --cluster $CLUSTER_NAME `
  --service-name "$PROJECT_NAME-backend" `
  --task-definition "smartparku-backend" `
  --desired-count 1 `
  --launch-type FARGATE `
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1_ID,$SUBNET2_ID],securityGroups=[$ECS_SG_ID],assignPublicIp=ENABLED}" `
  --load-balancers "targetGroupArn=$TG_BACKEND_ARN,containerName=backend,containerPort=8000"

Write-Host "✅ Servicio backend desplegado"
```

---

## 💰 Costos Estimados AWS

| Servicio | Configuración | Costo Mensual |
|----------|---------------|---------------|
| ECS Fargate (Backend) | 0.5 vCPU, 1 GB | $20-30 USD |
| ECS Fargate (Frontend) | 0.5 vCPU, 1 GB | $20-30 USD |
| RDS PostgreSQL | db.t3.micro | $15-20 USD |
| Application Load Balancer | 1 ALB | $16 USD |
| ECR Storage | 1-2 GB | $1-2 USD |
| Data Transfer | Normal usage | $10-20 USD |
| **TOTAL** | | **$82-118 USD/mes** |

---

## ⚖️ Comparación: Azure vs AWS

| Aspecto | Azure Container Apps | AWS ECS Fargate |
|---------|---------------------|-----------------|
| **Facilidad** | ⭐⭐⭐⭐⭐ Más simple | ⭐⭐⭐ Más complejo |
| **Pasos de Setup** | ~8 pasos | ~12 pasos |
| **Configuración Red** | Automática | Manual (VPC, Subnets, SG) |
| **SSL/HTTPS** | Automático | Manual (Certificate Manager) |
| **Costo** | $55-80/mes | $82-118/mes |
| **Free Tier** | $200 crédito | 12 meses limitado |
| **Escalado** | Automático simple | Automático complejo |
| **Documentación** | Excelente | Muy completa pero densa |

---

## 🎯 Recomendación Final

### **Usa Azure si:**
- ✅ Es tu primer despliegue en la nube
- ✅ Quieres algo rápido y funcional
- ✅ Prefieres menos configuración manual
- ✅ Tu presupuesto es limitado

### **Usa AWS si:**
- ✅ Ya tienes experiencia con AWS
- ✅ Necesitas integraciones específicas de AWS
- ✅ Tu organización ya usa AWS
- ✅ Necesitas control granular de la infraestructura

---

## 📚 Script Completo AWS

He preparado todo el proceso en un script automatizado. Ver: `deploy-aws.ps1`

---

**Para este proyecto, recomiendo Azure Container Apps por simplicidad y costo. 🎯**
