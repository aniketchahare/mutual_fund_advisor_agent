# Database Setup Guide

## Overview
The Mutual Fund Advisor now uses `DatabaseSessionService` instead of `InMemorySessionService` for persistent session storage. This allows sessions to persist across application restarts and provides better data management.

## Database Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Database Configuration
DATABASE_URL=sqlite:///mutual_fund_advisor.db
DATABASE_ECHO=False

# Logging Configuration
LOG_LEVEL=INFO

# Gradio Configuration
GRADIO_SHARE=False
GRADIO_INBROWSER=True
GRADIO_SHOW_ERROR=True
GRADIO_SHOW_API=False

# OpenAI API Key (required for the agent)
OPENAI_API_KEY=your_openai_api_key_here
```

### Supported Database Types

#### 1. SQLite (Default - Recommended for Development)
```bash
DATABASE_URL=sqlite:///mutual_fund_advisor.db
```
- **Pros**: No setup required, file-based, portable
- **Cons**: Not suitable for production with multiple users
- **Use Case**: Development, testing, single-user scenarios

#### 2. PostgreSQL (Recommended for Production)
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/mutual_fund_advisor
```
- **Pros**: Robust, scalable, ACID compliant
- **Cons**: Requires PostgreSQL installation
- **Use Case**: Production environments, multi-user scenarios

#### 3. MySQL
```bash
DATABASE_URL=mysql://username:password@localhost:3306/mutual_fund_advisor
```
- **Pros**: Widely supported, good performance
- **Cons**: Requires MySQL installation
- **Use Case**: Production environments

## Installation Steps

### For SQLite (Default)
No additional installation required. The database file will be created automatically.

### For PostgreSQL
1. Install PostgreSQL on your system
2. Create a database:
   ```sql
   CREATE DATABASE mutual_fund_advisor;
   ```
3. Install the Python driver:
   ```bash
   pip install psycopg2-binary
   ```
4. Update your `.env` file with PostgreSQL connection details

### For MySQL
1. Install MySQL on your system
2. Create a database:
   ```sql
   CREATE DATABASE mutual_fund_advisor;
   ```
3. Install the Python driver:
   ```bash
   pip install mysqlclient
   ```
4. Update your `.env` file with MySQL connection details

## Usage

### Starting the Application

```bash
# CLI interface (default)
python main.py

# Web interface
python main.py --gradio

# Show help
python main.py --help
```

### CLI Commands

When using the CLI interface, you have access to these commands:

- `help` - Show available commands
- `status` - Show current session status and database info
- `sessions` - List all your sessions stored in the database
- `clear` - Clear conversation history (resets session state)
- `exit` or `quit` - End the conversation

### Session Management

Sessions are now automatically stored in the database and will persist across:
- Application restarts
- System reboots
- Multiple user sessions

Each session contains:
- User profile information
- Investment goals
- Fund recommendations
- SIP calculations
- Conversation history

## Database Schema

The `DatabaseSessionService` automatically creates the necessary tables:

- `sessions` - Stores session metadata and state
- `session_states` - Stores session state data as JSON

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check your `DATABASE_URL` format
   - Ensure the database server is running (for PostgreSQL/MySQL)
   - Verify credentials and permissions

2. **Permission Errors**
   - Ensure the application has write permissions to the database directory
   - For SQLite, check file permissions in the project directory

3. **SQLAlchemy Errors**
   - Enable `DATABASE_ECHO=True` to see SQL queries
   - Check the logs for detailed error messages

### Debug Mode

To enable debug logging and SQL query logging:

```bash
DATABASE_ECHO=True
LOG_LEVEL=DEBUG
```

### Database File Location

- **SQLite**: `mutual_fund_advisor.db` in the project root directory
- **PostgreSQL/MySQL**: As specified in the connection string

## Migration from InMemorySessionService

If you were previously using `InMemorySessionService`, your sessions will not be automatically migrated. The new database will start fresh with new sessions.

## Security Considerations

1. **Database Security**
   - Use strong passwords for database connections
   - Restrict database access to necessary users only
   - Consider using connection pooling for production

2. **Data Privacy**
   - Session data contains user information
   - Implement appropriate data retention policies
   - Consider encryption for sensitive data

3. **Backup Strategy**
   - Regularly backup your database
   - Test backup and restore procedures
   - Store backups securely

## Performance Tips

1. **SQLite**
   - Suitable for development and single-user scenarios
   - Consider switching to PostgreSQL for production

2. **PostgreSQL/MySQL**
   - Use connection pooling for better performance
   - Monitor database performance
   - Consider indexing for large datasets

3. **General**
   - Monitor session cleanup and retention
   - Implement session timeout policies
   - Regular database maintenance 