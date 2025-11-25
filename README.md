# CDebug - Colorful Debugging Utilities for Python

A powerful, production-ready logging and debugging library for Python with colorful console output, smart log rotation, security features, and async support.

## Features

- 🎨 **Colorful console output** with ANSI colors
- 📝 **Multiple log formats** (Text, JSON)
- 🔒 **Security-first** - automatic sensitive data sanitization
- ⚡ **Async support** for modern web applications
- 🔄 **Smart log rotation** with error preservation
- 📊 **Performance monitoring** with execution timing
- 🛠 **Flexible configuration** for different environments

## Installation

```bash
pip install cdebug
```

Or copy `cdebug.py` directly into your project.

## Quick Start

```python
from cdebug import *

# Basic usage
info("Application started")
success("Data loaded successfully")
warning("This is a warning")
error("Something went wrong")

# With file logging
enable_file_logging("app.log")
info("This will be logged to file", exp=True)
```

## Core Functions

### Basic Logging

```python
debug("Debug message")
info("Information message")
success("Success message") 
warning("Warning message")
error("Error message")
critical("Critical message")

# With exceptions
try:
    risky_operation()
except Exception as e:
    error("Operation failed", e, exp=True)
```

### Advanced Logging

```python
# Log variable values
log_value("user_count", 42, exp=True)

# Log collections
log_list([1, 2, 3, 4, 5], "Sample data", exp=True)
log_dict({"key": "value"}, "Configuration", exp=True)

# Conditional logging
log_condition(len(users) > 0, "Users found", "No users found", exp=True)
```

### Timing and Performance

```python
# Context manager for timing
with timer("Database query", exp=True):
    results = db.query(...)

# Function decorators
@log_function_call(exp=True)
@log_execution_time(exp=True)
def process_data(data):
    return data * 2
```

## Async Support

```python
import asyncio
from cdebug import *

@alog_function_call(exp=True)
@alog_execution_time(exp=True)
async def fetch_data(url):
    await ainfo(f"Fetching {url}", exp=True)
    
    async with atimer("HTTP request", exp=True):
        await asyncio.sleep(0.1)
    
    await asuccess("Data fetched successfully", exp=True)
    return {"data": "sample"}

# Usage
async def main():
    await fetch_data("https://api.example.com/data")
```

## Security Features

### Sensitive Data Sanitization

```python
from cdebug import *

# Add custom sensitive keys
add_sensitive_keys(['credit_card', 'social_security', 'private_key'])

# Sensitive data is automatically masked
user_data = {
    "username": "john_doe",
    "password": "super_secret",
    "credit_card": "4111-1111-1111-1111",
    "normal_data": "this is safe"
}

log_dict(user_data, "User registration", exp=True)
# Output: password="***", credit_card="***", normal_data="this is safe"
```

**Default sensitive keys:** `password`, `token`, `api_key`, `secret`, `auth_key`, `credential`

## Configuration

### Production Setup

```python
from cdebug import *

setup_production_logging(
    log_file="production.log",
    max_lines=5000,
    preserve_errors=True,
    console_output=False,  # Disable console in production
    log_format='json',     # Use JSON for log aggregation
    sensitive_keys=['jwt_token', 'encryption_key']
)
```

### Manual Configuration

```python
# File logging
enable_file_logging("app.log")
set_max_log_lines(1000)           # Rotate after 1000 lines
enable_error_preservation(True)   # Keep all errors during rotation

# Log format
set_log_format('json')  # or 'text'

# Console control
disable_console_output()  # Only file logging
enable_console_output()   # Restore console output

# Log levels
set_log_level('info')  # debug, info, warning, error, critical
```

## Log Rotation

CDebug includes smart log rotation that preserves error messages:

```python
set_max_log_lines(1000)  # Keep maximum 1000 lines

# Errors and critical messages are never deleted during rotation
enable_error_preservation(True)  # Default behavior
```

### Monitoring

```python
# Get log statistics
stats = get_log_stats()
print(f"Total lines: {stats['total_lines']}")
print(f"Errors: {stats['error_lines']}")
print(f"Critical: {stats['critical_lines']}")

# Manual rotation
force_log_rotation()

# View logs
view_logs(limit=10)  # Show 10 most recent entries
```

## Log Formats

### Text Format (Default)
```
[2024-01-15T10:30:00] [INFO] User logged in successfully
[2024-01-15T10:30:01] [ERROR] Database connection failed: timeout
```

### JSON Format
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "level": "INFO",
  "message": "User logged in successfully"
}
{
  "timestamp": "2024-01-15T10:30:01", 
  "level": "ERROR",
  "message": "Database connection failed: timeout"
}
```

## Real-world Examples

### Web Application

```python
from cdebug import *
from fastapi import FastAPI

app = FastAPI()
setup_production_logging("api.log", log_format='json')

@app.get("/users/{user_id}")
@log_function_call(exp=True)
async def get_user(user_id: int):
    await ainfo(f"Fetching user {user_id}", exp=True)
    
    async with atimer("Database query", exp=True):
        user = await db.users.find_one(user_id)
    
    if not user:
        await awarning(f"User {user_id} not found", exp=True)
        return {"error": "User not found"}
    
    await asuccess(f"User {user_id} retrieved", exp=True)
    return user
```

### Data Processing

```python
from cdebug import *

@log_function_call(exp=True)
@log_execution_time(exp=True)
def process_dataset(data):
    log_value("dataset_size", len(data), exp=True)
    log_value("data_columns", list(data.columns), exp=True)
    
    with timer("Data cleaning", exp=True):
        cleaned_data = clean_data(data)
    
    log_condition(
        len(cleaned_data) > 0,
        "Data cleaning successful",
        "No data after cleaning",
        exp=True
    )
    
    return cleaned_data
```

## API Reference

### Core Functions
- `debug(msg, label, label_color, exp)`
- `info(msg, exp)`
- `success(msg, exp)`
- `warning(msg, exp)`
- `error(msg, exception, exp)`
- `critical(msg, exp)`

### Async Functions
- `adebug(msg, label, label_color, exp)`
- `ainfo(msg, exp)`
- `asuccess(msg, exp)`
- `awarning(msg, exp)`
- `aerror(msg, exception, exp)`
- `acritical(msg, exp)`

### Decorators
- `@log_function_call(exp)`
- `@alog_function_call(exp)`
- `@log_execution_time(exp)`
- `@alog_execution_time(exp)`

### Context Managers
- `timer(description, exp)`
- `atimer(description, exp)`

### Configuration
- `enable_file_logging(filename)`
- `set_log_format(format_type)`
- `add_sensitive_keys(keys)`
- `set_max_log_lines(max_lines)`
- `set_log_level(level)`

## Best Practices

1. **Use JSON format in production** for better log aggregation
2. **Disable console output in production** to improve performance
3. **Always enable error preservation** to never lose critical errors
4. **Sanitize sensitive data** before logging user input
5. **Use async functions** in web applications for better performance

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Python**