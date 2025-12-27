#!/bin/bash

# Bundle Optimization Script
# Usage: bash scripts/optimize-bundle.sh --help

set -e

show_help() {
  cat << EOF
Bundle Optimization Script

Usage: bash scripts/optimize-bundle.sh [OPTIONS]

Options:
  --analyze             Generate bundle analysis report
  --build               Build optimized production bundle
  --check               Check bundle size against limits
  --help, -h            Show this help message

Examples:
  bash scripts/optimize-bundle.sh --analyze
  bash scripts/optimize-bundle.sh --build
  bash scripts/optimize-bundle.sh --check

What this script does:
  ✅ Detects build tool (Vite/Webpack/Next.js)
  ✅ Builds optimized production bundle
  ✅ Generates bundle analysis report
  ✅ Checks bundle size against recommended limits
  ✅ Provides optimization suggestions

Bundle Size Limits:
  - Initial JS bundle: < 200 KB (gzipped)
  - Total JS: < 500 KB (gzipped)
  - CSS: < 50 KB (gzipped)
  - Images: Use WebP/AVIF, lazy loading

Requirements:
  - Build tool configured (Vite/Webpack/Next.js)
  - package.json with build scripts
  - Node.js installed
EOF
}

# Parse arguments
ANALYZE=false
BUILD=false
CHECK=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --help|-h)
      show_help
      exit 0
      ;;
    --analyze)
      ANALYZE=true
      shift
      ;;
    --build)
      BUILD=true
      shift
      ;;
    --check)
      CHECK=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Detect build tool
if [ -f "next.config.js" ] || [ -f "next.config.mjs" ]; then
  BUILD_TOOL="next"
elif [ -f "vite.config.ts" ] || [ -f "vite.config.js" ]; then
  BUILD_TOOL="vite"
elif [ -f "webpack.config.js" ]; then
  BUILD_TOOL="webpack"
else
  echo "❌ Could not detect build tool"
  exit 1
fi

echo "📦 Detected build tool: $BUILD_TOOL"

# Build production bundle
if [ "$BUILD" = true ] || [ "$ANALYZE" = true ]; then
  echo "🔨 Building production bundle..."
  
  case $BUILD_TOOL in
    next)
      npm run build
      ;;
    vite)
      npm run build
      ;;
    webpack)
      npm run build
      ;;
  esac
  
  echo "✅ Build complete"
fi

# Generate bundle analysis
if [ "$ANALYZE" = true ]; then
  echo "📊 Generating bundle analysis..."
  
  case $BUILD_TOOL in
    next)
      # Install analyzer if not present
      if ! grep -q "@next/bundle-analyzer" package.json; then
        npm install --save-dev @next/bundle-analyzer
      fi
      
      # Run with analyzer
      ANALYZE=true npm run build
      echo "📄 Open .next/analyze/client.html to view report"
      ;;
    
    vite)
      # Install rollup-plugin-visualizer if not present
      if ! grep -q "rollup-plugin-visualizer" package.json; then
        npm install --save-dev rollup-plugin-visualizer
      fi
      
      npm run build
      echo "📄 Open stats.html to view report"
      ;;
    
    webpack)
      # Install webpack-bundle-analyzer if not present
      if ! grep -q "webpack-bundle-analyzer" package.json; then
        npm install --save-dev webpack-bundle-analyzer
      fi
      
      npm run build -- --analyze
      echo "📄 Bundle analyzer will open in browser"
      ;;
  esac
fi

# Check bundle sizes
if [ "$CHECK" = true ]; then
  echo "🔍 Checking bundle sizes..."
  
  case $BUILD_TOOL in
    next)
      BUILD_DIR=".next"
      ;;
    vite)
      BUILD_DIR="dist"
      ;;
    webpack)
      BUILD_DIR="dist"
      ;;
  esac
  
  if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build directory not found. Run with --build first"
    exit 1
  fi
  
  # Find and check JS bundles
  echo ""
  echo "JavaScript Bundles:"
  echo "-------------------"
  
  find "$BUILD_DIR" -name "*.js" -type f | while read file; do
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    size_kb=$((size / 1024))
    
    # Check if gzip is available
    if command -v gzip &> /dev/null; then
      gzip_size=$(gzip -c "$file" | wc -c)
      gzip_kb=$((gzip_size / 1024))
      
      status="✅"
      if [ $gzip_kb -gt 200 ]; then
        status="⚠️"
      fi
      
      echo "$status $(basename "$file"): ${size_kb} KB (${gzip_kb} KB gzipped)"
    else
      echo "$(basename "$file"): ${size_kb} KB"
    fi
  done
  
  # Find and check CSS bundles
  echo ""
  echo "CSS Bundles:"
  echo "------------"
  
  find "$BUILD_DIR" -name "*.css" -type f | while read file; do
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    size_kb=$((size / 1024))
    
    if command -v gzip &> /dev/null; then
      gzip_size=$(gzip -c "$file" | wc -c)
      gzip_kb=$((gzip_size / 1024))
      
      status="✅"
      if [ $gzip_kb -gt 50 ]; then
        status="⚠️"
      fi
      
      echo "$status $(basename "$file"): ${size_kb} KB (${gzip_kb} KB gzipped)"
    else
      echo "$(basename "$file"): ${size_kb} KB"
    fi
  done
  
  echo ""
  echo "Optimization Tips:"
  echo "------------------"
  echo "1. Use code splitting and lazy loading"
  echo "2. Remove unused dependencies"
  echo "3. Use tree shaking"
  echo "4. Compress images (WebP/AVIF)"
  echo "5. Enable gzip/brotli compression"
  echo "6. Use CDN for large libraries"
  echo ""
  echo "Run with --analyze to see detailed bundle composition"
fi

echo ""
echo "✅ Bundle optimization complete!"

