from django.apps import AppConfig

class WorkforceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.workforce'
    label = 'workforce'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return 
        print(">>> Starting DB keep-alive...")
        try:
            from common.keepalive import start_db_keepalive
            start_db_keepalive()
            print(">>> Keep-alive thread started!")
        except Exception as e:
            print(f">>> Keep-alive FAILED: {e}")