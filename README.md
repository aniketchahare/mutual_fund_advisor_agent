# Mutual Fund Investment Advisor

A comprehensive mutual fund investment platform consisting of two main components: an AI-powered Python agent server for intelligent investment advice and a Node.js API server for fund management and transactions.

## 🏗️ Project Structure

```
mutual-fund-app/
├── mf-python-agent-server/     # AI-powered investment advisor
│   ├── mutual_fund_advisor_agent/
│   │   ├── agent.py            # Main agent orchestrator
│   │   ├── schemas.py          # Centralized data schemas
│   │   └── sub_agents/         # Specialized AI agents
│   ├── main.py                 # Main application entry point
│   ├── api_server.py           # FastAPI server
│   ├── utils.py                # Utility functions
│   ├── requirements.txt        # Python dependencies
│   ├── SCHEMA_DOCUMENTATION.md # Schema documentation
│   └── DATABASE_SETUP.md       # Database setup guide
├── mf-node-api-server/         # Fund management API
│   ├── config/                 # Database configuration
│   ├── controllers/            # Request handlers
│   ├── middleware/             # Custom middleware
│   ├── models/                 # Data models
│   ├── routes/                 # API routes
│   ├── services/               # Business logic
│   ├── uploads/                # File uploads
│   ├── server.js               # Express server entry point
│   └── package.json            # Node.js dependencies
└── README.md                   # This file
```

## 🚀 Features

### Python Agent Server (`mf-python-agent-server`)
- **AI-Powered Investment Advisor**: Uses Google ADK (Agent Development Kit) for intelligent conversations
- **Multi-Agent Architecture**: Specialized agents for different investment aspects
  - User Profile Agent: Collects and analyzes user information
  - Investor Classifier Agent: Determines investor type and risk profile
  - Goal Planner Agent: Helps set investment goals
  - Fund Recommender Agent: Suggests suitable mutual funds
  - SIP Calculator Agent: Calculates SIP investments
  - Investment Agent: Handles investment execution
- **Gradio Web Interface**: User-friendly chat interface
- **Session Management**: Persistent conversation history
- **Database Integration**: SQLite for session storage

### Node.js API Server (`mf-node-api-server`)
- **RESTful API**: Complete fund management system
- **User Management**: Authentication and user profiles
- **Fund Operations**: CRUD operations for mutual funds
- **Transaction Management**: Investment and withdrawal tracking
- **File Upload**: Excel file processing for fund data
- **MongoDB Integration**: Scalable data storage

## 🛠️ Technology Stack

### Python Agent Server
- **Framework**: FastAPI, Gradio
- **AI/ML**: Google ADK, Google Generative AI
- **Database**: SQLite
- **Key Libraries**: 
  - `google-adk`: Agent Development Kit
  - `google-generativeai`: AI model integration
  - `gradio`: Web interface
  - `fastapi`: API framework
  - `sqlalchemy`: Database ORM

### Node.js API Server
- **Framework**: Express.js
- **Database**: MongoDB with Mongoose
- **Authentication**: JWT, bcryptjs
- **File Processing**: multer, xlsx
- **Key Libraries**:
  - `express`: Web framework
  - `mongoose`: MongoDB ODM
  - `jsonwebtoken`: JWT authentication
  - `bcryptjs`: Password hashing
  - `multer`: File upload handling

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB (for Node.js server)
- Google Cloud Platform account (for AI services)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd mutual-fund-app
```

### 2. Python Agent Server Setup

```bash
cd mf-python-agent-server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Google Cloud credentials
```

### 3. Node.js API Server Setup

```bash
cd mf-node-api-server

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your MongoDB connection string and JWT secret
```

### 4. Database Setup

#### MongoDB (for Node.js server)
```bash
# Start MongoDB service
mongod

# The application will automatically create collections on first run
```

#### SQLite (for Python agent - auto-created)
The Python agent server will automatically create the SQLite database on first run.

## 🔧 Configuration

### Environment Variables

#### Python Agent Server (`.env`)
```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CLOUD_PROJECT=your_project_id
DATABASE_URL=sqlite:///./mutual_fund_advisor.db
```

#### Node.js API Server (`.env`)
```env
PORT=3000
MONGODB_URI=mongodb://localhost:27017/mutual_fund_db
JWT_SECRET=your_jwt_secret_key
NODE_ENV=development
```

## 🏃‍♂️ Running the Application

### Start Python Agent Server
```bash
cd mf-python-agent-server
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run with Gradio interface
python main.py

# Or run FastAPI server
python api_server.py
```

### Start Node.js API Server
```bash
cd mf-node-api-server

# Development mode
npm run dev

# Production mode
npm start
```

## 📚 API Documentation

### Python Agent Server Endpoints
- **Gradio Interface**: `http://localhost:7860` (default)
- **FastAPI Docs**: `http://localhost:8000/docs`

### Node.js API Server Endpoints
- **Base URL**: `http://localhost:3000`
- **API Routes**:
  - `/api/users` - User management
  - `/api/funds` - Fund operations
  - `/api/transactions` - Transaction management

## 🤖 AI Agent Architecture

The Python agent server uses a sophisticated multi-agent architecture:

1. **Root Agent**: Orchestrates the conversation flow
2. **User Profile Agent**: Collects user information and preferences
3. **Investor Classifier Agent**: Determines investor type and risk tolerance
4. **Goal Planner Agent**: Helps set and plan investment goals
5. **Fund Recommender Agent**: Suggests suitable mutual funds
6. **SIP Calculator Agent**: Calculates SIP investments
7. **Investment Agent**: Handles investment execution

Each agent specializes in a specific domain and communicates through structured schemas defined in `schemas.py`.

## 📊 Data Schemas

The application uses centralized schemas for consistency:

- **UserProfileOutput**: User information and preferences
- **InvestorTypeOutput**: Investor classification and risk profile
- **InvestmentGoalOutput**: Investment goals and planning
- **FundRecommendationOutput**: Fund recommendations with reasoning
- **SIPCalculatorOutput**: SIP calculation results
- **InvestmentDetailsOutput**: Investment execution details

See `SCHEMA_DOCUMENTATION.md` for detailed schema information.

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation and sanitization
- Environment variable protection

## 📝 Usage Examples

### Using the AI Advisor
1. Start the Python agent server
2. Open the Gradio interface at `http://localhost:7860`
3. Start a conversation with the AI advisor
4. Follow the guided investment planning process

### Using the API
```bash
# Get all funds
curl http://localhost:3000/api/funds

# Create a user
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "password": "password123"}'
```

## 🧪 Testing

### Python Agent Server
```bash
cd mf-python-agent-server
python -m pytest tests/
```

### Node.js API Server
```bash
cd mf-node-api-server
npm test
```

## 📦 Deployment

### Python Agent Server
```bash
# Using uvicorn for production
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### Node.js API Server
```bash
# Set NODE_ENV=production
NODE_ENV=production npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the ISC License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation in each component directory
- Review the schema documentation
- Open an issue on the repository

## 🔄 Version History

- **v1.0.0**: Initial release with basic AI advisor and API server
- Multi-agent architecture for investment advice
- Complete fund management API
- User authentication and session management 