#!/bin/bash

# Web bundle size analysis and optimization
# Usage: ./optimize-bundle.sh [--analyze] [--minify] [--tree-shake]

set -e

ACTION="analyze"

while [[ $# -gt 0 ]]; do
    case $1 in
        --analyze)
            ACTION="analyze"
            shift
            ;;
        --minify)
            ACTION="minify"
            shift
            ;;
        --tree-shake)
            ACTION="tree-shake"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

analyze_bundle() {
    echo "Analyzing bundle size..."

    if command -v webpack-bundle-analyzer &> /dev/null; then
        npx webpack-bundle-analyzer stats.json
    elif command -v esbuild &> /dev/null; then
        npx esbuild --bundle --metafile=meta.json --analyze
    elif command -v rollup &> /dev/null; then
        npx rollup -c --environment ANALYZE
    else
        echo "No bundle analyzer found. Install: webpack-bundle-analyzer or esbuild"
    fi

    if [ -f "stats.json" ]; then
        echo ""
        echo "Bundle Analysis:"
        echo "================"
        jq -r '.assets[] | "\(.name): \(.size / 1024 | floor)KB"' stats.json 2>/dev/null || cat stats.json
    fi
}

minify_bundle() {
    echo "Minifying bundle..."

    if command -v esbuild &> /dev/null; then
        npx esbuild src/index.js --bundle --minify --outfile=dist/bundle.min.js
    elif command -v terser &> /dev/null; then
        terser dist/bundle.js -o dist/bundle.min.js --compress --mangle
    elif command -v uglifyjs &> /dev/null; then
        uglifyjs dist/bundle.js -o dist/bundle.min.js
    else
        echo "No minifier found. Install: esbuild or terser"
    fi
}

enable_tree_shaking() {
    echo "Enabling tree shaking..."

    if [ -f "package.json" ]; then
        local has_side_effects
        has_side_effects=$(grep -A10 '"sideEffects"' package.json 2>/dev/null || echo "")

        if [ -z "$has_side_effects" ]; then
            echo "Adding sideEffects field to package.json..."
            node -e "
                const pkg = require('./package.json');
                pkg.sideEffects = false;
                require('fs').writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
            "
        fi
    fi

    if [ -f "webpack.config.js" ]; then
        echo "Optimizing webpack config for tree shaking..."
        node -e "
            const config = require('./webpack.config.js');
            config.optimization.usedExports = true;
            require('fs').writeFileSync('webpack.config.js', 'module.exports = ' + JSON.stringify(config, null, 2));
        "
    fi
}

main() {
    case $ACTION in
        analyze)
            analyze_bundle
            ;;
        minify)
            minify_bundle
            ;;
        tree-shake)
            enable_tree_shaking
            ;;
    esac
}

main
