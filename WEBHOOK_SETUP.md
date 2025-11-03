# SendGrid Webhook Setup Guide

## Problem: SendGrid Cannot Reach Localhost

SendGrid webhooks require a **public URL** that SendGrid can access. If you're running the backend on `localhost:8000`, SendGrid cannot reach it.

## Solution: Use a Tunneling Service

### Option 1: ngrok (Recommended for Local Development)

1. **Install ngrok:**
   - Download from: https://ngrok.com/download
   - Or use: `choco install ngrok` (Windows) / `brew install ngrok` (Mac)

2. **Start your backend server:**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start ngrok tunnel:**
   ```bash
   ngrok http 8000
   ```

4. **Copy the public URL:**
   - ngrok will show something like: `https://abc123.ngrok.io`
   - Your webhook URL will be: `https://abc123.ngrok.io/webhook/sendgrid`

5. **Configure SendGrid:**
   - Go to SendGrid Dashboard → Settings → Mail Settings → Event Webhook
   - Set HTTP POST URL: `https://your-ngrok-url.ngrok.io/webhook/sendgrid`
   - Enable events: **Delivered**, **Opened**, **Clicked**, **Bounced**, **Dropped**
   - Copy the verification key to your `.env` file as `SENDGRID_WEBHOOK_VERIFICATION_KEY`

6. **Test the webhook:**
   ```bash
   curl https://your-ngrok-url.ngrok.io/webhook/sendgrid/test
   ```

### Option 2: Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:8000
```

### Option 3: localtunnel

```bash
npx localtunnel --port 8000
```

## Environment Configuration

### For Local Development (with ngrok)

Set in your `.env` file:
```env
ENVIRONMENT=development
SENDGRID_WEBHOOK_VERIFICATION_KEY=  # Can be empty in dev, but recommended to set it
```

### For Production

Set in your `.env` file:
```env
ENVIRONMENT=production
SENDGRID_WEBHOOK_VERIFICATION_KEY=-----BEGIN PUBLIC KEY-----
... (paste the key from SendGrid dashboard)
-----END PUBLIC KEY-----
```

## Verification Steps

1. **Test webhook endpoint is accessible:**
   ```bash
   curl https://your-public-url/webhook/sendgrid/test
   ```

2. **Send a test email** from your application

3. **Check backend logs** for webhook events:
   ```bash
   # Look for logs like:
   # "Successfully processed webhook event: open for message ..."
   ```

4. **Check database:**
   ```sql
   SELECT id, status, sent_at, opened_at, clicked_at 
   FROM email_logs 
   ORDER BY created_at DESC 
   LIMIT 10;
   ```

## Troubleshooting

### Webhooks Not Received

1. **Verify endpoint is public:**
   - Test with: `curl https://your-url/webhook/sendgrid/test`

2. **Check SendGrid dashboard:**
   - Go to Activity Feed
   - Look for webhook delivery status
   - Check for errors

3. **Check backend logs:**
   - Look for webhook-related errors
   - Check if signature verification is failing

4. **Verify environment variable:**
   - In development, signature verification is more lenient
   - In production, `SENDGRID_WEBHOOK_VERIFICATION_KEY` must be set correctly

### Signature Verification Failing

- Make sure `SENDGRID_WEBHOOK_VERIFICATION_KEY` is set correctly
- The key should start with `-----BEGIN PUBLIC KEY-----` and end with `-----END PUBLIC KEY-----`
- In development mode, signature verification can be bypassed if key is not set

### Timestamps Not Updating

- Check that webhook events are being received (check logs)
- Verify `process_webhook_event` is being called
- Check database for `opened_at` and `clicked_at` updates

## Production Deployment

For production, deploy your backend to a cloud service (AWS, Heroku, DigitalOcean, etc.) and:

1. Set the webhook URL to: `https://your-production-domain.com/webhook/sendgrid`
2. Ensure `SENDGRID_WEBHOOK_VERIFICATION_KEY` is set in production environment
3. Test by sending an email and checking the database for updates

