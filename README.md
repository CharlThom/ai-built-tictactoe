# TicTacToe Monorepo

A modern TicTacToe application built with TypeScript, React, and pnpm workspaces.

## Project Structure


.
├── packages/
│   ├── frontend/          # React frontend application
│   └── shared/            # Shared utilities and types
├── docker-compose.dev.yml # Development environment
├── Dockerfile.dev         # Development Docker image
└── pnpm-workspace.yaml    # Workspace configuration


## Prerequisites

- Node.js 18+ and pnpm 8+
- Docker and Docker Compose (for containerized development)

## Local Development Setup

### Option 1: Native Development

1. **Install dependencies:**
   bash
   pnpm install
   

2. **Start development server:**
   bash
   pnpm --filter frontend dev
   

3. **Access the application:**
   - Frontend: http://localhost:5173

### Option 2: Docker Development (Recommended)

1. **Start development environment:**
   bash
   docker-compose -f docker-compose.dev.yml up
   

2. **Access the application:**
   - Frontend: http://localhost:5173

3. **Stop environment:**
   bash
   docker-compose -f docker-compose.dev.yml down
   

**Hot-reload is enabled** - changes to source files will automatically refresh the application.

## Available Scripts

- `pnpm install` - Install all dependencies
- `pnpm --filter <package> dev` - Start development server for a package
- `pnpm --filter <package> build` - Build a package for production
- `pnpm lint` - Run ESLint across all packages
- `pnpm format` - Format code with Prettier
- `pnpm type-check` - Run TypeScript type checking

## Code Quality

- **ESLint** - Linting with shared configuration
- **Prettier** - Code formatting
- **Husky** - Pre-commit hooks for automated checks
- **TypeScript** - Type safety with shared tsconfig

### Pre-commit Hooks

The following checks run automatically before each commit:
- Linting (ESLint)
- Code formatting (Prettier)
- Type checking (TypeScript)

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes (hot-reload will update automatically)
3. Commit changes (pre-commit hooks will run)
4. Push and create a pull request

## Troubleshooting

**Port already in use:**
bash
# Find and kill process using port 5173
lsof -ti:5173 | xargs kill -9


**Docker volume issues:**
bash
# Remove volumes and rebuild
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build


**Dependency issues:**
bash
# Clean install
rm -rf node_modules packages/*/node_modules
pnpm install


## Contributing

1. Follow the existing code style
2. Ensure all pre-commit hooks pass
3. Write meaningful commit messages
4. Update documentation as needed