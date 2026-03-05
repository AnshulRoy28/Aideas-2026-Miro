# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for Miro.

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: "Miro Auth" (or your preferred name)
4. Click "Create"

## Step 2: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" (or "Internal" if you have Google Workspace)
3. Click "Create"
4. Fill in the required fields:
   - App name: "Miro"
   - User support email: your email
   - Developer contact: your email
5. Click "Save and Continue"
6. Skip "Scopes" (click "Save and Continue")
7. Add test users if using External (add teacher emails)
8. Click "Save and Continue"

## Step 3: Create OAuth Client ID

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Web application"
4. Name: "Miro Web Client"
5. Add Authorized JavaScript origins:
   - `http://localhost:8000` (for local development)
   - Your production domain (e.g., `https://yourdomain.com`)
6. Add Authorized redirect URIs:
   - `http://localhost:8000` (for local development)
   - Your production domain
7. Click "Create"
8. **Copy the Client ID** - you'll need this!

## Step 4: Update Your Configuration

1. Open your `.env` file
2. Add the Google Client ID:
   ```
   GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   JWT_SECRET=generate_a_random_secret_key_here
   ```

3. Generate a secure JWT secret:
   ```bash
   # On Linux/Mac:
   openssl rand -hex 32
   
   # On Windows (PowerShell):
   -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
   ```

4. Update `frontend/login.html`:
   - Find the line: `data-client_id="YOUR_GOOGLE_CLIENT_ID"`
   - Replace `YOUR_GOOGLE_CLIENT_ID` with your actual Client ID

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 6: Test Authentication

1. Start your server:
   ```bash
   python server.py
   ```

2. Open your browser to `http://localhost:8000/login.html`
3. Click "Sign in with Google"
4. Select your Google account
5. You should be redirected to the main app

## Troubleshooting

### "Error 400: redirect_uri_mismatch"
- Make sure the redirect URI in Google Console matches your app URL exactly
- Check for trailing slashes

### "Error 401: Invalid token"
- Verify your GOOGLE_CLIENT_ID in .env matches the one from Google Console
- Make sure you updated the Client ID in login.html

### "Error: idpiframe_initialization_failed"
- Check that your domain is added to Authorized JavaScript origins
- Clear browser cache and cookies

## Production Deployment

When deploying to production:

1. Add your production domain to Google Console:
   - Authorized JavaScript origins: `https://yourdomain.com`
   - Authorized redirect URIs: `https://yourdomain.com`

2. Update `frontend/login.html` with your production Client ID

3. Set a strong JWT_SECRET in production .env

4. Consider restricting OAuth to specific email domains:
   - In OAuth consent screen, add your school domain
   - Or implement domain checking in backend

## Security Notes

- Never commit your `.env` file to version control
- Use a strong, random JWT_SECRET in production
- Consider implementing email domain restrictions for school-only access
- Enable HTTPS in production (required by Google OAuth)
