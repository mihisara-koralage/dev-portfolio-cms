# Developer Portfolio CMS

A production-ready Content Management System for managing a developer portfolio, 
built with Django, Docker, PostgreSQL, and deployed on AWS using Terraform and GitHub Actions CI/CD.

## Tech Stack

**Backend:** Django · Django REST Framework · PostgreSQL · Redis  
**Frontend:** HTML · CSS · JavaScript · Tailwind CSS  
**DevOps:** Docker · Docker Compose · Nginx · GitHub Actions  
**Cloud:** AWS EC2 · S3 · CloudWatch · Route 53  
**IaC:** Terraform  

## Project Status

🚧 In active development

## Architecture

*(Architecture diagram coming soon)*

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+

### Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/dev-portfolio-cms.git
cd dev-portfolio-cms
cp .env.example .env
# Edit .env with your values
make build
make up
make migrate
make createsuperuser
```

Visit `http://localhost:8000`

## License

MIT