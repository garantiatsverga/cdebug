"""
cdebug - Colorful debugging utilities for Python
Copyright 2024 cdebug Contributors
Licensed under Apache License 2.0 - see LICENSE file for details
"""

import os
import time
import re
import logging
import json
import asyncio
from datetime import datetime
from typing import Optional, Callable, List, Tuple, Union, Any
from functools import wraps

# Global logging settings
LOG_TO_FILE = False
LOG_FILE = "debug.log"
CONSOLE_ENABLED = True
MAX_LOG_LINES = 1000
KEEP_ERROR_LINES = True
LOG_FORMAT = 'text'  # 'text', 'json'
SENSITIVE_KEYS = ['password', 'token', 'api_key', 'secret', 'auth_key', 'credential']

# Show welcome message only once
_SHOW_WELCOME = True

class color:
    """ANSI color codes"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def _show_welcome_message():
    """Show welcome message on first import"""
    global _SHOW_WELCOME
    if _SHOW_WELCOME and CONSOLE_ENABLED:
        print(f"\n{color.BOLD}{color.CYAN}🌟 Welcome to cdebug!{color.END}")
        print(f"{color.CYAN}📚 Repository: {color.BOLD}https://github.com/garantiatsverga/cdebug{color.END}")
        print(f"{color.CYAN}⭐ If you find this library useful, please consider giving it a star!{color.END}")
        print(f"{color.CYAN}🐛 Happy debugging!{color.END}\n")
        _SHOW_WELCOME = False

# Show welcome message immediately on import
_show_welcome_message()

# Configure standard logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cdebug')

def _clean_ansi_codes(text):
    """Remove ANSI color codes from text for log file"""
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    return ansi_escape.sub('', text)

def _sanitize_sensitive_data(data: Any) -> Any:
    """
    Recursively sanitize sensitive data from logs
    Works with strings, dicts, lists, and nested structures
    """
    if isinstance(data, str):
        # Check if string contains sensitive patterns
        for key in SENSITIVE_KEYS:
            if key in data.lower():
                # Simple pattern matching for key-value pairs
                patterns = [
                    rf'"{key}"\s*:\s*"([^"]*)"',  # JSON style
                    rf"{key}\s*=\s*'([^']*)'",    # Python style  
                    rf"{key}\s*=\s*\"([^\"]*)\"", # Python style
                    rf"{key}\s*:\s*([^\s,]+)",    # Key: value
                ]
                for pattern in patterns:
                    data = re.sub(pattern, f'{key}="***"', data, flags=re.IGNORECASE)
        return data
    
    elif isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in str(key).lower() for sensitive in SENSITIVE_KEYS):
                sanitized[key] = "***"
            else:
                sanitized[key] = _sanitize_sensitive_data(value)
        return sanitized
    
    elif isinstance(data, (list, tuple)):
        return [_sanitize_sensitive_data(item) for item in data]
    
    return data

def _format_log_message(level: str, message: str, label: str = "") -> str:
    """Format log message according to selected format"""
    timestamp = datetime.now().isoformat()
    
    if LOG_FORMAT == 'json':
        log_data = {
            "timestamp": timestamp,
            "level": level,
            "label": label,
            "message": _sanitize_sensitive_data(message)
        }
        return json.dumps(log_data, ensure_ascii=False)
    else:
        # Text format
        clean_message = _sanitize_sensitive_data(message)
        return f"[{timestamp}] [{level}] {clean_message}"

def _rotate_logs_if_needed():
    """Rotate logs if they exceed MAX_LOG_LINES, preserving errors and criticals"""
    if not LOG_TO_FILE or not os.path.exists(LOG_FILE):
        return
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if len(lines) <= MAX_LOG_LINES:
            return
        
        if KEEP_ERROR_LINES:
            error_lines = []
            other_lines = []
            
            for line in lines:
                if any(tag in line for tag in ['[ERROR]', '[CRITICAL]']):
                    error_lines.append(line)
                else:
                    other_lines.append(line)
            
            lines_to_keep = error_lines + other_lines[-(MAX_LOG_LINES - len(error_lines)):]
        else:
            lines_to_keep = lines[-MAX_LOG_LINES:]
        
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines_to_keep)
            
        debug(f"Log rotation completed: {len(lines)} -> {len(lines_to_keep)} lines", exp=False)
        
    except Exception as e:
        error(f"Log rotation failed: {e}", exp=False)

def _log_to_file(message: str, level: str = "INFO"):
    """Internal function for writing to log file with smart rotation"""
    if LOG_TO_FILE:
        _rotate_logs_if_needed()
        
        formatted_message = _format_log_message(level, message, level)
        
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                existing_logs = f.readlines()
        except FileNotFoundError:
            existing_logs = []
        
        existing_logs.insert(0, formatted_message + '\n')
        
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.writelines(existing_logs)

def _std_log(level: str, msg: str, *args, **kwargs):
    """Internal function for standard logging"""
    exp = kwargs.pop('exp', False)
    logger_method = getattr(logger, level.lower())
    
    # Sanitize message for standard logging too
    sanitized_msg = _sanitize_sensitive_data(msg)
    logger_method(sanitized_msg, *args, **kwargs)
    
    if exp:
        _log_to_file(sanitized_msg, level)

# Core debug functions
def debug(msg: str, label: str = "DEBUG", label_color: str = color.BLUE, exp: bool = False):
    """Basic debug output"""
    sanitized_msg = _sanitize_sensitive_data(msg)
    
    if CONSOLE_ENABLED:
        console_output = f"{label_color}[{label}]{color.END} {sanitized_msg}"
        print(console_output)
    
    if exp:
        log_output = f"[{label}] {_clean_ansi_codes(sanitized_msg)}"
        _log_to_file(log_output, label)
    
    _std_log('DEBUG', sanitized_msg, exp=exp)

def info(msg: str, exp: bool = False):
    """Information message"""
    debug(msg, "INFO", color.CYAN, exp)

def success(msg: str, exp: bool = False):
    """Success message"""
    debug(msg, "SUCCESS", color.GREEN, exp)

def warning(msg: str, exp: bool = False):
    """Warning message"""
    debug(msg, "WARNING", color.YELLOW, exp)

def error(msg: str, exception: Optional[Exception] = None, exp: bool = False):
    """Error message"""
    full_msg = f"{msg}: {exception}" if exception else msg
    sanitized_msg = _sanitize_sensitive_data(full_msg)
    
    if CONSOLE_ENABLED:
        if exception:
            console_output = f"{color.RED}[ERROR]{color.END} {_sanitize_sensitive_data(msg)}: {exception}"
        else:
            console_output = f"{color.RED}[ERROR]{color.END} {_sanitize_sensitive_data(msg)}"
        print(console_output)
    
    if exp:
        log_output = f"[ERROR] {_clean_ansi_codes(sanitized_msg)}"
        _log_to_file(log_output, "ERROR")
    
    _std_log('ERROR', sanitized_msg, exp=exp)

def critical(msg: str, exp: bool = False):
    """Critical error message"""
    debug(msg, "CRITICAL", color.RED, exp)

# Async versions
async def adebug(msg: str, label: str = "DEBUG", label_color: str = color.BLUE, exp: bool = False):
    """Async basic debug output"""
    debug(msg, label, label_color, exp)

async def ainfo(msg: str, exp: bool = False):
    """Async information message"""
    info(msg, exp)

async def asuccess(msg: str, exp: bool = False):
    """Async success message"""
    success(msg, exp)

async def awarning(msg: str, exp: bool = False):
    """Async warning message"""
    warning(msg, exp)

async def aerror(msg: str, exception: Optional[Exception] = None, exp: bool = False):
    """Async error message"""
    error(msg, exception, exp)

async def acritical(msg: str, exp: bool = False):
    """Async critical error message"""
    critical(msg, exp)

# Advanced logging functions
def log_function_call(exp: bool = False):
    """Decorator to log function calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            debug(f"Calling {func.__name__}", "FUNCTION", color.MAGENTA, exp)
            try:
                result = func(*args, **kwargs)
                debug(f"{func.__name__} completed successfully", "FUNCTION", color.MAGENTA, exp)
                return result
            except Exception as e:
                error(f"{func.__name__} failed", e, exp)
                raise
        return wrapper
    return decorator

