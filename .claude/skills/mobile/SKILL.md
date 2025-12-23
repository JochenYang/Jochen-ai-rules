---
name: mobile
description: Mobile app development for iOS, Android, and cross-platform solutions. Handles Flutter, React Native, Swift, and Kotlin development with focus on performance, offline-first architecture, and native integrations.
license: MIT
compatibility: Requires mobile development SDKs (Xcode for iOS, Android Studio for Android, Flutter SDK, or React Native CLI).
allowed-tools: Read Write Bash
---

# Mobile Development Expert

Deep mobile development, focusing on performance optimization and complex native features. Suitable for mobile performance bottlenecks, cross-platform optimization, or tasks requiring deep mobile expertise.

## Core Capabilities

- Flutter/React Native cross-platform development
- iOS Swift/SwiftUI native development
- Android Kotlin/Jetpack Compose native development
- Mobile UI adaptation and gesture interactions
- Offline storage and data synchronization
- Push notifications and background tasks

## Tech Stack

| Category         | Technologies                      |
|------------------|-----------------------------------|
| Cross-Platform   | Flutter, React Native, Expo       |
| iOS              | Swift, SwiftUI, UIKit             |
| Android          | Kotlin, Jetpack Compose, XML      |
| State Management | Provider, Riverpod, Redux, MobX   |
| Storage          | SQLite, Realm, Hive, AsyncStorage |

## Design Guidelines

### No Gradients Policy

❌ **Absolutely Forbidden**:
- Linear gradient backgrounds
- Gradient button effects
- Rainbow color decorations

✅ **Correct Approach**:
- Use solid color design
- Build depth through shadows and layers
- Follow Material Design / Human Interface Guidelines

### Platform Adaptation

- iOS: Follow Human Interface Guidelines
- Android: Follow Material Design 3
- Adapt to different screen sizes and densities

## Performance Optimization

- List virtualization (FlatList/ListView)
- Image caching and lazy loading
- Reduce re-renders
- Memory management and leak detection

## Offline-First

- Local data caching
- Offline operation queue
- Network status detection
- Data synchronization strategy

## Boundaries

Focus on mobile app development, not backend API or web frontend.

## Detailed References

- `../designer/guides/design-system.md` - Design system guide
- `../performance-optimizer/workflows/performance-optimization.md` - Performance optimization workflow
