# Deploy Book Translation API to Google Cloud Run

Hướng dẫn chi tiết từng bước để deploy API lên Google Cloud.

---

## Bước 0: Chuẩn bị

### 0.1 Tạo tài khoản Google Cloud (nếu chưa có)
1. Truy cập https://console.cloud.google.com/
2. Đăng ký với thẻ tín dụng (sẽ nhận $300 free credit)
3. Nhớ project ID sau khi tạo xong

### 0.2 Cài đặt Google Cloud CLI
1. Download từ: https://cloud.google.com/sdk/docs/install
2. Chạy installer
3. Mở terminal mới và kiểm tra:
   ```bash
   gcloud --version
   ```

---

## Bước 1: Login và Setup Project

### 1.1 Login vào Google Cloud
```bash
gcloud auth login
```
→ Sẽ mở browser để đăng nhập Google account

### 1.2 Tạo hoặc chọn Project
```bash
# Xem danh sách projects
gcloud projects list

# Tạo project mới (THAY book-translator-xxx bằng tên bạn muốn)
gcloud projects create book-translator-xxx --name="Book Translator"

# Set project mặc định
gcloud config set project book-translator-xxx
```

### 1.3 Enable cần thiết APIs
```bash
# Cloud Run - để chạy API
gcloud services enable run.googleapis.com

# Cloud Build - để build Docker image
gcloud services enable cloudbuild.googleapis.com

# Cloud Storage - để lưu files
gcloud services enable storage.googleapis.com

# Artifact Registry - để lưu Docker images
gcloud services enable artifactregistry.googleapis.com
```

---

## Bước 2: Tạo Google Cloud Storage Bucket

### 2.1 Tạo bucket
```bash
# Thay YOUR-BUCKET-NAME bằng tên unique (VD: book-translator-files-123)
gsutil mb -l asia-southeast1 gs://YOUR-BUCKET-NAME
```

### 2.2 Set bucket public (để FE có thể load HTML/images)
```bash
gsutil iam ch allUsers:objectViewer gs://YOUR-BUCKET-NAME
```

### 2.3 Set CORS (nếu cần load từ browser khác domain)
Tạo file `cors.json`:
```json
[
  {
    "origin": ["*"],
    "method": ["GET"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
```

Apply:
```bash
gsutil cors set cors.json gs://YOUR-BUCKET-NAME
```

---

## Bước 3: Setup Supabase Database

### 3.1 Tạo project trên Supabase (nếu chưa có)
1. Truy cập https://supabase.com/
2. Create new project
3. Lưu lại **Project URL** và **anon key** từ Settings → API

### 3.2 Tạo table `translated_books`
Vào SQL Editor trong Supabase và chạy:

```sql
CREATE TABLE translated_books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    source_format VARCHAR(20) DEFAULT 'pdf',
    target_language VARCHAR(10) DEFAULT 'vi',
    
    -- Output URLs
    html_url TEXT,
    epub_url TEXT,
    pdf_url TEXT,
    
    -- Token tracking
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10,4) DEFAULT 0,
    
    -- Metadata
    page_count INTEGER,
    file_size_bytes BIGINT,
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Enable Row Level Security (optional nhưng khuyến nghị)
ALTER TABLE translated_books ENABLE ROW LEVEL SECURITY;

-- Allow all operations (điều chỉnh theo nhu cầu)
CREATE POLICY "Allow all" ON translated_books FOR ALL USING (true);
```

---

## Bước 4: Chuẩn bị Environment Variables

Thu thập các values sau:

| Variable | Giá trị | Lấy từ đâu |
|----------|---------|------------|
| GEMINI_API_KEY | AIza... | https://aistudio.google.com/apikey |
| ADMIN_API_KEY | your-secret-key | Tự tạo password mạnh |
| GCS_BUCKET | book-translator-files-123 | Tên bucket ở Bước 2 |
| SUPABASE_URL | https://xxx.supabase.co | Supabase → Settings → API |
| SUPABASE_KEY | eyJhbGci... | Supabase → Settings → API (anon key) |

---

## Bước 5: Deploy lên Cloud Run

### 5.1 Chuyển đến thư mục backend
```bash
cd c:\Users\vieta\poker-book-translator\backend
```

### 5.2 Deploy (THAY các giá trị xxx)
```bash
gcloud run deploy book-translator-api \
  --source . \
  --region asia-southeast1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 3600 \
  --set-env-vars "GEMINI_API_KEY=xxx,ADMIN_API_KEY=xxx,GCS_BUCKET=xxx,SUPABASE_URL=xxx,SUPABASE_KEY=xxx"
```

**Giải thích các flags:**
- `--source .` : Build từ source code hiện tại
- `--region asia-southeast1` : Singapore (gần VN nhất)
- `--memory 2Gi` : 2GB RAM (cần cho PDF processing)
- `--timeout 3600` : 1 giờ timeout (sách lớn cần nhiều thời gian)
- `--allow-unauthenticated` : Cho phép public access

### 5.3 Chờ deploy xong
Build + deploy mất khoảng 5-10 phút lần đầu.
Sau khi xong sẽ hiện URL như:
```
Service URL: https://book-translator-api-xxxxx-as.a.run.app
```

---

## Bước 6: Test API đã deploy

### 6.1 Test health check
```bash
curl https://YOUR-URL/health
```
→ Response: `{"status":"healthy"}`

### 6.2 Test translation endpoint
```bash
curl -X POST https://YOUR-URL/api/v1/translate \
  -H "X-API-Key: YOUR-ADMIN-KEY" \
  -F "file=@path/to/your/book.pdf" \
  -F "title=My Book"
```

### 6.3 Mở Swagger UI
Truy cập: `https://YOUR-URL/docs`

---

## Bước 7: Setup CI/CD (Optional)

### 7.1 Push code lên GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/poker-book-translator.git
git push -u origin main
```

### 7.2 Tạo Cloud Build Trigger
1. Vào https://console.cloud.google.com/cloud-build/triggers
2. Create Trigger
3. Connect GitHub repo
4. Set trigger on push to `main` branch
5. Add substitution variables for env vars

---

## Troubleshooting

### Xem build logs
```bash
gcloud builds list
gcloud builds log BUILD_ID
```

### Xem runtime logs
```bash
gcloud run services logs read book-translator-api --region asia-southeast1
```

### Deploy lại
```bash
gcloud run deploy book-translator-api --source . --region asia-southeast1
```

### Xóa service
```bash
gcloud run services delete book-translator-api --region asia-southeast1
```

---

## Chi phí ước tính

| Service | Free Tier | Sau Free Tier |
|---------|-----------|---------------|
| Cloud Run | 2M requests/tháng | $0.40/1M req |
| Cloud Storage | 5 GB | $0.02/GB/tháng |
| Cloud Build | 120 min/ngày | $0.003/phút |
| Gemini API | Theo plan | ~$0.03/sách |

**Tổng với $300 credit:** Dùng được ~1 năm với usage trung bình!
