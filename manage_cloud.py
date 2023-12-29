#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import ssl

from django.core.management import execute_from_command_line

CERTIFICATE_PATH = './certs/galaxystream_online_ssl.crt'
PRIVATE_KEY_PATH = './certs/galaxystream_online_ssl.key'

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
ssl_context.load_cert_chain(CERTIFICATE_PATH, PRIVATE_KEY_PATH)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_auth.settings_cloud')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv, ssl_context=ssl_context)


if __name__ == '__main__':
    main()
