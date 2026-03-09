# Django Allauth Google Setup

This document describes how to configure Google OAuth for this project using `django-allauth`.

## 1. Google Cloud Console
1. Open https://console.cloud.google.com/
2. Create or select a project.
3. Configure OAuth consent screen:
   - App name
   - Support email
   - Developer email
   - Add test users while app is in testing mode
4. Go to Credentials -> Create Credentials -> OAuth client ID.
5. Application type: Web application.
6. Add Authorized redirect URIs:
   - Production: `https://lms-w5ul.onrender.com/accounts/google/login/callback/`
   - Local: `http://127.0.0.1:8000/accounts/google/login/callback/`
   - Local: `http://localhost:8000/accounts/google/login/callback/`
7. Save and copy:
   - Client ID
   - Client Secret

## 2. Django Admin Site configuration
1. Sign in to `/admin/` as superuser.
2. Open `Sites`.
3. Edit site with id=1:
   - Domain name: `lms-w5ul.onrender.com`
   - Display name: your app name

## 3. Django Admin SocialApp configuration
1. Open `Social applications` -> Add.
2. Provider: `Google`.
3. Name: e.g. `Google OAuth`.
4. Client id: paste Google Client ID.
5. Secret key: paste Google Client Secret.
6. In `Sites`, move the production site to selected.
7. Save.

## 4. Render environment variables
Ensure these are configured in Render:
- `ALLOWED_HOSTS=lms-w5ul.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://lms-w5ul.onrender.com`
- `DEBUG=False`
- `SECRET_KEY=<strong-random-key>`
- `DATABASE_URL=<render-postgres-url>`
- Cloudinary variables (`CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`)

## 5. Verification flow
1. Open login page.
2. Click `Sign in with Google`.
3. Complete consent.
4. Confirm callback returns to app and user is authenticated.

## 6. Common errors and fixes
- `redirect_uri_mismatch`: callback URL mismatch in Google Console.
- `SocialAppDoesNotExist`: SocialApp missing or not attached to Site.
- `DisallowedHost`: Render host not included in `ALLOWED_HOSTS`.
- CSRF origin errors: missing `CSRF_TRUSTED_ORIGINS`.
- Works locally but not production: site domain in `Sites` still points to localhost.
