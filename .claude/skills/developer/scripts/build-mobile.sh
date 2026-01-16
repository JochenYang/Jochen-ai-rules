#!/bin/bash

# Mobile app build script for iOS and Android
# Usage: ./build-mobile.sh --platform <ios|android> [--release] [--profile]

set -e

PLATFORM=""
BUILD_TYPE="debug"
PROFILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --release)
            BUILD_TYPE="release"
            shift
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$PLATFORM" ]; then
    echo "Error: Platform is required"
    echo "Usage: ./build-mobile.sh --platform <ios|android> [--release] [--profile <name>]"
    exit 1
fi

detect_framework() {
    if [ -f "pubspec.yaml" ]; then
        echo "flutter"
    elif [ -f "package.json" ]; then
        if grep -q "react-native" package.json 2>/dev/null; then
            echo "react-native"
        elif grep -q "expo" package.json 2>/dev/null; then
            echo "expo"
        else
            echo "unknown"
        fi
    elif [ -f "ios/Podfile" ]; then
        echo "ios-native"
    elif [ -f "build.gradle" ] || [ -f "settings.gradle" ]; then
        echo "android-native"
    else
        echo "unknown"
    fi
}

build_flutter() {
    local mode="$1"

    if ! command -v flutter &> /dev/null; then
        echo "Flutter not found. Install from: https://flutter.dev"
        exit 1
    fi

    echo "Building Flutter app for $PLATFORM ($mode)..."

    flutter pub get

    case $PLATFORM in
        ios)
            flutter build ipa --$mode
            ;;
        android)
            if [ "$mode" = "release" ]; then
                flutter build appbundle
            else
                flutter build apk
            fi
            ;;
        *)
            echo "Unsupported platform: $PLATFORM"
            exit 1
            ;;
    esac

    echo "Build output:"
    ls -la build/$PLATFORM/ 2>/dev/null || ls -la build/outputs/ 2>/dev/null
}

build_react_native() {
    local mode="$1"

    echo "Building React Native app for $PLATFORM ($mode)..."

    if ! command -v react-native &> /dev/null; then
        echo "React Native CLI not found. Run: npm install -g react-native-cli"
        exit 1
    fi

    case $PLATFORM in
        ios)
            cd ios
            if [ ! -f "Podfile" ]; then
                pod init
            fi
            pod install
            xcodebuild -workspace $PROJECT_NAME.xcworkspace \
                       -scheme $PROJECT_NAME \
                       -configuration $mode \
                       -sdk iphonesimulator \
                       build
            ;;
        android)
            cd android
            ./gradlew assemble$mode
            ;;
        *)
            echo "Unsupported platform: $PLATFORM"
            exit 1
            ;;
    esac
}

build_expo() {
    local mode="$1"

    echo "Building Expo app for $PLATFORM ($mode)..."

    if ! command -v eas &> /dev/null; then
        echo "Expo CLI not found. Run: npm install -g expo-cli"
        exit 1
    fi

    if [ "$mode" = "release" ]; then
        eas build --platform $PLATFORM
    else
        eas build --platform $PLATFORM --profile development
    fi
}

build_ios_native() {
    local mode="$1"

    echo "Building native iOS app ($mode)..."

    if ! command -v xcodebuild &> /dev/null; then
        echo "Xcode command line tools not found"
        exit 1
    fi

    if [ ! -f "ios/Podfile" ]; then
        echo "No Podfile found. Run: pod install"
        exit 1
    fi

    cd ios
    pod install

    xcodebuild -workspace $PROJECT_NAME.xcworkspace \
               -scheme $PROJECT_NAME \
               -configuration $mode \
               -sdk iphonesimulator \
               -destination 'generic/platform=iOS Simulator' \
               build

    cd ..
}

build_android_native() {
    local mode="$1"

    echo "Building native Android app ($mode)..."

    if ! command -v ./gradlew &> /dev/null; then
        echo "Gradle wrapper not found"
        exit 1
    fi

    if [ "$mode" = "release" ]; then
        ./gradlew assembleRelease
    else
        ./gradlew assembleDebug
    fi
}

print_summary() {
    local framework="$1"
    local mode="$2"

    echo ""
    echo "========================================"
    echo "Build Summary"
    echo "========================================"
    echo "Framework: $framework"
    echo "Platform: $PLATFORM"
    echo "Mode: $mode"
    echo ""

    echo "Output locations:"
    case $PLATFORM in
        ios)
            if [ "$mode" = "release" ]; then
                echo "  - .ipa: build/ios/ipa/"
                echo "  - .xcarchive: build/ios/archive/"
            else
                echo "  - .app: build/ios/iphonesimulator/"
            fi
            ;;
        android)
            if [ "$mode" = "release" ]; then
                echo "  - .aab: build/app/outputs/bundle/release/"
            else
                echo "  - .apk: build/app/outputs/debug/"
            fi
            ;;
    esac
}

main() {
    local framework
    framework=$(detect_framework)
    local mode
    mode=$(echo "$BUILD_TYPE" | sed 's/.*/\u&/')

    echo "Detected framework: $framework"
    echo "Platform: $PLATFORM"
    echo "Build type: $mode"
    echo "========================================"

    case $framework in
        flutter)
            build_flutter "$mode"
            ;;
        react-native)
            build_react_native "$mode"
            ;;
        expo)
            build_expo "$mode"
            ;;
        ios-native)
            build_ios_native "$mode"
            ;;
        android-native)
            build_android_native "$mode"
            ;;
        *)
            echo "Unknown framework. Supported: Flutter, React Native, Expo, Native iOS/Android"
            exit 1
            ;;
    esac

    print_summary "$framework" "$mode"
}

main
