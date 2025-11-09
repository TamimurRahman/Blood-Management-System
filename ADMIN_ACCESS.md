# 🔐 Admin Access Guide

## How to Access Admin Dashboard

### Option 1: Create an Admin User During Registration

1. Go to: `http://127.0.0.1:8000/register/`
2. Fill in the registration form
3. **Important**: Select **"Admin"** from the Role dropdown
4. Complete registration
5. Login with your admin credentials
6. Access admin dashboard at: `http://127.0.0.1:8000/admin/dashboard/`

### Option 2: Create a Superuser (Recommended)

1. Open terminal/PowerShell
2. Activate virtual environment:
   ```powershell
   venv\Scripts\activate
   ```
3. Create superuser:
   ```powershell
   python manage.py createsuperuser
   ```
4. Enter username, email, and password when prompted
5. Login with superuser credentials
6. Access admin dashboard at: `http://127.0.0.1:8000/admin/dashboard/`

### Option 3: Change Existing User to Admin

1. Access Django admin panel: `http://127.0.0.1:8000/django-admin/`
2. Login with superuser credentials
3. Go to **Users** section
4. Click on the user you want to make admin
5. Change **Role** from "Donor" to "Admin"
6. Save changes
7. That user can now access admin dashboard

## Admin URLs

- **Custom Admin Dashboard**: `http://127.0.0.1:8000/admin/dashboard/`
- **Manage Donors**: `http://127.0.0.1:8000/admin/donors/`
- **Manage Blood Banks**: `http://127.0.0.1:8000/admin/blood-banks/`
- **Manage Requests**: `http://127.0.0.1:8000/admin/requests/`
- **Django Admin Panel**: `http://127.0.0.1:8000/django-admin/`

## Troubleshooting

### "Admin not found" or 404 Error

**Possible causes:**
1. **Not logged in** - Login first at `http://127.0.0.1:8000/login/`
2. **User doesn't have admin role** - User must have role="admin" or be a superuser
3. **Wrong URL** - Make sure you're using `/admin/dashboard/` not just `/admin/`

### "Access denied" Message

If you see "Access denied. Admin privileges required":
- Your user account doesn't have admin role
- Change your role to "Admin" via Django admin panel
- Or create a new admin user

### How to Check if User is Admin

1. Login to Django admin: `http://127.0.0.1:8000/django-admin/`
2. Go to **Users** → Select your user
3. Check the **Role** field - it should be "Admin"
4. Or check **Superuser status** - Superusers automatically have admin access

## Quick Test

1. Create superuser: `python manage.py createsuperuser`
2. Login at: `http://127.0.0.1:8000/login/`
3. You should be automatically redirected to admin dashboard
4. If not, manually go to: `http://127.0.0.1:8000/admin/dashboard/`

## Notes

- **Superusers** automatically have admin access (no need to set role="admin")
- **Regular users** with role="admin" also have admin access
- **Donors** (role="donor") cannot access admin pages
- Admin dashboard shows system statistics and management tools

