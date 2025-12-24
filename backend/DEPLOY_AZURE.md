1# Deploy Book Translation API to Microsoft Azure

Hướng dẫn chi tiết deploy API lên Azure (dành cho Azure for Students).

---

## Tài nguyên của bạn

| Resource | Giá trị |
|----------|---------|
| Credit | $100 |
| Thời hạn | 365 ngày |
| Blob Storage | 5 GB FREE |

---

## Bước 0: Cài đặt Azure CLI

### Windows
1. Download từ: https://aka.ms/installazurecliwindows
2. Chạy installer
3. Mở PowerShell mới và kiểm tra:
   ```bash
   az --version
   ```

---

## Bước 1: Login và Setup

### 1.1 Login Azure
```bash
az login
```
→ Mở browser để đăng nhập tài khoản Azure của bạn

### 1.2 Kiểm tra subscription
```bash
az account show
```
→ Sẽ thấy "Azure for Students" subscription

### 1.3 Tạo Resource Group
```bash
# Tạo resource group ở Southeast Asia (gần VN)
az group create --name book-translator-rg --location southeastasia
```

---

## Bước 2: Tạo Azure Blob Storage

### 2.1 Tạo Storage Account
```bash
# Thay booktranslator123 bằng tên unique (chỉ chữ thường và số)
az storage account create \
  --name booktranslator123 \
  --resource-group book-translator-rg \
  --location southeastasia \
  --sku Standard_LRS
```

### 2.2 Tạo Container (tương đương bucket)
```bash
# Lấy connection string
az storage account show-connection-string \
  --name booktranslator123 \
  --resource-group book-translator-rg \
  --output tsv

# Tạo container
az storage container create \
  --name books \
  --account-name booktranslator123 \
  --public-access blob
```

### 2.3 Lưu lại Connection String
```bash
az storage account show-connection-string \
  --name booktranslator123 \
  --resource-group book-translator-rg
```
→ Lưu lại giá trị `connectionString` cho bước sau

---

## Bước 3: Deploy lên Azure Container Apps

### 3.1 Cài extension Container Apps
```bash
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
```

### 3.2 Tạo Container Apps Environment
```bash
az containerapp env create \
  --name book-translator-env \
  --resource-group book-translator-rg \
  --location southeastasia
```

### 3.3 Deploy API
```bash
cd c:\Users\vieta\poker-book-translator\backend

# Build và deploy từ source
az containerapp up \
  --name book-translator-api \
  --resource-group book-translator-rg \
  --environment book-translator-env \
  --source . \
  --ingress external \
  --target-port 8080
```

### 3.4 Set Environment Variables
```bash
az containerapp update \
  --name book-translator-api \
  --resource-group book-translator-rg \
  --set-env-vars \
    "GEMINI_API_KEY=xxx" \
    "ADMIN_API_KEY=xxx" \
    "AZURE_STORAGE_CONNECTION_STRING=xxx" \
    "SUPABASE_URL=xxx" \
    "SUPABASE_KEY=xxx"
```

---

## Bước 4: Lấy API URL

```bash
az containerapp show \
  --name book-translator-api \
  --resource-group book-translator-rg \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```
→ URL dạng: `book-translator-api.xxx.southeastasia.azurecontainerapps.io`

---

## Bước 5: Test API

### Health check
```bash
curl https://YOUR-URL/health
```

### Swagger UI
Mở browser: `https://YOUR-URL/docs`

---

## Cập nhật Code cho Azure Storage

Bạn cần cập nhật `storage_service.py` để dùng Azure Blob Storage thay vì GCS.
Tôi sẽ tạo file này nếu bạn confirm dùng Azure.

---

## Chi phí ước tính

| Service | Free Tier | Chi phí |
|---------|-----------|---------|
| Container Apps | 180,000 vCPU-s/tháng | ~$0 với usage nhỏ |
| Blob Storage | 5 GB | FREE |
| Bandwidth | 5 GB/tháng | FREE |

**Với $100 credit:** Dùng được 1+ năm!

---

## Troubleshooting

### Xem logs
```bash
az containerapp logs show \
  --name book-translator-api \
  --resource-group book-translator-rg \
  --follow
```

### Restart app
```bash
az containerapp revision restart \
  --name book-translator-api \
  --resource-group book-translator-rg
```

### Xóa tất cả
```bash
az group delete --name book-translator-rg --yes
```
