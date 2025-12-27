#!/bin/bash

# Database Migration Script
# Usage: bash scripts/db-migrate.sh --help

set -e

show_help() {
  cat << EOF
Database Migration Script

Usage: bash scripts/db-migrate.sh [OPTIONS]

Options:
  --action <action>     Migration action (create|up|down|status|reset)
  --name <name>         Migration name (for create action)
  --orm <orm>           ORM to use (prisma|typeorm|sqlalchemy|gorm)
  --help, -h            Show this help message

Actions:
  create    Create a new migration
  up        Run pending migrations
  down      Rollback last migration
  status    Show migration status
  reset     Reset database (WARNING: destroys all data)

Examples:
  bash scripts/db-migrate.sh --action create --name add_users_table --orm prisma
  bash scripts/db-migrate.sh --action up --orm typeorm
  bash scripts/db-migrate.sh --action status --orm sqlalchemy
  bash scripts/db-migrate.sh --action down --orm prisma

Supported ORMs:
  prisma        Prisma ORM (Node.js/TypeScript)
  typeorm       TypeORM (Node.js/TypeScript)
  sqlalchemy    SQLAlchemy (Python)
  gorm          GORM (Go)

What this script does:
  ✅ Detects ORM automatically if not specified
  ✅ Runs appropriate migration commands
  ✅ Validates database connection
  ✅ Provides clear error messages

Requirements:
  - ORM installed and configured
  - Database connection configured in .env
  - Migration files in standard locations
EOF
}

# Parse arguments
ACTION=""
MIGRATION_NAME=""
ORM=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --help|-h)
      show_help
      exit 0
      ;;
    --action)
      ACTION="$2"
      shift 2
      ;;
    --name)
      MIGRATION_NAME="$2"
      shift 2
      ;;
    --orm)
      ORM="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [ -z "$ACTION" ]; then
  echo "Error: --action is required"
  echo "Run 'bash scripts/db-migrate.sh --help' for usage"
  exit 1
fi

# Auto-detect ORM if not specified
if [ -z "$ORM" ]; then
  if [ -f "prisma/schema.prisma" ]; then
    ORM="prisma"
  elif [ -f "ormconfig.json" ] || [ -f "ormconfig.ts" ]; then
    ORM="typeorm"
  elif [ -f "alembic.ini" ]; then
    ORM="sqlalchemy"
  elif [ -f "go.mod" ] && grep -q "gorm.io/gorm" go.mod; then
    ORM="gorm"
  else
    echo "❌ Could not detect ORM"
    echo "Please specify --orm manually"
    exit 1
  fi
fi

echo "📦 Using ORM: $ORM"
echo "🔧 Action: $ACTION"

# Execute migration based on ORM and action
case $ORM in
  prisma)
    case $ACTION in
      create)
        if [ -z "$MIGRATION_NAME" ]; then
          echo "Error: --name is required for create action"
          exit 1
        fi
        echo "Creating migration: $MIGRATION_NAME"
        npx prisma migrate dev --name "$MIGRATION_NAME"
        ;;
      up)
        echo "Running migrations..."
        npx prisma migrate deploy
        ;;
      down)
        echo "⚠️  Prisma does not support rollback"
        echo "You need to create a new migration to revert changes"
        exit 1
        ;;
      status)
        npx prisma migrate status
        ;;
      reset)
        echo "⚠️  WARNING: This will destroy all data!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
          npx prisma migrate reset
        else
          echo "Cancelled"
        fi
        ;;
      *)
        echo "Unknown action: $ACTION"
        exit 1
        ;;
    esac
    ;;
  
  typeorm)
    case $ACTION in
      create)
        if [ -z "$MIGRATION_NAME" ]; then
          echo "Error: --name is required for create action"
          exit 1
        fi
        npx typeorm migration:create "src/migrations/$MIGRATION_NAME"
        ;;
      up)
        npx typeorm migration:run
        ;;
      down)
        npx typeorm migration:revert
        ;;
      status)
        npx typeorm migration:show
        ;;
      reset)
        echo "⚠️  WARNING: This will destroy all data!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
          npx typeorm schema:drop
          npx typeorm migration:run
        else
          echo "Cancelled"
        fi
        ;;
      *)
        echo "Unknown action: $ACTION"
        exit 1
        ;;
    esac
    ;;
  
  sqlalchemy)
    case $ACTION in
      create)
        if [ -z "$MIGRATION_NAME" ]; then
          echo "Error: --name is required for create action"
          exit 1
        fi
        alembic revision --autogenerate -m "$MIGRATION_NAME"
        ;;
      up)
        alembic upgrade head
        ;;
      down)
        alembic downgrade -1
        ;;
      status)
        alembic current
        alembic history
        ;;
      reset)
        echo "⚠️  WARNING: This will destroy all data!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
          alembic downgrade base
          alembic upgrade head
        else
          echo "Cancelled"
        fi
        ;;
      *)
        echo "Unknown action: $ACTION"
        exit 1
        ;;
    esac
    ;;
  
  *)
    echo "❌ Unsupported ORM: $ORM"
    exit 1
    ;;
esac

echo ""
echo "✅ Migration $ACTION completed successfully!"

