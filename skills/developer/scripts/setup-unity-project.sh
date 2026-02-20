#!/bin/bash

# Unity project structure initialization
# Usage: ./setup-unity-project.sh --name <project-name> --template <template>

set -e

PROJECT_NAME=""
TEMPLATE="3d"
OUTPUT_DIR="."

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --template)
            TEMPLATE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$PROJECT_NAME" ]; then
    echo "Error: Project name is required"
    echo "Usage: ./setup-unity-project.sh --name <project-name> [--template <2d|3d|urp|hrdp>]"
    exit 1
fi

create_directory_structure() {
    local root="$1"
    local dirs=(
        "Assets/Scripts"
        "Assets/Scenes"
        "Assets/Prefabs"
        "Assets/Materials"
        "Assets/Textures"
        "Assets/Meshes"
        "Assets/Audio"
        "Assets/Animations"
        "Assets/UI"
        "Assets/Plugins"
        "Assets/Editor"
        "Assets/Resources"
        "Assets/StreamingAssets"
        "Packages"
        "ProjectSettings"
        "Logs"
    )

    echo "Creating directory structure for: $root"
    mkdir -p "${dirs[@]/#/$root/}"
}

create_script_templates() {
    local scripts_dir="$1/Assets/Scripts"

    cat > "$scripts_dir/MonoBehaviourTemplate.cs" << 'EOF'
using UnityEngine;

public class NewBehaviourScript : MonoBehaviour
{
    [Header("Settings")]
    [SerializeField] private float moveSpeed = 5f;

    private void Start()
    {
        // Initialization logic
    }

    private void Update()
    {
        // Per-frame logic
    }

    private void FixedUpdate()
    {
        // Physics updates
    }

    private void OnCollisionEnter(Collision collision)
    {
        // Collision handling
    }
}
EOF

    cat > "$scripts_dir/ScriptableObjectTemplate.cs" << 'EOF'
using UnityEngine;

[CreateAssetMenu(fileName = "NewData", menuName = "Custom/New Data")]
public class DataScriptableObject : ScriptableObject
{
    [Header("Data")]
    [SerializeField] private string dataName;
    [TextArea(3, 10)]
    [SerializeField] private string description;

    public string DataName => dataName;
    public string Description => description;
}
EOF

    cat > "$scripts_dir/SingletonTemplate.cs" << 'EOF'
using UnityEngine;

public class Singleton<T> : MonoBehaviour where T : MonoBehaviour
{
    private static T instance;
    public static T Instance
    {
        get
        {
            if (instance == null)
            {
                instance = FindObjectOfType<T>();
                if (instance == null)
                {
                    var singletonObject = new GameObject(typeof(T).Name);
                    instance = singletonObject.AddComponent<T>();
                }
            }
            return instance;
        }
    }

    protected virtual void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }

        instance = this as T;
        DontDestroyOnLoad(gameObject);
    }
}
EOF

    cat > "$scripts_dir/Editor/EditorScriptTemplate.cs" << 'EOF'
#if UNITY_EDITOR
using UnityEditor;

[CustomEditor(typeof(MonoBehaviour))]
public class CustomEditor : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
    }
}
#endif
EOF
}

