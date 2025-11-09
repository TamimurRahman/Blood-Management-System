# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```
Enter username, email, and password when prompted.

### Step 4: Run the Server
```bash
python manage.py runserver
```

### Step 5: Access the Application
Open your browser and navigate to:
- **Home**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Root**: http://127.0.0.1:8000/api/

## 📝 First Steps

### For Donors:
1. Go to http://127.0.0.1:8000/register/
2. Register with role "Donor"
3. Login and complete your profile
4. Create a donation request

### For Admins:
1. Create a superuser or register with role "Admin"
2. Login to access the admin dashboard
3. Manage donors, blood banks, and requests

## 🔑 Default Test Accounts

You can create test accounts through:
- Registration page: http://127.0.0.1:8000/register/
- Admin panel: http://127.0.0.1:8000/admin/

## 📚 API Testing

You can test the API using:
- **Postman**
- **curl** commands
- **Django REST Framework Browsable API**: http://127.0.0.1:8000/api/

### Example API Calls:

**Register a user:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "role": "donor"
  }'
```

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

## 🛠️ Troubleshooting

### Issue: Migration errors
**Solution**: Delete `db.sqlite3` and run migrations again:
```bash
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

### Issue: Static files not loading
**Solution**: Collect static files:
```bash
python manage.py collectstatic
```

### Issue: Module not found errors
**Solution**: Make sure you're in the project root directory and virtual environment is activated.

## 📖 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the admin panel to manage data
- Check out the API endpoints documentation
- Customize the templates and styling

## 💡 Tips

- Use the Django admin panel for quick data management
- API endpoints require authentication (token or session)
- Donors can only see their own data
- Admins have full access to all data

