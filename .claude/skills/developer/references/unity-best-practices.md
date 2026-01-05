# Unity Best Practices

## Project Structure

```
Assets/
├── _Project/              # Project-specific assets
│   ├── Scripts/
│   │   ├── Core/         # Core game systems
│   │   ├── Gameplay/     # Gameplay mechanics
│   │   ├── UI/           # UI scripts
│   │   └── Utilities/    # Helper utilities
│   ├── Prefabs/
│   ├── Scenes/
│   ├── Materials/
│   ├── Textures/
│   └── Audio/
├── Plugins/              # Third-party plugins
└── Resources/            # Runtime-loaded assets
```

## Scripting Best Practices

### MonoBehaviour Lifecycle

```csharp
// Initialization order
void Awake()    // Initialize references
void OnEnable() // Subscribe to events
void Start()    // Initialize state

// Update loop
void FixedUpdate()  // Physics calculations (50 FPS)
void Update()       // Frame-based logic
void LateUpdate()   // Camera follow, final adjustments

// Cleanup
void OnDisable()  // Unsubscribe from events
void OnDestroy()  // Cleanup resources
```

### Performance Optimization

**Avoid in Update():**
- `GetComponent<T>()` - Cache in Awake/Start
- `Find()` / `FindObjectOfType()` - Use references
- String operations - Use StringBuilder
- Instantiate/Destroy - Use object pooling

**Good Practices:**
```csharp
// Cache components
private Rigidbody rb;
void Awake() => rb = GetComponent<Rigidbody>();

// Use object pooling
public class ObjectPool {
    private Queue<GameObject> pool = new Queue<GameObject>();
    
    public GameObject Get() {
        return pool.Count > 0 ? pool.Dequeue() : Instantiate(prefab);
    }
    
    public void Return(GameObject obj) {
        obj.SetActive(false);
        pool.Enqueue(obj);
    }
}

// Avoid allocations in Update
private Vector3 direction; // Reuse variable
void Update() {
    direction = target.position - transform.position;
    direction.Normalize();
}
```

## ScriptableObjects for Data

```csharp
[CreateAssetMenu(fileName = "WeaponData", menuName = "Game/Weapon")]
public class WeaponData : ScriptableObject {
    public string weaponName;
    public int damage;
    public float fireRate;
    public GameObject projectilePrefab;
}
```

## Event System

```csharp
// Event definition
public class GameEvents : MonoBehaviour {
    public static event Action<int> OnScoreChanged;
    public static event Action OnGameOver;
    
    public static void ScoreChanged(int newScore) => OnScoreChanged?.Invoke(newScore);
    public static void GameOver() => OnGameOver?.Invoke();
}

// Subscribe/Unsubscribe
void OnEnable() => GameEvents.OnScoreChanged += HandleScoreChanged;
void OnDisable() => GameEvents.OnScoreChanged -= HandleScoreChanged;
```

## Coroutines

```csharp
// Delay execution
IEnumerator DelayedAction(float delay) {
    yield return new WaitForSeconds(delay);
    // Execute action
}

// Wait for condition
IEnumerator WaitForCondition() {
    yield return new WaitUntil(() => isReady);
    // Continue
}

// Frame-by-frame animation
IEnumerator FadeOut(CanvasGroup group, float duration) {
    float elapsed = 0f;
    while (elapsed < duration) {
        elapsed += Time.deltaTime;
        group.alpha = 1f - (elapsed / duration);
        yield return null;
    }
}
```

## Physics Best Practices

- Use `FixedUpdate()` for physics calculations
- Use layers and layer masks for collision filtering
- Prefer `Rigidbody.MovePosition()` over `transform.position`
- Use `Physics.OverlapSphere()` instead of `OnTriggerStay()`

## Memory Management

- Unsubscribe from events in `OnDisable()`
- Clear references in `OnDestroy()`
- Use `Resources.UnloadUnusedAssets()` after scene loads
- Profile with Unity Profiler regularly

## Common Patterns

### Singleton
```csharp
public class GameManager : MonoBehaviour {
    public static GameManager Instance { get; private set; }
    
    void Awake() {
        if (Instance != null && Instance != this) {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }
}
```

### State Machine
```csharp
public enum PlayerState { Idle, Moving, Jumping, Attacking }

public class PlayerController : MonoBehaviour {
    private PlayerState currentState;
    
    void Update() {
        switch (currentState) {
            case PlayerState.Idle: HandleIdle(); break;
            case PlayerState.Moving: HandleMoving(); break;
            case PlayerState.Jumping: HandleJumping(); break;
        }
    }
    
    void ChangeState(PlayerState newState) {
        ExitState(currentState);
        currentState = newState;
        EnterState(newState);
    }
}
```