create_unity_settings() {
    local root="$1"

    cat > "$root/ProjectSettings/ProjectSettings.asset" << 'EOF'
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!129 &1
PlayerSettings:
  m_ObjectHideFlags: 0
  productGUID: $(uuidgen)
  AndroidProfiler: 0
  AndroidFilterTouchesWhenObscured: 0
  AndroidEnableSustainedPerformanceMode: 0
  defaultScreenOrientation: 4
  targetDevice: 2
  useOnDemandResources: 0
  accelerometerFrequency: 60
  companyName: DefaultCompany
  productName: $PROJECT_NAME
  defaultCursor: {fileID: 0}
  cursorHotspot: {x: 0, y: 0}
  m_SplashScreenBackgroundColor: {r: 0.13725491, g: 0.12156863, b: 0.1254902, a: 1}
  m_ShowUnitySplashScreen: 1
  m_ShowUnitySplashLogo: 1
  m_SplashScreenOverlayOpacity: 1
  m_SplashScreenAnimation: 1
  m_SplashScreenLogoStyle: 1
  m_SplashScreenDrawMode: 0
  m_SplashScreenBackgroundAnimationZoom: 1
  m_SplashScreenLogoAnimationZoom: 1
  m_SplashScreenBackgroundLandscapeAspect: 1
  m_SplashScreenBackgroundPortraitAspect: 1
  m_SplashScreenBackgroundLandscapeUvs:
    serializedVersion: 2
    x: 0
    y: 0
    width: 1
    height: 1
  m_SplashScreenBackgroundPortraitUvs:
    serializedVersion: 2
    x: 0
    y: 0
    width: 1
    height: 1
  m_SplashScreenLogos: []
  m_VirtualRealitySplashScreen: {fileID: 0}
  m_HolographicTrackingLossScreen: {fileID: 0}
  defaultScreenWidth: 1920
  defaultScreenHeight: 1080
  defaultScreenWidthWeb: 1280
  defaultScreenHeightWeb: 720
  m_StereoRenderingPath: 0
  m_ActiveColorSpace: 0
  m_MTRendering: 1
  mipStripping: 0
  numberOfMipsStripped: 0
  m_StackTraceTypes: 010000000100000001000000010000000100000001000000
  iosShowActivityIndicatorOnLoading: -1
  androidShowActivityIndicatorOnLoading: -1
  displayResolutionDialog: 0
  iosUseCustomAppBackgroundBehavior: 0
  allowedAutorotateToPortrait: 1
  allowedAutorotateToPortraitUpsideDown: 1
  allowedAutorotateToLandscapeRight: 1
  allowedAutorotateToLandscapeLeft: 1
  useOSAutorotation: 1
  use32BitDisplayBuffer: 1
  preserveFramebufferAlpha: 0
  disableDepthAndStencilBuffers: 0
  androidStartInFullscreen: 1
  androidRenderOutsideSafeArea: 1
  androidUseSwappy: 1
  androidBlitType: 0
  androidResizableWindow: 0
  androidDefaultWindowWidth: 1920
  androidDefaultWindowHeight: 1080
  androidMinimumWindowWidth: 400
  androidMinimumWindowHeight: 300
  androidFullscreenMode: 1
  defaultIsNativeResolution: 1
  macRetinaSupport: 1
  runInBackground: 1
  captureSingleScreen: 0
  muteOtherAudioSources: 0
  Prepare IOS For Recording: 0
  Force IOS Speakers When Recording: 0
  deferSystemGesturesMode: 0
  hideHomeButton: 0
  submitAnalytics: 1
  usePlayerLog: 1
  bakeCollisionMeshes: 0
  forceSingleInstance: 0
  useFlipModelSwapchain: 1
  resizableWindow: 0
  useMacAppStoreValidation: 0
  macAppStoreCategory: public.app-category.games
  gpuSkinning: 1
  xboxPIXTextureCapture: 0
  xboxEnableAvatar: 0
  xboxEnableKinect: 0
  xboxEnableKinectAutoTracking: 0
  xboxEnableFitness: 0
  visibleInBackground: 1
  allowFullscreenSwitch: 1
  fullscreenMode: 1
  xboxSpeechDB: 0
  xboxEnableHeadOrientation: 0
  xboxEnableGuest: 0
  xboxEnablePIXSampling: 0
  metalFramebufferOnly: 0
  xboxOneResolution: 0
  xboxOneSResolution: 0
  xboxOneXResolution: 3
  xboxOneMonoLoggingLevel: 0
  xboxOneLoggingLevel: 1
  xboxOneDisableEsram: 0
  xboxOneEnableTypeOptimization: 0
  xboxOnePresentImmediateThreshold: 0
  switchQueueCommandMemory: 0
  switchQueueControlMemory: 16384
  switchQueueComputeMemory: 262144
  switchNVNShaderPoolsGranularity: 33554432
  switchNVNDefaultPoolsGranularity: 16777216
  switchNVNOtherPoolsGranularity: 16777216
  switchNVNMaxPublicTextureIDCount: 0
  switchNVNMaxPublicSamplerIDCount: 0
  stadiaPresentMode: 0
  stadiaTargetFramerate: 0
  vulkanNumSwapchainBuffers: 3
  vulkanEnableSetSRGBWrite: 0
  vulkanEnablePreTransform: 0
  vulkanEnableLateAcquireNextImage: 0
  vulkanEnableCommandBufferRecycling: 1
  m_SupportedAspectRatios:
    4:3: 1
    5:4: 1
    16:10: 1
    16:9: 1
    Others: 1
  bundleVersion: 1.0
  preloadedAssets: []
  metroInputSource: 0
  wsaTransparentSwapchain: 0
  m_HolographicPauseOnTrackingLoss: 1
  xboxOneDisableKinectGpuReservation: 1
  xboxOneEnable7thCore: 1
  vrSettings:
    enable360StereoCapture: 0
  isWsaHolographicRemotingEnabled: 0
  enableFrameTimingStats: 0
  enableOpenGLProfilerGPURecorders: 1
  useHDRDisplay: 0
  hdrBitDepth: 0
  m_ColorGamuts: 00000000
  targetPixelDensity: 30
  resolutionScalingMode: 0
  resetResolutionOnWindowResize: 0
  androidSupportedAspectRatio: 1
  androidMaxAspectRatio: 2.1
  applicationIdentifier:
    Standalone: com.Company.ProductName
    iPhone: com.Company.ProductName
    tvOS: com.Company.ProductName
  buildNumber:
    Standalone: 0
  overrideDefaultApplicationIdentifier: 0
  AndroidBundleVersionCode: 1
  AndroidMinSdkVersion: 22
  AndroidTargetSdkVersion: 0
  AndroidPreferredInstallLocation: 1
  aotOptions:
  stripEngineCode: 1
  iPhoneStrippingLevel: 0
  iPhoneScriptCallOptimization: 0
  ForceInternetPermission: 0
  ForceSDCardPermission: 0
  CreateWallpaper: 0
  APKExpansionFiles: 0
  keepLoadedShadersAlive: 0
  StripUnusedMeshComponents: 1
  VertexChannelCompressionMask: 4054
  iPhoneSdkVersion: 988
  iOSTargetOSVersionString: 12.0
  tvOSSdkVersion: 0
  tvOSRequireExtendedGameController: 0
  tvOSTargetOSVersionString: 12.0
  uIPrerenderedIcon: 0
  uIRequiresPersistentWiFi: 0
  uIRequiresFullScreen: 1
  uIStatusBarHidden: 1
  uIExitOnSuspend: 0
  uIStatusBarStyle: 0
  appleTVSplashScreen: {fileID: 0}
  appleTVSplashScreen2x: {fileID: 0}
  tvOSSmallIconLayers: []
  tvOSSmallIconLayers2x: []
  tvOSLargeIconLayers: []
  tvOSLargeIconLayers2x: []
  tvOSTopShelfImageLayers: []
  tvOSTopShelfImageLayers2x: []
  tvOSTopShelfImageWideLayers: []
  tvOSTopShelfImageWideLayers2x: []
  iOSLaunchScreenType: 0
  iOSLaunchScreenPortrait: {fileID: 0}
  iOSLaunchScreenLandscape: {fileID: 0}
  iOSLaunchScreenBackgroundColor:
    serializedVersion: 2
    rgba: 0
  iOSLaunchScreenFillPct: 25
  iOSLaunchScreenSize: 100
  iOSLaunchScreenCustomXibPath:
  iOSLaunchScreeniPadType: 0
  iOSLaunchScreeniPadImage: {fileID: 0}
  iOSLaunchScreeniPadBackgroundColor:
    serializedVersion: 2
    rgba: 0
  iOSLaunchScreeniPadFillPct: 25
  iOSLaunchScreeniPadSize: 100
  iOSLaunchScreeniPadCustomXibPath:
  iOSLaunchScreenCustomStoryboardPath:
  iOSLaunchScreeniPadCustomStoryboardPath:
  iOSDeviceRequirements: []
  iOSURLSchemes: []
  macOSURLSchemes: []
  iOSBackgroundModes: 0
  iOSMetalForceHardShadows: 0
  metalEditorSupport: 1
  metalAPIValidation: 1
  iOSRenderExtraFrameOnPause: 0
  iosCopyPluginsCodeInsteadOfSymlink: 0
  appleDeveloperTeamID:
  iOSManualSigningProvisioningProfileID:
  tvOSManualSigningProvisioningProfileID:
  iOSManualSigningProvisioningProfileType: 0
  tvOSManualSigningProvisioningProfileType: 0
  appleEnableAutomaticSigning: 0
  iOSRequireARKit: 0
  iOSAutomaticallyDetectAndAddCapabilities: 1
  appleEnableProMotion: 0
  shaderPrecisionModel: 0
  clonedFromGUID: c0afd0d1d80e3634a9dac47571a205b9
  templatePackageId: com.unity.template.3d@5.0.4
  templateDefaultScene: Assets/Scenes/SampleScene.unity
  useCustomMainManifest: 0
  useCustomLauncherManifest: 0
  useCustomMainGradleTemplate: 0
  useCustomLauncherGradleManifest: 0
  useCustomBaseGradleTemplate: 0
  useCustomGradlePropertiesTemplate: 0
  useCustomGradleSettingsTemplate: 0
  useCustomProguardFile: 0
  AndroidTargetArchitectures: 1
  AndroidTargetDevices: 0
  AndroidSplashScreenScale: 0
  androidSplashScreen: {fileID: 0}
  AndroidKeystoreName:
  AndroidKeyaliasName:
  AndroidBuildApkPerCpuArchitecture: 0
  AndroidTVCompatibility: 0
  AndroidIsGame: 1
  AndroidEnableTango: 0
  androidEnableBanner: 1
  androidUseLowAccuracyLocation: 0
  androidUseCustomKeystore: 0
  m_AndroidBanners:
  - width: 320
    height: 180
    banner: {fileID: 0}
  androidGamepadSupportLevel: 0
  chromeosInputEmulation: 1
  AndroidMinifyWithR8: 0
  AndroidMinifyRelease: 0
  AndroidMinifyDebug: 0
  AndroidValidateAppBundleSize: 1
  AndroidAppBundleSizeToValidate: 150
  m_BuildTargetIcons: []
  m_BuildTargetPlatformIcons: []
  m_BuildTargetBatching: []
  m_BuildTargetShaderSettings: []
  m_BuildTargetGraphicsJobs: []
  m_BuildTargetGraphicsJobMode: []
  m_BuildTargetGraphicsAPIs: []
  m_BuildTargetVRSettings: []
  webGLCompression: 1
  webGLExceptionSupport: 0
  webGLLinkerTarget: 1
  webGLMemorySize: 32
  webGLPowerPreference: 2
  webGLShowDiagnostics: 0
  webGLDataCaching: 1
  webGLDebugSymbols: 0
  webGLEmscriptenArgs:
  webGLModulesDirectory:
  webGLTemplate: APPLICATION:Default
  webGLAnalyzeBuildSize: 0
  webGLUseEmbeddedResources: 0
  webGLCompressionFormat: 1
  webGLWasmArithmeticExceptions: 0
  webGLWasmStreaming: 0
  webGLDebugMode: 0
  webGLMemoryGrowthMode: 2
  webGLMemoryLinearGrowthStep: 16
  webGLMemoryGeometricGrowthStep: 0.2
  webGLMemoryGeometricGrowthCap: 96
  webGLPowerPreferenceIndex: 2
  scriptingDefineSymbols: {}
  additionalCompilerArguments: {}
  platformArchitecture: {}
  scriptingBackend:
    Standalone: 1
  il2cppCompilerConfiguration: {}
  il2cppCodeGeneration: {}
  managedStrippingLevel:
    WebGL: 1
  incrementalIl2cppBuild: {}
  suppressCommonWarnings: 1
  allowUnsafeCode: 0
  useDeterministicCompilation: 1
  enableRoslynAnalyzers: 1
  selectedPlatform: 0
  additionalIl2CppArgs:
  scriptingRuntimeVersion: 1
  gcIncremental: 1
  assemblyVersionValidation: 1
  gcWBarrierValidation: 0
  apiCompatibilityLevelPerPlatform:
    Standalone: 6
  m_RenderingPath: 1
  m_MobileRenderingPath: 1
  metroPackageName: $PROJECT_NAME
  metroPackageVersion:
  metroCertificatePath:
  metroCertificatePassword:
  metroCertificateSubject:
  metroCertificateIssuer:
  metroCertificateNotAfter: 0000000000000000
  metroApplicationDescription: $PROJECT_NAME
  wsaImages: {}
  metroTileShortName:
  metroTileShowName: 0
  metroMediumTileShowName: 0
  metroLargeTileShowName: 0
  metroWideTileShowName: 0
  metroSupportStreamingInstall: 0
  metroLastRequiredScene: 0
  metroDefaultTileSize: 1
  metroTileForegroundText: 2
  metroTileBackgroundColor: {r: 0.13333334, g: 0.17254902, b: 0.21568628, a: 0}
  metroSplashScreenBackgroundColor: {r: 0.12941177, g: 0.17254902, b: 0.21568628, a: 1}
  metroSplashScreenUseBackgroundColor: 0
  platformCapabilities: {}
  metroTargetDeviceFamilies: {}
  metroFTAName:
  metroFTAFileTypes: []
  metroProtocolName:
  XboxOneProductId:
  XboxOneUpdateKey:
  XboxOneSandboxId:
  XboxOneContentId:
  XboxOneTitleId:
  XboxOneSCId:
  XboxOneGameOsOverridePath:
  XboxOnePackagingOverridePath:
  XboxOneAppManifestOverridePath:
  XboxOneVersion: 1.0.0.0
  XboxOnePackageEncryption: 0
  XboxOnePackageUpdateGranularity: 2
  XboxOneDescription:
  XboxOneLanguage:
  - enus
  XboxOneCapability: []
  XboxOneGameRating: {}
  XboxOneIsContentPackage: 0
  XboxOneEnhancedXboxCompatibilityMode: 0
  XboxOneEnableGPUVariability: 1
  XboxOneSockets: {}
  XboxOneSplashScreen: {fileID: 0}
  XboxOneAllowedProductIds: []
  XboxOnePersistentLocalStorageSize: 0
  XboxOneXTitleMemory: 8
  XboxOneOverrideIdentityName:
  XboxOneOverrideIdentityPublisher:
  vraboroveditorSettings: {}
  cloudaboroveditorSettings: {}
  framebufferDepthMemorylessMode: 0
  projectName:
  organizationId:
  cloudEnabled: 0
  legacyClampBlendShapeWeights: 0
  hmiLoadingImage: {fileID: 0}
  hmiLogEnabled: 1
  hmiLogLimit: 1
  hmiCpuConfiguration:
  hmiTarget头颅Devices: 1
  hmiGraphicsJobMode: -1
  hmiGraphicsAPIs:
  hmiShowHmiSDKWarnings: 0
  hmiHoloLensHolographicRemotingEnabled: 0
  hmiHolographicRemotingVersion: 1
  virtualTexturingSupportEnabled: 0
  insecureHttpOption: 0
EOF
}

