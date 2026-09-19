"""
Gunicorn configuration for production.

Reference: https://docs.gunicorn.org/en/stable/configure.html
"""
import multiprocessing

# Server socket
bind = '0.0.0.0:8000'

# Workers
# Formula: (2 × CPU) + 1
# For t3.micro (1 vCPU) = 3 workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'

# Use /dev/shm for worker heartbeat files
# Avoids issues with read-only filesystems
worker_tmp_dir = '/dev/shm'

# Timeouts
timeout = 60          # kill worker if request takes longer than 60s
keepalive = 5         # keep connections alive for 5s

# Recycle workers periodically to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging — write to stdout so Docker captures it
accesslog  = '-'
errorlog   = '-'
loglevel   = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(D)sµs'

# Process naming
proc_name = 'portfolio_cms'

# Prevent slowloris attacks
limit_request_line   = 4096
limit_request_fields = 100