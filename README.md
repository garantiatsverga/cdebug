# colordebug - Colorful Debugging Utilities for Python

A powerful, production-ready logging and debugging library for Python with colorful console output, smart log rotation, security features, async support, and **text wrapping** capabilities.

## Features

- 🎨 **Colorful console output** with ANSI colors
- 📝 **Multiple log formats** (Text, JSON)
- 🔒 **Security-first** - automatic sensitive data sanitization
- ⚡ **Async support** for modern web applications
- 🔄 **Smart log rotation** with error preservation
- 📊 **Performance monitoring** with execution timing
- 🛠 **Flexible configuration** for different environments
- 📜 **Text wrapping** for better log readability

## Installation

```bash
pip install colordebug
```

Or copy `colordebug.py` directly into your project.

## Quick Start

```python
from colordebug import *

# Basic usage
info("Application started")
success("Data loaded successfully")
warning("This is a warning")
error("Something went wrong")

# With file logging
enable_file_logging("app.log")
info("This will be logged to file", exp=True)

# With text wrapping (new!)
long_message = "This is a very long message that will be wrapped to multiple lines for better readability."
info(long_message, exp=True, textwrapping=True, wrapint=40)
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
from colordebug import *

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

## Text Wrapping (New!)

colordebug now supports automatic text wrapping for better log readability.

### Basic Text Wrapping

```python
from colordebug import *

# Enable text wrapping for long messages
long_message = "This is a very long message that should be wrapped to multiple lines based on the specified width."

# Log with text wrapping (width = 40 characters)
info(long_message, exp=True, textwrapping=True, wrapint=40)

# Log without text wrapping
debug(long_message, exp=True, textwrapping=False)
```

### Advanced Usage

```python
# Set default text wrapping for all logs
enable_file_logging("app.log", textwrapping=True, wrapint=80)

# Use with different log levels
warning("This is a warning message that will be wrapped", exp=True, textwrapping=True, wrapint=50)
error("This is an error message that will be wrapped", exp=True, textwrapping=True, wrapint=50)

# Use with decorators
@log_function_call(exp=True, textwrapping=True, wrapint=60)
def process_data(data):
    # Function logic here
    pass
```

### Parameters

- `textwrapping` (bool): Enable or disable text wrapping. Default: `False`
- `wrapint` (int): Maximum line width in characters. Default: `80`

### Notes

- Text wrapping only applies to text format logs (not JSON format)
- Wrapping preserves words and breaks at whitespace when possible
- Very long words that exceed the wrap width will be broken as needed

## Security Features

### Sensitive Data Sanitization

```python
from colordebug import *

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
from colordebug import *

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

colordebug includes smart log rotation that preserves error messages:

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
from colordebug import *
from fastapi import FastAPI

app = FastAPI()
setup_production_logging("api.log", log_format='json', textwrapping=True, wrapint=100)

@app.get("/users/{user_id}")
@log_function_call(exp=True, textwrapping=True, wrapint=100)
async def get_user(user_id: int):
    await ainfo(f"Fetching user {user_id}", exp=True, textwrapping=True, wrapint=100)
    
    async with atimer("Database query", exp=True, textwrapping=True, wrapint=100):
        user = await db.users.find_one(user_id)
    
    if not user:
        await awarning(f"User {user_id} not found", exp=True, textwrapping=True, wrapint=100)
        return {"error": "User not found"}
    
    await asuccess(f"User {user_id} retrieved successfully", exp=True, textwrapping=True, wrapint=100)
    return user
```

### Data Processing

```python
from colordebug import *

@log_function_call(exp=True, textwrapping=True, wrapint=80)
@log_execution_time(exp=True, textwrapping=True, wrapint=80)
def process_dataset(data):
    log_value("dataset_size", len(data), exp=True, textwrapping=True, wrapint=80)
    log_value("data_columns", list(data.columns), exp=True, textwrapping=True, wrapint=80)
    
    with timer("Data cleaning", exp=True, textwrapping=True, wrapint=80):
        cleaned_data = clean_data(data)
    
    log_condition(
        len(cleaned_data) > 0,
        "Data cleaning successful - all data has been processed and validated",
        "No data after cleaning - the dataset appears to be empty",
        exp=True,
        textwrapping=True,
        wrapint=80
    )
    
    return cleaned_data
```

## API Reference

### Core Functions
- `debug(msg, label, label_color, exp, textwrapping, wrapint)`
- `info(msg, exp, textwrapping, wrapint)`
- `success(msg, exp, textwrapping, wrapint)`
- `warning(msg, exp, textwrapping, wrapint)`
- `error(msg, exception, exp, textwrapping, wrapint)`
- `critical(msg, exp, textwrapping, wrapint)`

### Async Functions
- `adebug(msg, label, label_color, exp, textwrapping, wrapint)`
- `ainfo(msg, exp, textwrapping, wrapint)`
- `asuccess(msg, exp, textwrapping, wrapint)`
- `awarning(msg, exp, textwrapping, wrapint)`
- `aerror(msg, exception, exp, textwrapping, wrapint)`
- `acritical(msg, exp, textwrapping, wrapint)`

### Decorators
- `@log_function_call(exp, textwrapping, wrapint)`
- `@alog_function_call(exp, textwrapping, wrapint)`
- `@log_execution_time(exp, textwrapping, wrapint)`
- `@alog_execution_time(exp, textwrapping, wrapint)`

### Context Managers
- `timer(description, exp, textwrapping, wrapint)`
- `atimer(description, exp, textwrapping, wrapint)`

### Configuration
- `enable_file_logging(filename, textwrapping, wrapint)`
- `set_log_format(format_type, textwrapping, wrapint)`
- `add_sensitive_keys(keys, textwrapping, wrapint)`
- `set_max_log_lines(max_lines, textwrapping, wrapint)`
- `set_log_level(level, textwrapping, wrapint)`
- `setup_production_logging(log_file, max_lines, preserve_errors, console_output, log_format, sensitive_keys, textwrapping, wrapint)`

## Best Practices

1. **Use JSON format in production** for better log aggregation
2. **Disable console output in production** to improve performance
3. **Always enable error preservation** to never lose critical errors
4. **Sanitize sensitive data** before logging user input
5. **Use async functions** in web applications for better performance
6. **Enable text wrapping** for better log readability with `textwrapping=True` and `wrapint=80`
7. **Use appropriate wrap width** based on your logging system (80-120 characters recommended)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Python**