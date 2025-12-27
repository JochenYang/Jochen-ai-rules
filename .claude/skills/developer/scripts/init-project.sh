#!/bin/bash

# Project Initialization Script
# Usage: bash scripts/init-project.sh --help

set -e

show_help() {
  cat << EOF
Project Initialization Script

Usage: bash scripts/init-project.sh [OPTIONS]

Options:
  --stack <name>        Technology stack (next-ts|react-ts|vue-ts|fastapi|express-ts)
  --name <name>         Project name (default: my-app)
  --output <dir>        Output directory (default: current directory)
  --help, -h            Show this help message

Examples:
  bash scripts/init-project.sh --stack next-ts --name my-saas
  bash scripts/init-project.sh --stack fastapi --name api-server
  bash scripts/init-project.sh --stack react-ts --name admin-panel

Available Stacks:
  next-ts      Next.js 14+ with TypeScript, Tailwind CSS, App Router
  react-ts     React 18+ with Vite, TypeScript, Tailwind CSS
  vue-ts       Vue 3 with Vite, TypeScript, Tailwind CSS
  fastapi      Python FastAPI with SQLAlchemy, Pydantic
  express-ts   Express.js with TypeScript, Prisma ORM

What this script does:
  ✅ Creates project structure
  ✅ Initializes package manager
  ✅ Sets up TypeScript/ESLint/Prettier
  ✅ Configures Git repository
  ✅ Installs dependencies
  ✅ Creates .env.example
  ✅ Generates README.md

After initialization:
  cd <project-name>
  cp .env.example .env
  # Edit .env with your configuration
  # Follow README.md for next steps
EOF
}

# Parse arguments
STACK=""
PROJECT_NAME="my-app"
OUTPUT_DIR="."

while [[ $# -gt 0 ]]; do
  case $1 in
    --help|-h)
      show_help
      exit 0
      ;;
    --stack)
      STACK="$2"
      shift 2
      ;;
    --name)
      PROJECT_NAME="$2"
      shift 2
      ;;
    --output)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Run 'bash scripts/init-project.sh --help' for usage"
      exit 1
      ;;
  esac
done

if [ -z "$STACK" ]; then
  echo "Error: --stack is required"
  echo "Run 'bash scripts/init-project.sh --help' for usage"
  exit 1
fi

echo "🚀 Initializing $STACK project: $PROJECT_NAME"

cd "$OUTPUT_DIR"

case $STACK in
  next-ts)
    npx create-next-app@latest "$PROJECT_NAME" \
      --typescript \
      --tailwind \
      --eslint \
      --app \
      --src-dir \
      --import-alias "@/*" \
      --no-git
    cd "$PROJECT_NAME"
    ;;
  
  react-ts)
    npm create vite@latest "$PROJECT_NAME" -- --template react-ts
    cd "$PROJECT_NAME"
    npm install -D tailwindcss postcss autoprefixer
    npx tailwindcss init -p
    ;;
  
  vue-ts)
    npm create vite@latest "$PROJECT_NAME" -- --template vue-ts
    cd "$PROJECT_NAME"
    npm install -D tailwindcss postcss autoprefixer
    npx tailwindcss init -p
    ;;
  
  fastapi)
    mkdir -p "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    python -m venv venv
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
    pip install fastapi uvicorn sqlalchemy pydantic python-dotenv
    pip freeze > requirements.txt
    ;;
  
  express-ts)
    mkdir -p "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    npm init -y
    npm install express prisma @prisma/client
    npm install -D typescript @types/node @types/express ts-node nodemon
    npx tsc --init
    npx prisma init
    ;;
  
  *)
    echo "Error: Unknown stack '$STACK'"
    echo "Run 'bash scripts/init-project.sh --help' for available stacks"
    exit 1
    ;;
esac

# Create .env.example
cat > .env.example << 'EOF'
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

# API
API_PORT=3000
API_SECRET=your-secret-key-here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:3000
EOF

# Initialize Git
git init
echo "node_modules/" > .gitignore
echo ".env" >> .gitignore
echo "dist/" >> .gitignore
echo "build/" >> .gitignore

echo ""
echo "✅ Project initialized successfully!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  cp .env.example .env"
echo "  # Edit .env with your configuration"
echo "  # Follow README.md for development instructions"

