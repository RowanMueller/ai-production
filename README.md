# 🤖 AI Production - Intelligent Stock Analysis Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-18.2.0-61dafb.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A comprehensive AI-powered stock analysis platform featuring machine learning predictions, intelligent chatbot assistance, and portfolio management tools. Built with modern microservices architecture using React, Node.js, and Python.

## 🚀 Features

### 📈 Stock Price Prediction
- **ML-powered forecasting** using advanced algorithms
- **Technical analysis** with multiple indicators
- **Historical data analysis** with interactive charts
- **Real-time market data** integration

### 🤖 AI Chatbot Assistant
- **Natural language processing** for stock queries
- **Contextual responses** based on market data
- **Investment advice** and portfolio insights
- **Real-time market updates**

### 📊 Portfolio Analysis
- **Portfolio optimization** algorithms
- **Risk assessment** and diversification analysis
- **Performance tracking** with detailed metrics
- **Investment recommendations**

### 🎯 Task Management
- **AI-powered task prioritization**
- **Smart scheduling** based on market conditions
- **Progress tracking** and analytics
- **Integration** with trading activities

## 🏗️ Architecture

```
AI_Production/
├── 🎨 frontend/                 # React application with Tailwind CSS
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/             # Application pages
│   │   └── api.js             # API integration
│   └── package.json
├── ⚙️ backend/                  # Node.js Express server
│   ├── routes/                # API endpoints
│   ├── middleware/            # Custom middleware
│   └── server.js              # Main server file
├── 🧠 ai-services/             # Python AI/ML services
│   ├── services/              # AI service modules
│   ├── models/                # ML models
│   ├── data/                  # Data collection and storage
│   └── requirements.txt       # Python dependencies
└── 🐳 docker-compose.yml      # Container orchestration
```

## 🛠️ Technology Stack

### Frontend
- **React 18.2.0** - Modern UI framework
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Data visualization library
- **Framer Motion** - Animation library
- **Axios** - HTTP client
- **React Router** - Client-side routing

### Backend
- **Node.js** - JavaScript runtime
- **Express.js** - Web framework
- **Socket.io** - Real-time communication
- **Helmet** - Security middleware
- **Morgan** - HTTP request logger
- **Joi** - Data validation

### AI Services
- **Python 3.9+** - AI/ML development
- **Flask** - Web framework
- **Pandas** - Data manipulation
- **Scikit-learn** - Machine learning
- **TensorFlow/Keras** - Deep learning
- **YFinance** - Financial data
- **NLTK** - Natural language processing

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Git** - Version control

## 🚀 Quick Start

### Prerequisites
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- [Node.js](https://nodejs.org/) 18+ (for local development)
- [Python](https://www.python.org/) 3.9+ (for local development)
- [Git](https://git-scm.com/)

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-production.git
   cd ai-production
   ```

2. **Build and run with Docker**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - 🌐 **Frontend**: http://localhost:3000
   - 🔧 **Backend API**: http://localhost:5000
   - 🧠 **AI Services**: http://localhost:8000

### Option 2: Local Development

1. **Backend Setup**
   ```bash
   cd backend
   npm install
   npm run dev
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **AI Services Setup**
   ```bash
   cd ai-services
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

## 📚 API Documentation

### Stock Prediction
- `POST /api/predict` - Predict stock prices
- `GET /api/stocks` - Get available stocks
- `GET /api/history/:symbol` - Get historical data

### Chatbot
- `POST /api/chat` - Send message to chatbot
- `GET /api/chat/history` - Get chat history

### Task Prioritizer
- `POST /api/tasks` - Create new task
- `GET /api/tasks` - Get prioritized tasks
- `PUT /api/tasks/:id` - Update task

## Technologies Used

- **Frontend**: React, Tailwind CSS, Axios
- **Backend**: Node.js, Express, Socket.io
- **AI Services**: Python, pandas, scikit-learn, TensorFlow
- **Database**: MongoDB (optional)
- **Containerization**: Docker, Docker Compose 