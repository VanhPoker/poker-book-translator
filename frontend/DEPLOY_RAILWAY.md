# Deploy Frontend to Railway

## Quick Deploy

### 1. Chuẩn bị
Tạo file `railway.json` trong thư mục `frontend/`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm run start",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. Environment Variables
Trong Railway dashboard, thêm các biến:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### 3. Deploy Steps

1. **Login Railway CLI:**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Link project:**
   ```bash
   cd frontend
   railway link
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

### 4. Hoặc Deploy via GitHub

1. Vào [railway.app](https://railway.app)
2. New Project → Deploy from GitHub repo
3. Chọn repo `poker-book-translator`
4. **Root Directory:** `frontend`
5. Thêm Environment Variables
6. Deploy!

### 5. Custom Domain (Optional)
- Settings → Domains → Add Custom Domain
- Cấu hình DNS: CNAME → `*.up.railway.app`

---

## Lưu ý
- Railway tự detect Next.js và build với `npm run build`
- Start command mặc định: `npm run start`
- Port tự động: Railway cấp port qua `$PORT`
