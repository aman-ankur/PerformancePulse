# PerformancePulse

**Performance Data Aggregation Assistant**

PerformancePulse helps managers and team leads quickly gather factual performance data from multiple engineering systems, providing context and objective metrics while leaving interpretation to humans.

## 🎯 What It Does

- **Aggregates Objective Data**: Pulls factual metrics from GitLab, Jira, and other systems
- **Provides Context**: Organizes commits, tickets, and documentation in one place  
- **Saves Time**: Reduces data gathering from hours to minutes
- **Maintains Privacy**: Requires explicit consent from team members
- **Focuses on Facts**: Shows what happened, not why or how well

## 🔒 Privacy & Consent

- **Explicit Consent Required**: Team members must authorize data access
- **Transparent Process**: Clear visibility into what data is collected
- **User Control**: Individuals can revoke access at any time
- **Objective Metrics Only**: Focuses on factual data (commits, tickets, docs)
- **No Interpretation**: Leaves analysis and conclusions to humans

## 📊 What Gets Aggregated

### Technical Contributions
- Commit frequency and scope
- Code review participation
- Documentation contributions
- Technical discussions

### Project Delivery
- Ticket completion rates
- Sprint participation
- Feature delivery timelines
- Bug resolution metrics

### Collaboration Indicators
- Cross-team contributions
- Knowledge sharing activities
- Mentoring and support provided

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- GitLab access token
- Jira workspace access

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/PerformancePulse.git
cd PerformancePulse

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database URL
```

### Environment Setup

```bash
# Frontend (.env.local)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend (.env)
ANTHROPIC_API_KEY=your_claude_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
GITLAB_CLIENT_ID=your_gitlab_client_id
GITLAB_CLIENT_SECRET=your_gitlab_client_secret
```

### Running Locally

```bash
# Start the backend
cd backend
uvicorn main:app --reload

# Start the frontend (in another terminal)
npm run dev
```

Visit `http://localhost:3000` to access the application.

## 🏗️ Architecture

- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: Supabase (PostgreSQL)
- **AI**: Claude 3.5 Sonnet for data categorization
- **Integrations**: GitLab API, Jira MCP

## 📁 Project Structure

```
PerformancePulse/
├── components/          # React components
├── pages/              # Next.js pages
├── lib/                # Utilities and configurations
├── backend/            # FastAPI backend
│   ├── services/       # Integration services
│   ├── models/         # Data models
│   └── api/           # API endpoints
├── memory-bank/        # Project documentation
└── docs/              # Additional documentation
```

## 🔧 Key Features

### Data Aggregation
- **Multi-Source Integration**: Connects to GitLab, Jira, and other tools
- **Automated Collection**: Gathers data on schedule with user consent
- **Smart Categorization**: Uses AI to organize contributions by type

### Insights Dashboard
- **Visual Overview**: Clean, modern interface showing key metrics
- **Time-Based Views**: Weekly, monthly, and quarterly summaries
- **Export Options**: PDF and markdown reports for reviews

### Privacy Controls
- **Granular Permissions**: Users control what data is shared
- **Audit Trail**: Complete log of data access and usage
- **Data Retention**: Configurable retention policies

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/memory-bank` folder for detailed specs
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join our community discussions

## 🗺️ Roadmap

- [x] Core data aggregation from GitLab and Jira
- [x] AI-powered categorization and insights
- [x] Modern, responsive UI
- [ ] Slack integration for team updates
- [ ] Advanced analytics and trends
- [ ] Team collaboration features
- [ ] Mobile app

---

**Note**: PerformancePulse is designed to support performance conversations, not replace them. It provides factual data to help managers and team members have more informed discussions about contributions and growth.
