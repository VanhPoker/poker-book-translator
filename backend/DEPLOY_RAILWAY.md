# Deploy Book Translation API to Railway

Hướng dẫn deploy API lên Railway.app (miễn phí, không cần credit card).

---

## Tài nguyên Free Tier

| Service | Free Tier |
|---------|-----------|
| Railway | $5 credit/tháng |
| Supabase Storage | 1GB |

---

## Bước 1: Setup Supabase Storage

### 1.1 Vào Supabase Dashboard
- Đăng nhập [app.supabase.com](https://app.supabase.com)
- Chọn project của bạn

### 1.2 Tạo Storage Bucket
1. Vào **Storage** → **New bucket**
2. Đặt tên: `books`
3. ✅ Check **Public bucket**
4. Click **Create bucket**

### 1.3 Lấy Credentials
- **SUPABASE_URL**: Settings → API → Project URL
- **SUPABASE_KEY**: Settings → API → `anon` `public` key

---

## Bước 2: Deploy lên Railway

### 2.1 Đăng ký Railway
1. Vào [railway.app](https://railway.app)
2. Click **Login** → **GitHub**
3. Authorize Railway

### 2.2 Tạo Project mới
1. Click **New Project**
2. Chọn **Deploy from GitHub repo**
3. Chọn repo `poker-book-translator`
4. Railway sẽ tự detect Dockerfile

### 2.3 Configure Settings
1. Vào project → **Settings**
2. **Root Directory**: `backend`
3. **Port**: `8080`

### 2.4 Add Environment Variables
Vào **Variables** tab, thêm:

```env
GEMINI_API_KEY=your-gemini-api-key
ADMIN_API_KEY=your-secure-admin-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_STORAGE_BUCKET=books
STORAGE_PROVIDER=supabase
```

### 2.5 Deploy
- Railway tự động build và deploy
- Chờ khoảng 3-5 phút

---

## Bước 3: Lấy API URL

1. Vào project → **Settings** → **Domains**
2. Click **Generate Domain**
3. URL dạng: `xxx.up.railway.app`

---

## Bước 4: Test API

### Health check
```bash
curl https://YOUR-URL/health
```

### Swagger UI
Mở browser: `https://YOUR-URL/docs`

---

## Troubleshooting

### Xem logs
- Railway Dashboard → Project → **Logs** tab

### Restart
- Railway Dashboard → **Deployments** → Click "..." → **Restart**

### Xóa project
- Railway Dashboard → **Settings** → **Danger Zone** → Delete

---

## Chi phí ước tính

| Service | Usage | Cost |
|---------|-------|------|
| Railway | ~500 MB RAM, 0.5 vCPU | ~$0-2/tháng |
| Supabase | 1GB storage | FREE |

**Với $5 free credit/tháng**: Đủ cho project nhỏ!
