# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import csv
import os
import logging
from io import StringIO

__all__ = ['app']

LF = '%(process)s %(thread)s [%(asctime)s] %(levelname)s %(name)s %(message)s'
log_file = os.environ.get('WSGI_LOG_FILE')
log_level = os.environ.get('LOG_LEVEL', 'ERROR')
if log_file:
    logging.basicConfig(level=getattr(logging, log_level), format=LF,
        filename=log_file)

if not log_file:
    # Logging must be set before importing
    logging_config = os.environ.get('TRYTOND_LOGGING_CONFIG')
    logging_level = int(os.environ.get(
            'TRYTOND_LOGGING_LEVEL', default=logging.ERROR))
    if logging_config:
        logging.config.fileConfig(logging_config)
    else:
        logformat = ('%(process)s %(thread)s [%(asctime)s] '
            '%(levelname)s %(name)s %(message)s')
        level = max(logging_level, logging.NOTSET)
        logging.basicConfig(level=level, format=logformat)
    logging.captureWarnings(True)

if os.environ.get('TRYTOND_COROUTINE'):
    from gevent import monkey
    monkey.patch_all()

from trytond.pool import Pool
from trytond.wsgi import app

Pool.start()
# TRYTOND_CONFIG it's managed by importing config
db_names = os.environ.get('TRYTOND_DATABASE_NAMES')
if db_names:
    # Read with csv so database name can include special chars
    reader = csv.reader(StringIO(db_names))
    for name in next(reader):
        threading.Thread(target=Pool(name).init).start()
