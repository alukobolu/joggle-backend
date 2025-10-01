# Railway Deployment Guide for Joggle Backend

This guide will help you deploy your Django Joggle backend to Railway.

## Prerequisites

1. A Railway account (sign up at [railway.app](https://railway.app))
2. Git repository with your code
3. GitHub account (for easy deployment)

## Deployment Steps

### 1. Prepare Your Repository

Your project is already configured with the necessary files:
- `Procfile` - Tells Railway how to start your app
- `requirements.txt` - Lists all Python dependencies
- `runtime.txt` - Specifies Python version
- `railway.json` - Railway-specific configuration

### 2. Deploy to Railway

#### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Connect to Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect it's a Python/Django project

#### Option B: Deploy via Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize and deploy**:
   ```bash
   railway init
   railway up
   ```

### 3. Configure Environment Variables

In your Railway dashboard, go to your project → Variables tab and add:

#### Required Variables:
```
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.railway.app
USE_SQLITE=true
```

#### Database Options:

**Option A: Use SQLite (Quick Start)**
```
USE_SQLITE=true
```
- No additional database setup required
- Data is stored in the container (will be lost on redeployment)
- Good for testing and development

**Option B: Use PostgreSQL (Production Ready)**
```
USE_SQLITE=false
```
- Add PostgreSQL database in Railway dashboard
- Railway will automatically provide a `DATABASE_URL` variable
- Data persists across deployments

#### Optional Variables:
```
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.railway.app
```

### 4. Database Setup

#### For SQLite (Quick Start):
- No additional setup required
- Your app will use SQLite automatically
- Database file will be created at `/app/db.sqlite3`

#### For PostgreSQL (Production):
1. In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically set up the `DATABASE_URL` environment variable
3. Set `USE_SQLITE=false` in your environment variables

### 5. Run Database Migrations

Railway will automatically run migrations during deployment, but you can also run them manually:

1. Go to your project in Railway dashboard
2. Click on "Deployments" tab
3. Click on the latest deployment
4. Go to "Logs" tab to see if migrations ran successfully

If migrations fail, you can run them manually:
```bash
railway run python manage.py migrate
```

### 6. Create a Superuser (Optional)

To access Django admin, create a superuser:
```bash
railway run python manage.py createsuperuser
```

### 7. Verify Deployment

1. Your app will be available at `https://your-app-name.railway.app`
2. Test the API endpoints:
   - `GET https://your-app-name.railway.app/main/` - List projects
   - `GET https://your-app-name.railway.app/account/` - User endpoints
   - `GET https://your-app-name.railway.app/admin/` - Django admin

## Configuration Details

### Static Files
- Static files are served by WhiteNoise middleware
- No additional configuration needed for basic static files
- Files are automatically compressed and cached

### Database
- Automatically switches from SQLite to PostgreSQL in production
- Uses `dj-database-url` to parse Railway's DATABASE_URL
- Migrations run automatically during deployment

### Security
- `DEBUG=False` in production
- `SESSION_COOKIE_SECURE=True` when not in debug mode
- CORS and CSRF origins configurable via environment variables

### Logging
- Logs are available in Railway dashboard under "Logs" tab
- Gunicorn is configured to log to stdout

## Important Notes About SQLite on Railway

⚠️ **SQLite Limitations on Railway:**

1. **Data Persistence**: SQLite files are stored in the container's filesystem, which means:
   - Data will be **lost** when you redeploy your app
   - Data will be **lost** if Railway restarts your container
   - Data will be **lost** if you make changes to your code and redeploy

2. **Concurrent Access**: SQLite has limited concurrent write capabilities, which can cause issues with multiple users

3. **Production Recommendation**: For production apps with real users, PostgreSQL is strongly recommended

4. **When to Use SQLite**: 
   - ✅ Development and testing
   - ✅ Prototyping
   - ✅ Apps with no critical data persistence needs
   - ❌ Production apps with user data
   - ❌ Apps that need data to survive deployments

**Migration Path**: When you're ready to move to PostgreSQL:
1. Add PostgreSQL database in Railway
2. Set `USE_SQLITE=false` in environment variables
3. Run migrations to create PostgreSQL tables
4. Your app will automatically switch to PostgreSQL

## Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check `requirements.txt` has all dependencies
   - Verify Python version in `runtime.txt`

2. **Database Connection Errors**:
   - For PostgreSQL: Ensure database is added to your project and `DATABASE_URL` is set
   - For SQLite: Check that `USE_SQLITE=true` is set in environment variables

3. **Static Files Not Loading**:
   - Verify WhiteNoise is in `INSTALLED_APPS` (it's added as middleware)
   - Check `STATIC_ROOT` and `STATIC_URL` settings

4. **CORS Errors**:
   - Update `CORS_ALLOWED_ORIGINS` environment variable
   - Include your frontend domain

### Useful Commands:

```bash
# View logs
railway logs

# Run Django shell
railway run python manage.py shell

# Run migrations manually
railway run python manage.py migrate

# Collect static files
railway run python manage.py collectstatic

# Create superuser
railway run python manage.py createsuperuser
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Django secret key |
| `DEBUG` | No | True | Debug mode |
| `ALLOWED_HOSTS` | No | localhost,127.0.0.1 | Comma-separated list of allowed hosts |
| `USE_SQLITE` | No | auto | Set to 'true' to use SQLite, 'false' for PostgreSQL |
| `DATABASE_URL` | Auto | - | PostgreSQL connection string (set by Railway when using PostgreSQL) |
| `CORS_ALLOWED_ORIGINS` | No | localhost origins | Comma-separated list of CORS origins |
| `CSRF_TRUSTED_ORIGINS` | No | localhost origins | Comma-separated list of CSRF trusted origins |

## Next Steps

1. **Domain Setup**: Configure a custom domain in Railway dashboard
2. **SSL Certificate**: Railway provides free SSL certificates
3. **Monitoring**: Set up monitoring and alerts
4. **Backup**: Configure automated database backups
5. **Frontend Integration**: Update your frontend to use the Railway URL

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Django Deployment: [docs.djangoproject.com/en/stable/howto/deployment/](https://docs.djangoproject.com/en/stable/howto/deployment/)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
