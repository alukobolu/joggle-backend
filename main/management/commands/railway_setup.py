from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Setup Django app for Railway deployment'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Setting up Django app for Railway...')
        
        try:
            # Collect static files
            self.stdout.write('📁 Collecting static files...')
            call_command('collectstatic', '--noinput', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✅ Static files collected'))
            
            # Run migrations
            self.stdout.write('🗄️ Running database migrations...')
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✅ Migrations completed'))
            
            self.stdout.write(self.style.SUCCESS('🎉 Railway setup completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Setup failed: {str(e)}'))
            raise