def alog_function_call(exp: bool = False):
    """Async decorator to log function calls"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await adebug(f"Calling {func.__name__}", "FUNCTION", color.MAGENTA, exp)
            try:
                result = await func(*args, **kwargs)
                await adebug(f"{func.__name__} completed successfully", "FUNCTION", color.MAGENTA, exp)
                return result
            except Exception as e:
                await aerror(f"{func.__name__} failed", e, exp)
                raise
        return wrapper
    return decorator

def log_execution_time(exp: bool = False):
    """Decorator to log function execution time"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            debug(f"{func.__name__} executed in {elapsed:.3f}s", "PERF", color.CYAN, exp)
            return result
        return wrapper
    return decorator

def alog_execution_time(exp: bool = False):
    """Async decorator to log function execution time"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            await adebug(f"{func.__name__} executed in {elapsed:.3f}s", "PERF", color.CYAN, exp)
            return result
        return wrapper
    return decorator

def log_condition(condition: bool, true_msg: str, false_msg: str = "", exp: bool = False):
    """Log different messages based on condition"""
    if condition:
        success(true_msg, exp)
    elif false_msg:
        warning(false_msg, exp)
    return condition

def log_value(name: str, value: Any, exp: bool = False):
    """Log variable value"""
    debug(f"{name} = {value}", "VALUE", color.BLUE, exp)
    return value

def log_list(items: list, name: str = "List", max_display: int = 10, exp: bool = False):
    """Log list contents"""
    if len(items) <= max_display:
        debug(f"{name}: {items}", "LIST", color.BLUE, exp)
    else:
        debug(f"{name}: {items[:max_display]}... (+{len(items) - max_display} more)", "LIST", color.BLUE, exp)

def log_dict(d: dict, name: str = "Dictionary", max_items: int = 10, exp: bool = False):
    """Log dictionary contents"""
    items = list(d.items())
    if len(items) <= max_items:
        debug(f"{name}: {d}", "DICT", color.BLUE, exp)
    else:
        preview = dict(items[:max_items])
        debug(f"{name}: {preview}... (+{len(items) - max_items} more items)", "DICT", color.BLUE, exp)

# Context manager for timing
class timer:
    """Code execution timer"""
    
    def __init__(self, description: str = "Operation", exp: bool = False):
        self.description = description
        self.exp = exp
    
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        elapsed = time.time() - self.start
        debug(f"{self.description} completed in {elapsed:.2f}s", "TIMER", color.MAGENTA, self.exp)

class atimer:
    """Async code execution timer"""
    
    def __init__(self, description: str = "Operation", exp: bool = False):
        self.description = description
        self.exp = exp
    
    async def __aenter__(self):
        self.start = time.time()
        return self
    
    async def __aexit__(self, *args):
        elapsed = time.time() - self.start
        await adebug(f"{self.description} completed in {elapsed:.2f}s", "TIMER", color.MAGENTA, self.exp)

# Logging management functions
def enable_file_logging(filename: str = "debug.log"):
    """Enable file logging"""
    global LOG_TO_FILE, LOG_FILE
    LOG_TO_FILE = True
    LOG_FILE = filename

def disable_file_logging():
    """Disable file logging"""
    global LOG_TO_FILE
    LOG_TO_FILE = False

def enable_console_output():
    """Enable console output"""
    global CONSOLE_ENABLED
    CONSOLE_ENABLED = True

def disable_console_output():
    """Disable console output"""
    global CONSOLE_ENABLED
    CONSOLE_ENABLED = False

def set_log_level(level: str):
    """Set standard logging level"""
    level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    logger.setLevel(level_map.get(level.lower(), logging.INFO))

def set_log_format(format_type: str = 'text'):
    """Set log format (text or json)"""
    global LOG_FORMAT
    if format_type.lower() in ['text', 'json']:
        LOG_FORMAT = format_type.lower()
        debug(f"Log format set to {LOG_FORMAT}")
    else:
        warning(f"Unsupported log format: {format_type}")

def add_sensitive_keys(keys: List[str]):
    """Add keys to sanitize in logs"""
    global SENSITIVE_KEYS
    SENSITIVE_KEYS.extend([key.lower() for key in keys])
    SENSITIVE_KEYS = list(set(SENSITIVE_KEYS))  # Remove duplicates
    debug(f"Added sensitive keys: {keys}")

def clear_sensitive_keys():
    """Clear all sensitive keys"""
    global SENSITIVE_KEYS
    SENSITIVE_KEYS = []
    debug("Cleared all sensitive keys")

# Rotation management functions
def set_max_log_lines(max_lines: int = 1000):
    """Set maximum number of lines in log file"""
    global MAX_LOG_LINES
    MAX_LOG_LINES = max_lines
    debug(f"Max log lines set to {max_lines}")

def enable_error_preservation(enabled: bool = True):
    """Enable/disable preservation of error lines during rotation"""
    global KEEP_ERROR_LINES
    KEEP_ERROR_LINES = enabled
    debug(f"Error preservation {'enabled' if enabled else 'disabled'}")

def get_log_stats() -> dict:
    """Get statistics about current log file"""
    if not os.path.exists(LOG_FILE):
        return {"total_lines": 0, "error_lines": 0, "critical_lines": 0}
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        error_count = sum(1 for line in lines if '[ERROR]' in line)
        critical_count = sum(1 for line in lines if '[CRITICAL]' in line)
        warning_count = sum(1 for line in lines if '[WARNING]' in line)
        
        return {
            "total_lines": len(lines),
            "error_lines": error_count,
            "critical_lines": critical_count,
            "warning_lines": warning_count,
            "info_lines": len(lines) - error_count - critical_count - warning_count
        }
    except Exception as e:
        error(f"Failed to get log stats: {e}")
        return {}

def force_log_rotation():
    """Manually trigger log rotation"""
    _rotate_logs_if_needed()
    stats = get_log_stats()
    info(f"Manual rotation completed: {stats['total_lines']} lines, "
         f"{stats['error_lines']} errors, {stats['critical_lines']} criticals")

def view_logs(limit: Optional[int] = None):
    """View recent logs from file (most recent first)"""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.readlines()
        
        if limit:
            logs = logs[:limit]
        
        for log in logs:
            print(log, end='')
    except FileNotFoundError:
        print("No log file found")

def clear_logs():
    """Clear all logs from file"""
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")
        info("Logs cleared")
    except FileNotFoundError:
        pass

# Production setup helper
def setup_production_logging(
    log_file: str = "production.log",
    max_lines: int = 1000,
    preserve_errors: bool = True,
    console_output: bool = False,
    log_format: str = 'json',
    sensitive_keys: Optional[List[str]] = None
):
    """Production-ready logging setup"""
    enable_file_logging(log_file)
    set_max_log_lines(max_lines)
    enable_error_preservation(preserve_errors)
    set_log_format(log_format)
    
    if sensitive_keys:
        add_sensitive_keys(sensitive_keys)
    
    if not console_output:
        disable_console_output()
    
    set_log_level('INFO')
    info("Production logging configured", exp=True)