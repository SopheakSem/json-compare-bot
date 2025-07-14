#!/usr/bin/env python3
"""
Health check script for JSON Compare Bot
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

def check_logs():
    """Check if the bot is logging properly"""
    log_file = Path("logs/bot.log")
    if not log_file.exists():
        return False, "Log file not found"
    
    try:
        # Check if there are recent log entries (within last 5 minutes)
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return False, "No log entries found"
        
        # Parse the last log entry timestamp
        last_line = lines[-1]
        if not last_line.strip():
            return False, "Empty log file"
        
        return True, f"Last log entry: {last_line.strip()[:100]}..."
    
    except Exception as e:
        return False, f"Error reading log file: {e}"

def check_base_json():
    """Check if base JSON file exists and is valid"""
    base_path = os.getenv("BASE_JSON_PATH", "visit-sample.json")
    
    if not Path(base_path).exists():
        return False, f"Base JSON file not found: {base_path}"
    
    try:
        with open(base_path, 'r') as f:
            json.load(f)
        return True, f"Base JSON file is valid: {base_path}"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in base file: {e}"
    except Exception as e:
        return False, f"Error reading base file: {e}"

def check_environment():
    """Check environment variables"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        return False, "TELEGRAM_BOT_TOKEN not set"
    
    # Don't log the actual token, just check it exists and has reasonable length
    if len(token) < 30:
        return False, "TELEGRAM_BOT_TOKEN seems too short"
    
    return True, "Environment variables OK"

def check_disk_space():
    """Check available disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)
        
        if free_gb < 1:  # Less than 1GB free
            return False, f"Low disk space: {free_gb:.2f}GB free"
        
        return True, f"Disk space OK: {free_gb:.2f}GB free"
    except Exception as e:
        return False, f"Error checking disk space: {e}"

def main():
    """Run all health checks"""
    print("🔍 JSON Compare Bot Health Check")
    print("=" * 40)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Base JSON File", check_base_json),
        ("Log Files", check_logs),
        ("Disk Space", check_disk_space),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {check_name}: {message}")
            
            if not passed:
                all_passed = False
                
        except Exception as e:
            print(f"❌ FAIL {check_name}: Exception - {e}")
            all_passed = False
    
    print("=" * 40)
    
    if all_passed:
        print("🎉 All health checks passed!")
        return 0
    else:
        print("⚠️  Some health checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