create_gitignore() {
    local root="$1"

    cat > "$root/.gitignore" << 'EOF'
# Unity
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild/
[Bb]uilds/
[Ll]ogs/
[Uu]pdated/

# Autogenerated
/*.userprefs
/*.unityproj
/*.sln
/*.suo

# Cache
/.vs/
.vscode/
*.cache

# OS
.DS_Store
Thumbs.db

# Backup
*~
*.bak
*.backup

# IDE
.idea/
*.swp
*.swo
*~
EOF
}

create_readme() {
    local root="$1"

    cat > "$root/README.md" << EOF
# $PROJECT_NAME

Unity $TEMPLATE project.

## Setup

1. Open Unity Hub
2. Click "Add" and select this directory
3. Open with Unity $(grep -m1 'version' ProjectSettings/ProjectSettings.asset | cut -d' ' -f2 || echo "2021+")

## Structure

- `Assets/Scripts/` - C# scripts
- `Assets/Scenes/` - Unity scenes
- `Assets/Prefabs/` - Prefabs
- `Assets/Materials/` - Materials
- `Assets/UI/` - UI assets
- `Assets/Editor/` - Editor scripts

## Development

- Use C# scripts with MonoBehaviour
- Follow Unity coding conventions
- Use ScriptableObjects for data
- Create Editor scripts for tools

## Build

1. File → Build Settings
2. Select platform
3. Click Build
EOF
}

main() {
    local project_root="$OUTPUT_DIR/$PROJECT_NAME"

    echo "Creating Unity project: $PROJECT_NAME (template: $TEMPLATE)"
    echo "Location: $project_root"
    echo ""

    create_directory_structure "$project_root"
    create_script_templates "$project_root"
    create_unity_settings "$project_root"
    create_gitignore "$project_root"
    create_readme "$project_root"

    echo ""
    echo "========================================"
    echo "Unity project created successfully!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "1. Open Unity Hub"
    echo "2. Add this project: $project_root"
    echo "3. Open with Unity Editor"
    echo "4. Open scene: Assets/Scenes/SampleScene.unity"
}

main
