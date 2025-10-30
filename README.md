# RealtorOS - CRM for Real Estate Agents

A full-stack CRM system designed specifically for real estate agents, featuring automated follow-up scheduling, AI-powered email generation, and comprehensive client management.

## 🚀 Features

- **Client Management**: Complete CRUD operations for real estate clients
- **Automated Follow-ups**: Intelligent scheduling system with predefined follow-up sequences
- **AI Email Generation**: OpenAI-powered personalized email content
- **Email Automation**: SendGrid integration for reliable email delivery
- **Task Management**: Track and manage follow-up tasks and their completion
- **Dashboard Analytics**: Comprehensive insights and performance metrics
- **Real-time Updates**: Live data synchronization across the application

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: Flexible NoSQL database for client and task data
- **Celery + Redis**: Asynchronous task processing and message queuing
- **OpenAI API**: AI-powered email content generation
- **SendGrid**: Reliable email delivery service

### Frontend (Next.js + React)
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling framework
- **SWR**: Data fetching and caching
- **Axios**: HTTP client for API communication

## 📁 Project Structure

```
realtoros/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes and dependencies
│   │   ├── services/       # Business logic services
│   │   ├── models/         # MongoDB document models
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── tasks/          # Celery task definitions
│   │   ├── db/             # Database configuration
│   │   ├── utils/          # Utility functions
│   │   └── constants/      # Application constants
│   ├── tests/              # Unit and integration tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container config
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utility libraries
│   │   ├── styles/        # CSS and styling
│   │   └── types/         # TypeScript type definitions
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile         # Frontend container config
├── docker-compose.yml     # Multi-container orchestration
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd realtoros
   ```

2. **Set up environment variables**
   ```bash
   # Backend environment
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys
   
   # Frontend environment
   cp frontend/.env.example frontend/.env.local
   # Edit frontend/.env.local if needed
   ```

3. **Required API Keys**
   - OpenAI API Key (for email generation)
   - SendGrid API Key (for email delivery)

### Docker Development

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **Seed demo data**
   ```bash
   docker exec realtoros-backend python -m app.db.seed
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Start supporting services**
   ```bash
   # MongoDB
   docker run -d -p 27017:27017 --name mongo mongo:6.0
   
   # Redis
   docker run -d -p 6379:6379 --name redis redis:7.0-alpine
   ```

## 📚 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Clients
- `GET /api/clients` - List all clients
- `POST /api/clients` - Create new client
- `GET /api/clients/{id}` - Get client details
- `PATCH /api/clients/{id}` - Update client
- `DELETE /api/clients/{id}` - Delete client

#### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PATCH /api/tasks/{id}` - Update task

#### Emails
- `GET /api/emails` - List email history
- `POST /api/emails/preview` - Preview generated email
- `POST /api/emails/send` - Send email

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
MONGODB_URL=mongodb://mongo:27017
MONGODB_DB=realtoros

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# External APIs
OPENAI_API_KEY=your_openai_key
SENDGRID_API_KEY=your_sendgrid_key

# Security
SECRET_KEY=your-secret-key
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Deployment

### Production Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Individual Service Deployment
- **Backend**: Deploy to AWS ECS, DigitalOcean App Platform, or Railway
- **Frontend**: Deploy to Vercel, Netlify, or AWS S3 + CloudFront
- **Database**: Use MongoDB Atlas for production
- **Cache**: Use Redis Cloud or AWS ElastiCache

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation at `/docs`
- Review the API documentation at `/api/docs`

## 🗺️ Roadmap

### Phase 1 (Current)
- [x] Basic client management
- [x] Task scheduling system
- [x] Email generation and sending
- [x] Dashboard and analytics

### Phase 2 (Next)
- [ ] Email analytics (opens, clicks)
- [ ] Advanced task rescheduling
- [ ] Bulk operations
- [ ] Data export capabilities

### Phase 3 (Future)
- [ ] User authentication and authorization
- [ ] Multi-user support
- [ ] Custom email templates
- [ ] SMS follow-ups
- [ ] Calendar integration
- [ ] Mobile application

---

Built with ❤️ for real estate professionals
