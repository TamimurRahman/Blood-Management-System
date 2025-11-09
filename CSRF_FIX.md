# CSRF Token Error Fix

## ✅ Fixed Settings

I've updated the settings to fix CSRF token errors in Django admin:

1. **Added CSRF_TRUSTED_ORIGINS** - Allows CSRF tokens from localhost
2. **Added Session Cookie Settings** - Ensures proper cookie handling
3. **Updated ALLOWED_HOSTS** - Added localhost and 127.0.0.1

## 🔧 If Error Persists - Try These Steps:

### Step 1: Restart Django Server
```powershell
# Stop the server (Ctrl+C)
# Then restart:
python manage.py runserver
```

### Step 2: Clear Browser Cache and Cookies
1. **Chrome/Edge**: Press `Ctrl+Shift+Delete` → Clear cookies and cached images
2. **Firefox**: Press `Ctrl+Shift+Delete` → Clear cookies and cache
3. Or use **Incognito/Private mode** to test

### Step 3: Clear Django Sessions
```powershell
python manage.py clearsessions
```

### Step 4: Verify You're Logged In
- Make sure you're properly logged into Django admin
- Try logging out and logging back in
- Check that your session is active

### Step 5: Check Browser Console
- Press `F12` to open developer tools
- Check the Console tab for any JavaScript errors
- Check the Network tab to see if cookies are being sent

## 🎯 Alternative: Use Django Shell

If CSRF errors persist, you can add blood banks via Django shell:

```powershell
python manage.py shell
```

Then run:
```python
from blood_management.models import BloodBank

BloodBank.objects.create(
    name='City General Hospital Blood Bank',
    address='123 Main Street, Medical Center',
    city='New York',
    state='NY',
    zip_code='10001',
    phone_number='(555) 123-4567',
    email='bloodbank@citygeneral.com'
)
```

## 📝 What Was Changed

**File: `blood_management_project/settings.py`**

Added:
- `CSRF_TRUSTED_ORIGINS` - Trusts CSRF tokens from localhost
- `SESSION_COOKIE_SECURE = False` - Allows cookies over HTTP (development)
- `CSRF_COOKIE_SECURE = False` - Allows CSRF cookies over HTTP (development)
- `ALLOWED_HOSTS` - Added localhost and 127.0.0.1

## ✅ Test

After restarting the server:
1. Clear browser cache/cookies
2. Login to Django admin: `http://127.0.0.1:8000/django-admin/`
3. Try adding a blood bank again
4. The CSRF error should be resolved

