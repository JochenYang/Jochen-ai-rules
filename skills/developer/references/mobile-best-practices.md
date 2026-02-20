# Mobile Development Best Practices

Guidelines for building quality mobile applications.

## Platform Guidelines

### iOS (Human Interface Guidelines)
- Navigation bar at top, tab bar at bottom
- Back gesture from left edge
- Standard swipe gestures
- Large touch targets (44x44pt minimum)
- Safe area layout for notches

### Android (Material Design)
- Navigation drawer or bottom navigation
- System back button handling
- Material Design components
- Support for different screen densities
- Dark theme support

## Architecture

### Clean Architecture Layers
```
Presentation (UI/ViewModels)
    ↓
Domain (Use Cases/Entities)
    ↓
Data (Repositories/Data Sources)
```

### State Management
```dart
// Provider pattern
class CounterModel with ChangeNotifier {
  int _count = 0;
  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }
}
```

## Performance

### Optimization Checklist
- Minimize main thread blocking
- Use lazy loading for lists
- Implement image caching
- Optimize database queries
- Compress network payloads

### Battery Optimization
```kotlin
// Use WorkManager for background tasks
val workRequest = PeriodicWorkRequestBuilder<SyncWorker>(
  15, TimeUnit.MINUTES
).build()

WorkManager.getInstance(context).enqueue(workRequest);
```

## Offline-First

### Data Sync Strategy
```typescript
interface Syncable {
  id: string;
  lastModified: Date;
  syncStatus: 'synced' | 'pending' | 'conflict';
}

// Queue for offline operations
class OfflineQueue {
  private queue: Operation[] = [];

  add(operation: Operation) {
    this.queue.push(operation);
    this.persist();
  }

  async sync() {
    while (this.queue.length > 0) {
      const op = this.queue.shift();
      await this.persist();
      try {
        await this.server.sync(op);
      } catch (error) {
        this.queue.unshift(op);
        throw error;
      }
    }
  }
}
```

## Security

### Secure Storage
```swift
// iOS Keychain
let query: [String: Any] = [
  kSecClass as String: kSecClassGenericPassword,
  kSecAttrAccount as String: "user_token",
  kSecValueData as String: token.data(using: .utf8)!,
  kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
]

SecItemAdd(query as CFDictionary, nil);
```

```kotlin
// Android EncryptedSharedPreferences
val masterKey = MasterKey.Builder(context)
  .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
  .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
  context,
  "secret_shared_prefs",
  masterKey,
  EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
  EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```
