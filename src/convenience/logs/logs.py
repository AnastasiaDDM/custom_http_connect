import asyncio
from datetime import datetime as dt
import logging
import multiprocessing
import os
import sys
import textwrap
import threading
from traceback import format_exception
import json


SERVICE = os.environ.get('CONVENIENCE_LOGS_SERVICE')
VERSION = os.environ.get('CONVENIENCE_LOGS_VERSION')
BUILD_NUMBER = os.environ.get('CONVENIENCE_LOGS_BUILD_NUMBER')


stderr_lock = threading.RLock()

if int(os.environ.get('CONVENIENCE_LOGS_DEVELOPMENT', '0')) != 0:
    def write_line(line):
        with stderr_lock:
            sys.stderr.write(f'''{line['timestamp']} {line['level']}\n''')
            sys.stderr.write(
                f'''    service: {line['service']} {line['version']} {line['build_number']}\n'''
            )
            sys.stderr.write(f'''    module: {line['module']}\n''')
            sys.stderr.write(f'''    line: {line['line']}\n''')
            sys.stderr.write(f'''    process: {line['process_ID']} {line['process_name']}\n'''),
            sys.stderr.write(f'''    thread: {line['thread_ID']} {line['thread_name']}\n'''),
            sys.stderr.write(f'''    task: {line['task_ID']} {line['task_name']}\n'''),
            sys.stderr.write(f'''    message: {line['message']}\n''')
            sys.stderr.write(f'''    arguments: {line['arguments']}\n''')

            if 'exception' in line:
                sys.stderr.write(f'''    exception: {line['exception']}\n''')

                if 'traceback' in line:
                    sys.stderr.write('\n')
                    sys.stderr.write(textwrap.indent(line['traceback'], '    '))

            sys.stderr.write('\n')
            sys.stderr.flush()
else:
    def write_line(line):
        with stderr_lock:
            sys.stderr.write(str(line) + '\n')
            sys.stderr.flush()


def log(level, frame, message, *, exception=None, traceback=None, **kwargs):
    process = multiprocessing.current_process()
    thread = threading.current_thread()

    try:
        task = asyncio.current_task()
    except RuntimeError:
        task = None

    if task is None:
        task_ID = None
        task_name = None
    else:
        task_ID = id(task)
        task_name = task.get_name()

    line = {
        'service': SERVICE,
        'version': VERSION,
        'build_number': BUILD_NUMBER,
        'timestamp': str(dt.now()),
        'module': frame.f_globals['__name__'],
        'line': frame.f_lineno,
        'level': level,
        'process_ID': process.pid,
        'process_name': process.name,
        'thread_ID': thread.native_id,
        'thread_name': thread.name,
        'task_ID': task_ID,
        'task_name': task_name,
        'message': message,
        'arguments': kwargs
    }

    if exception is not None:
        line['exception'] = repr(exception)
        line['traceback'] = ''.join(format_exception(None, exception, traceback))

    write_line(line)


def debug(message, **kwargs):
    log('debug', sys._getframe().f_back, message, **kwargs)


def info(message, **kwargs):
    log('info', sys._getframe().f_back, message, **kwargs)


def warning(message, **kwargs):
    log('warning', sys._getframe().f_back, message, **kwargs)


def error(message, **kwargs):
    log('error', sys._getframe().f_back, message, **kwargs)


def exception_caught(message, **kwargs):
    exception_type, exception, traceback = sys.exc_info()
    log(
        'error',
        sys._getframe().f_back,
        message,
        exception=exception,
        traceback=traceback,
        **kwargs
    )


# Для поддержки логирования в библиотеках типа Uvicorn
class Handler(logging.Handler):
    def handle(self, record):
        if record.levelno < logging.DEBUG:
            return

        if record.levelno < logging.INFO:
            level = 'debug'
        elif record.levelno < logging.WARNING:
            level = 'info'
        elif record.levelno < logging.ERROR:
            level = 'warning'
        else:
            level = 'error'

        frame = sys._getframe()
        module = 'logging'
        previous_module = None

        while frame is not None:
            module = frame.f_globals['__name__']

            if module != 'logging' and previous_module == 'logging':
                break

            frame = frame.f_back
            previous_module = module

        process = multiprocessing.current_process()
        thread = threading.current_thread()

        try:
            task = asyncio.current_task()
        except RuntimeError:
            task = None

        if task is None:
            task_ID = None
            task_name = None
        else:
            task_ID = id(task)
            task_name = task.get_name()

        line = {
            'service': SERVICE,
            'version': VERSION,
            'build_number': BUILD_NUMBER,
            'timestamp': str(dt.fromtimestamp(record.created)),
            'module': module,
            'line': record.lineno,
            'level': level,
            'process_ID': process.pid,
            'process_name': process.name,
            'thread_ID': thread.native_id,
            'thread_name': thread.name,
            'task_ID': task_ID,
            'task_name': task_name,
            # Uvicorn иногда передаёт не строки в качестве сообщения
            'message': str(record.msg) % record.args,
            'arguments': {}
        }

        if isinstance(record.exc_info, tuple | list):
            if record.exc_info[1] is not None:
                line['exception'] = repr(record.exc_info[1])
                line['traceback'] = ''.join(format_exception(*record.exc_info))
        # Uvicorn передаёт само исключение, а не кортеж
        elif isinstance(record.exc_info, BaseException):
            line['exception'] = repr(record.exc_info)

            exception_type, exception, traceback = sys.exc_info()

            if exception is record.exc_info and traceback is not None:
                line['traceback'] = ''.join(format_exception(exception_type, exception, traceback))

        write_line(line)


logging.root.setLevel('DEBUG')
logging.basicConfig(handlers=[Handler()])
