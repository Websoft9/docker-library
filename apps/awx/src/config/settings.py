import socket
import uuid


hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
DEBUG = True
SECRET_KEY = "XzFwTFZnM0NSLUhWMHdybEVPaEQ="
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1",
                        f"http://{ip_address}", 'f"http://{ip_address}:8052"', 'http://127.0.0.1:8052']
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)
ALLOWED_HOSTS = ['127.0.0.1', '*']
AWX_AUTO_DEPROVISION_INSTANCES = True
SYSTEM_UUID = str(uuid.uuid4())

BROADCAST_WEBSOCKET_PROTOCOL = 'http'
BROADCAST_WEBSOCKET_VERIFY_CERT = False
BROADCAST_WEBSOCKET_PORT = '8052'

# 是否启用k8s
RECEPTOR_RELEASE_WORK = False
