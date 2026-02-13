# VM Frontend Deployment

Deploying the t0 web frontend and backend on a single Azure VM using nginx with HTTPS.

## Architecture

```
Browser → nginx (port 443, HTTPS)
             ├── / → serves static frontend files from /var/www/t0
             └── /api/* → proxies to backend on localhost:8050
```

This replaces the previous setup of GitHub Pages (frontend) + Azure App Service reverse proxy (HTTPS for API).

## Prerequisites

- Azure VM (Ubuntu) with the backend already running on port 8050
- Azure CLI access

## Setup Steps

### 1. Assign a DNS label to the VM's public IP

```bash
az network public-ip update \
  --resource-group mini_vm_rg \
  --name <your-public-ip-name> \
  --dns-name t0-web
```

This gives you `t0-web.uksouth.cloudapp.azure.com` (free, required for Let's Encrypt).

### 2. Add NSG rules for HTTP and HTTPS

```bash
az network nsg rule create \
  --resource-group mini_vm_rg \
  --nsg-name miniVM-nsg \
  --name AllowHTTP \
  --priority 310 \
  --protocol TCP \
  --destination-port-ranges 80 \
  --access Allow \
  --direction Inbound

az network nsg rule create \
  --resource-group mini_vm_rg \
  --nsg-name miniVM-nsg \
  --name AllowHTTPS \
  --priority 320 \
  --protocol TCP \
  --destination-port-ranges 443 \
  --access Allow \
  --direction Inbound
```

### 3. Install nginx and certbot on the VM

```bash
sudo apt update && sudo apt install -y nginx certbot python3-certbot-nginx
```

### 4. Create nginx config

Create `/etc/nginx/sites-available/t0`:

```nginx
server {
    listen 80;
    server_name t0-web.uksouth.cloudapp.azure.com;

    root /var/www/t0;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8050/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;
    }

    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

Enable it:

```bash
sudo ln -s /etc/nginx/sites-available/t0 /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

### 5. Get HTTPS certificate

```bash
sudo certbot --nginx -d t0-web.uksouth.cloudapp.azure.com
```

Certbot adds SSL config to the nginx file automatically and sets up auto-renewal.

### 6. Build and deploy the frontend

Update `HOST` in `web/src/App.svelte`:

```ts
const HOST = "/api";
```

Build and copy to the serve directory:

```bash
cd t0-1/web
pnpm install && pnpm build
sudo mkdir -p /var/www/t0
sudo cp -r dist/* /var/www/t0/
sudo chmod -R 755 /var/www/t0
```

## Redeploying after code changes

```bash
cd t0-1/web
pnpm build
sudo cp -r dist/* /var/www/t0/
```

## Notes

- The `t0-reverse-proxy` Azure App Service is no longer needed and can be retired.
- Certbot auto-renews the SSL certificate.
- The nginx config in `sites-enabled/t0` is the active one (certbot may write directly there rather than to `sites-available/t0`).
- `/var/www/t0` is used instead of serving from the home directory to avoid permission issues with nginx.
