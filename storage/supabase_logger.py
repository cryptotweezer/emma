"""
Supabase Logger — registra actividad de agentes y del bot en agent_logs
"""
import os

try:
    from supabase import create_client
    _client = None

    def _get_client():
        global _client
        if _client is None:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_ANON_KEY')
            if url and key:
                _client = create_client(url, key)
        return _client

    def log_agent_activity(
        agent_name: str,
        task_description: str,
        model_used: str = 'emma-bot',
        status: str = 'completed'
    ):
        """Registra actividad en Supabase agent_logs. Nunca rompe el bot."""
        try:
            client = _get_client()
            if client is None:
                return
            client.table('agent_logs').insert({
                'agent_name': agent_name,
                'task_description': task_description,
                'model_used': model_used,
                'status': status,
            }).execute()
        except Exception:
            pass  # Supabase logging nunca debe interrumpir el bot

except ImportError:
    def log_agent_activity(*args, **kwargs):
        pass  # Si supabase no está instalado, no hace nada
