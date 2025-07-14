# JSON Compare Telegram Bot

A Telegram bot that compares JSON files against a base format schema and provides compliance reports.

## Features

- **JSON Format Validation**: Compares uploaded JSON files against a base schema
- **Detailed Reports**: Provides comprehensive compliance reports with:
  - Missing fields
  - Extra fields
  - Type mismatches
  - List length differences
- **Telegram Integration**: Easy-to-use Telegram bot interface
- **Production Ready**: Dockerized with proper logging and monitoring

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### Deployment

1. **Clone or download the project files**

2. **Configure environment variables**:
   ```bash
   cp .env.production .env
   ```
   Edit `.env` and add your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   ```

3. **Deploy using the deployment script**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

   Or manually with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**:
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to get instructions
3. Upload a JSON file as a document
4. Receive a detailed compliance report

## Example Report

```
=== 1-by-1 JSON Format Compliance Report (Base vs Second JSON) ===

✅ No format differences found. Second JSON fully complies with base JSON.

=== End of Report ===
```

Or with issues:
```
❌ MISSING in second JSON at patient.address.province: expected 'dict'
⚠️ EXTRA in second JSON at patient.extra_field: found 'string' (not in base)
❌ TYPE MISMATCH at patient.birthdate: base 'date' vs target 'string'
```

## Management Commands

- **View logs**: `docker-compose logs -f`
- **Stop bot**: `docker-compose down`
- **Restart bot**: `docker-compose restart`
- **Update and redeploy**: `./deploy.sh`

## Configuration

### Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `BASE_JSON_PATH`: Path to base JSON file (default: visit-sample.json)

### Base JSON Schema

The bot compares uploaded files against `visit-sample.json`. To use a different base schema:

1. Replace `visit-sample.json` with your schema file
2. Update `BASE_JSON_PATH` in `.env` if needed
3. Redeploy: `./deploy.sh`

## Architecture

- **Language**: Python 3.11
- **Framework**: python-telegram-bot
- **Deployment**: Docker + Docker Compose
- **Logging**: JSON structured logs with rotation
- **Health Checks**: Built-in container health monitoring

## Production Features

- **Security**: Non-root user execution
- **Resource Limits**: Memory and CPU constraints
- **Auto-restart**: Automatic container restart on failure
- **Log Rotation**: Automatic log file rotation
- **Health Monitoring**: Built-in health checks

## Troubleshooting

### Bot not responding
```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f

# Restart bot
docker-compose restart
```

### Invalid token error
1. Get a new token from [@BotFather](https://t.me/BotFather)
2. Update `.env` file
3. Redeploy: `./deploy.sh`

### Memory issues
- Increase memory limits in `docker-compose.yml`
- Monitor with: `docker stats`

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_token

# Run locally
python compare_json_bot.py
```

### File Structure
```
.
├── compare_json_bot.py    # Main bot application
├── compare_json.py        # CLI version for testing
├── visit-sample.json      # Base JSON schema
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Production deployment
├── deploy.sh            # Deployment script
└── README.md           # This file
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Verify your bot token is correct
3. Ensure the base JSON file is valid
4. Check container resource usage

## Security Notes

- The bot runs as a non-root user
- Environment variables are used for sensitive data
- Container resources are limited
- No data is stored persistently by default
