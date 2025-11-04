# Google OAuth Configuration Check

## Common Issue: 401 Unauthorized on Google Login

If you're getting `401 Unauthorized` errors when trying to use Google login, the most common cause is a **Client ID mismatch** between frontend and backend.

## Required Configuration

### Backend (.env file)
```env
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

### Frontend (.env.local file)
```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here
```

**IMPORTANT**: The `GOOGLE_CLIENT_ID` in backend must **EXACTLY MATCH** the `NEXT_PUBLIC_GOOGLE_CLIENT_ID` in frontend.

## How to Verify

1. **Check backend configuration:**
   ```bash
   cd backend
   python -c "from app.config import settings; print('GOOGLE_CLIENT_ID:', settings.GOOGLE_CLIENT_ID[:20] + '...' if settings.GOOGLE_CLIENT_ID else 'NOT SET')"
   ```

2. **Check frontend configuration:**
   - Open `frontend/.env.local`
   - Verify `NEXT_PUBLIC_GOOGLE_CLIENT_ID` is set
   - Make sure it matches the backend `GOOGLE_CLIENT_ID` exactly

3. **Restart servers:**
   - Restart your backend server after changing `.env`
   - Restart your frontend dev server after changing `.env.local`

## Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Find your OAuth 2.0 Client ID
4. Make sure:
   - **Authorized JavaScript origins** includes:
     - `http://localhost:3000` (for development)
     - Your production domain (for production)
   - **Authorized redirect URIs** includes:
     - `http://localhost:3000` (for development)
     - Your production domain (for production)

## Troubleshooting

1. **Clear browser cache** - Sometimes cached tokens can cause issues
2. **Check browser console** - Look for any JavaScript errors
3. **Check backend logs** - The improved error messages will show what's wrong
4. **Verify token format** - The token should be a long string starting with `eyJ...`

## Testing

After fixing the configuration:
1. Clear browser cookies for localhost
2. Restart both frontend and backend servers
3. Try logging in with Google again

