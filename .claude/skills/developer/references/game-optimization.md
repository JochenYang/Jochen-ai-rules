# Game Performance Optimization Guide

## Profiling Tools

### Unity Profiler
- CPU Usage: Identify expensive scripts
- GPU Usage: Rendering bottlenecks
- Memory: Allocation and leaks
- Physics: Collision and rigidbody overhead

### Unreal Insights
- Frame time analysis
- CPU/GPU profiling
- Memory tracking
- Network profiling

## CPU Optimization

### Script Optimization
```csharp
// BAD: Expensive operations in Update
void Update() {
    GameObject enemy = GameObject.FindWithTag("Enemy");
    float distance = Vector3.Distance(transform.position, enemy.transform.position);
}

// GOOD: Cache and optimize
private Transform enemyTransform;
private float distanceSquared; // Avoid sqrt

void Start() {
    enemyTransform = GameObject.FindWithTag("Enemy").transform;
}

void Update() {
    // Use sqrMagnitude instead of Distance
    distanceSquared = (transform.position - enemyTransform.position).sqrMagnitude;
}
```

### Object Pooling
```csharp
public class BulletPool : MonoBehaviour {
    [SerializeField] private GameObject bulletPrefab;
    [SerializeField] private int poolSize = 50;
    private Queue<GameObject> pool;
    
    void Start() {
        pool = new Queue<GameObject>();
        for (int i = 0; i < poolSize; i++) {
            GameObject bullet = Instantiate(bulletPrefab);
            bullet.SetActive(false);
            pool.Enqueue(bullet);
        }
    }
    
    public GameObject GetBullet() {
        if (pool.Count > 0) {
            GameObject bullet = pool.Dequeue();
            bullet.SetActive(true);
            return bullet;
        }
        return Instantiate(bulletPrefab);
    }
    
    public void ReturnBullet(GameObject bullet) {
        bullet.SetActive(false);
        pool.Enqueue(bullet);
    }
}
```

### Reduce Garbage Collection
```csharp
// BAD: Creates garbage every frame
void Update() {
    string message = "Score: " + score.ToString();
    Debug.Log(message);
}

// GOOD: Reuse StringBuilder
private StringBuilder sb = new StringBuilder();
void Update() {
    sb.Clear();
    sb.Append("Score: ");
    sb.Append(score);
    Debug.Log(sb.ToString());
}
```

## GPU Optimization

### Draw Call Reduction
- **Static Batching**: Mark static objects
- **Dynamic Batching**: Small meshes with same material
- **GPU Instancing**: Many identical objects
- **Texture Atlasing**: Combine textures

### LOD (Level of Detail)
```csharp
// Unity LOD Group setup
LODGroup lodGroup = gameObject.AddComponent<LODGroup>();
LOD[] lods = new LOD[3];

lods[0] = new LOD(0.6f, highDetailRenderers);  // 60% screen height
lods[1] = new LOD(0.3f, mediumDetailRenderers); // 30% screen height
lods[2] = new LOD(0.1f, lowDetailRenderers);    // 10% screen height

lodGroup.SetLODs(lods);
```

### Occlusion Culling
- Bake occlusion data for static geometry
- Use camera frustum culling
- Implement custom culling for large worlds

### Shader Optimization
```hlsl
// Avoid expensive operations in fragment shader
// BAD: Complex calculations per pixel
float4 frag(v2f i) : SV_Target {
    float3 normal = normalize(i.normal);
    float3 lightDir = normalize(_WorldSpaceLightPos0.xyz);
    float ndotl = max(0, dot(normal, lightDir));
    return _Color * ndotl * pow(ndotl, _Shininess);
}

// GOOD: Move to vertex shader when possible
v2f vert(appdata v) {
    v2f o;
    o.pos = UnityObjectToClipPos(v.vertex);
    float3 normal = UnityObjectToWorldNormal(v.normal);
    o.lighting = max(0, dot(normal, _WorldSpaceLightPos0.xyz));
    return o;
}
```

## Memory Optimization

### Texture Compression
- Mobile: ASTC, ETC2
- PC: DXT/BC
- Use mipmaps for distant objects
- Reduce texture resolution where possible

### Audio Compression
- Background music: Vorbis/MP3 (streaming)
- Sound effects: ADPCM (compressed in memory)
- Short sounds: PCM (uncompressed)

### Asset Bundle Management
```csharp
public class AssetBundleManager : MonoBehaviour {
    private Dictionary<string, AssetBundle> loadedBundles = new Dictionary<string, AssetBundle>();
    
    public async Task<T> LoadAssetAsync<T>(string bundleName, string assetName) where T : Object {
        if (!loadedBundles.ContainsKey(bundleName)) {
            AssetBundleCreateRequest request = AssetBundle.LoadFromFileAsync(bundleName);
            await request;
            loadedBundles[bundleName] = request.assetBundle;
        }
        
        AssetBundleRequest assetRequest = loadedBundles[bundleName].LoadAssetAsync<T>(assetName);
        await assetRequest;
        return assetRequest.asset as T;
    }
    
    public void UnloadBundle(string bundleName, bool unloadAllLoadedObjects = false) {
        if (loadedBundles.ContainsKey(bundleName)) {
            loadedBundles[bundleName].Unload(unloadAllLoadedObjects);
            loadedBundles.Remove(bundleName);
        }
    }
}
```

## Physics Optimization

### Collision Matrix
- Configure layer collision matrix
- Disable unnecessary collisions
- Use triggers instead of collisions when possible

### Rigidbody Settings
```csharp
// Optimize rigidbody for performance
rigidbody.interpolation = RigidbodyInterpolation.None; // If not needed
rigidbody.collisionDetectionMode = CollisionDetectionMode.Discrete; // Default
rigidbody.sleepThreshold = 0.5f; // Put to sleep faster
```

### Simplified Colliders
- Use primitive colliders (Box, Sphere, Capsule)
- Avoid Mesh Colliders when possible
- Use convex Mesh Colliders for moving objects

## Mobile-Specific Optimization

### Battery Life
- Target 30 FPS instead of 60 FPS
- Reduce screen resolution
- Minimize particle effects
- Use simpler shaders

### Thermal Management
```csharp
public class PerformanceManager : MonoBehaviour {
    void Start() {
        // Reduce target frame rate on mobile
        #if UNITY_ANDROID || UNITY_IOS
        Application.targetFrameRate = 30;
        QualitySettings.vSyncCount = 0;
        #endif
    }
    
    void Update() {
        // Monitor temperature and adjust quality
        if (SystemInfo.batteryLevel < 0.2f) {
            QualitySettings.SetQualityLevel(0); // Lowest quality
        }
    }
}
```

## Profiling Checklist

- [ ] CPU usage < 16ms (60 FPS) or < 33ms (30 FPS)
- [ ] GPU usage < frame budget
- [ ] Draw calls < 1000 (mobile) or < 5000 (PC)
- [ ] Memory usage within platform limits
- [ ] No memory leaks (stable over time)
- [ ] Physics overhead < 5ms
- [ ] GC allocations < 1KB per frame
- [ ] Load times < 5 seconds

## Common Bottlenecks

1. **Too many draw calls**: Use batching and instancing
2. **Expensive shaders**: Simplify or move to vertex shader
3. **Too many physics objects**: Use simplified colliders
4. **Memory allocations**: Use object pooling
5. **Unoptimized scripts**: Cache references, avoid Find()
6. **Large textures**: Compress and use mipmaps
7. **Too many lights**: Use baked lighting
8. **Overdraw**: Optimize UI and particle effects
