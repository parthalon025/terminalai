"""
RTX Video SDK Low-Level Wrapper
===============================

Provides ctypes-based Python bindings for NVIDIA RTX Video SDK DLLs.

This module handles:
- DLL loading and initialization
- CUDA context management
- Effect creation and configuration
- Frame processing with memory management
"""

import ctypes
import logging
import platform
from ctypes import (
    POINTER, Structure, byref, c_char_p, c_float, c_int, c_uint, c_void_p, c_uint32
)
from pathlib import Path
from typing import Optional, Callable
import numpy as np

from .models import RTXVideoConfig, EffectType, GPUInfo, ProcessingStats
from .utils import detect_sdk, validate_gpu, get_sdk_info

logger = logging.getLogger(__name__)


# NvVFX Status codes
class NvVFXStatus:
    """RTX Video SDK status codes."""
    SUCCESS = 0
    ERR_GENERAL = -1
    ERR_UNIMPLEMENTED = -2
    ERR_MEMORY = -3
    ERR_EFFECT = -4
    ERR_SELECTOR = -5
    ERR_BUFFER = -6
    ERR_PARAMETER = -7
    ERR_MISMATCH = -8
    ERR_PIXELFORMAT = -9
    ERR_MODEL = -10
    ERR_LIBRARY = -11
    ERR_INITIALIZATION = -12
    ERR_FILE = -13
    ERR_CUDA = -14
    ERR_DRIVER_VERSION = -15


# NvCV Image pixel formats
class NvCVImagePixelFormat:
    """Pixel format constants."""
    UNKNOWN = 0
    Y = 1
    A = 2
    YA = 3
    RGB = 4
    BGR = 5
    RGBA = 6
    BGRA = 7
    ARGB = 8
    ABGR = 9
    YUV420 = 10
    YUV422 = 11
    YUV444 = 12


# NvCV Image component types
class NvCVImageComponentType:
    """Component type constants."""
    UNKNOWN = 0
    UINT8 = 1
    UINT16 = 2
    UINT32 = 3
    FLOAT16 = 4
    FLOAT32 = 5


# NvCV Image memory layout
class NvCVImageLayout:
    """Memory layout constants."""
    INTERLEAVED = 0  # RGBRGBRGB
    PLANAR = 1       # RRRGGGBBB
    UYVY = 2
    YUV = 3


class NvCVImage(Structure):
    """NvCVImage structure matching SDK header."""
    _fields_ = [
        ("pixels", c_void_p),
        ("width", c_int),
        ("height", c_int),
        ("pitch", c_int),
        ("pixelFormat", c_int),
        ("componentType", c_int),
        ("layout", c_int),
        ("colorspace", c_int),
        ("gpuMem", c_int),
        ("reserved", c_int * 8),
    ]


def _check_status(status: int, operation: str):
    """Check SDK status and raise exception on error."""
    if status != NvVFXStatus.SUCCESS:
        error_messages = {
            NvVFXStatus.ERR_GENERAL: "General error",
            NvVFXStatus.ERR_UNIMPLEMENTED: "Feature not implemented",
            NvVFXStatus.ERR_MEMORY: "Memory allocation failed",
            NvVFXStatus.ERR_EFFECT: "Invalid effect",
            NvVFXStatus.ERR_SELECTOR: "Invalid selector/parameter name",
            NvVFXStatus.ERR_BUFFER: "Invalid buffer",
            NvVFXStatus.ERR_PARAMETER: "Invalid parameter value",
            NvVFXStatus.ERR_MISMATCH: "Resolution or format mismatch",
            NvVFXStatus.ERR_PIXELFORMAT: "Unsupported pixel format",
            NvVFXStatus.ERR_MODEL: "Model loading failed",
            NvVFXStatus.ERR_LIBRARY: "Library loading failed",
            NvVFXStatus.ERR_INITIALIZATION: "Initialization failed",
            NvVFXStatus.ERR_FILE: "File not found",
            NvVFXStatus.ERR_CUDA: "CUDA error",
            NvVFXStatus.ERR_DRIVER_VERSION: "Driver version too old",
        }
        msg = error_messages.get(status, f"Unknown error ({status})")
        raise RuntimeError(f"RTX Video SDK {operation} failed: {msg}")


class RTXVideoWrapper:
    """
    Python wrapper for RTX Video SDK.

    Provides high-level interface to SDK effects while managing
    low-level resources and CUDA contexts.

    Example:
        config = RTXVideoConfig(enable_super_resolution=True)
        wrapper = RTXVideoWrapper(config)
        wrapper.initialize()

        output_frame = wrapper.process_frame(input_frame)

        wrapper.cleanup()
    """

    def __init__(self, config: RTXVideoConfig):
        """
        Initialize wrapper with configuration.

        Args:
            config: RTX Video SDK configuration
        """
        self.config = config
        self._sdk_path: Optional[Path] = None
        self._dll: Optional[ctypes.CDLL] = None
        self._effect_handle: c_void_p = c_void_p()
        self._cuda_stream: c_void_p = c_void_p()
        self._initialized = False
        self._gpu_info: Optional[GPUInfo] = None
        self._input_image: Optional[NvCVImage] = None
        self._output_image: Optional[NvCVImage] = None
        self._stats = ProcessingStats()

    @property
    def is_initialized(self) -> bool:
        """Check if SDK is initialized."""
        return self._initialized

    @property
    def gpu_info(self) -> Optional[GPUInfo]:
        """Get GPU information."""
        return self._gpu_info

    @property
    def stats(self) -> ProcessingStats:
        """Get processing statistics."""
        return self._stats

    def initialize(self) -> bool:
        """
        Initialize SDK and create effect.

        Returns:
            True if initialization successful.

        Raises:
            RuntimeError: If initialization fails critically.
        """
        if self._initialized:
            return True

        # Validate configuration
        errors = self.config.validate()
        if errors:
            logger.error(f"Configuration errors: {errors}")
            return False

        # Validate platform
        if platform.system() != "Windows":
            logger.error("RTX Video SDK only supports Windows")
            return False

        # Detect SDK
        if self.config.sdk_path:
            self._sdk_path = Path(self.config.sdk_path)
        else:
            self._sdk_path = detect_sdk()

        if not self._sdk_path:
            logger.error(
                "RTX Video SDK not found. Download from: "
                "https://developer.nvidia.com/rtx-video-sdk"
            )
            return False

        # Validate GPU
        self._gpu_info = validate_gpu()
        if not self._gpu_info.is_supported:
            logger.error(
                f"GPU not supported: {self._gpu_info.name}. "
                f"RTX Video SDK requires RTX 20 series or newer."
            )
            return False

        logger.info(f"Using GPU: {self._gpu_info}")

        # Load DLL
        try:
            if not self._load_dll():
                return False
        except Exception as e:
            logger.error(f"Failed to load SDK DLL: {e}")
            return False

        # Initialize CUDA and create effect
        try:
            self._init_cuda()
            self._create_effect()
            self._initialized = True
            logger.info("RTX Video SDK initialized successfully")
            return True

        except Exception as e:
            logger.error(f"SDK initialization failed: {e}")
            self.cleanup()
            return False

    def _load_dll(self) -> bool:
        """Load SDK DLL and setup function signatures."""
        sdk_info = get_sdk_info(self._sdk_path)
        if not sdk_info.is_valid:
            logger.error(sdk_info.error_message)
            return False

        logger.debug(f"Loading SDK DLL from: {sdk_info.dll_path}")

        try:
            self._dll = ctypes.CDLL(sdk_info.dll_path)
        except OSError as e:
            logger.error(f"Failed to load DLL: {e}")
            return False

        self._setup_function_signatures()
        return True

    def _setup_function_signatures(self):
        """Configure ctypes function signatures for SDK calls."""
        # NvVFX_CreateEffect
        self._dll.NvVFX_CreateEffect.argtypes = [c_char_p, POINTER(c_void_p)]
        self._dll.NvVFX_CreateEffect.restype = c_int

        # NvVFX_DestroyEffect
        self._dll.NvVFX_DestroyEffect.argtypes = [c_void_p]
        self._dll.NvVFX_DestroyEffect.restype = c_int

        # NvVFX_SetU32
        self._dll.NvVFX_SetU32.argtypes = [c_void_p, c_char_p, c_uint32]
        self._dll.NvVFX_SetU32.restype = c_int

        # NvVFX_SetF32
        self._dll.NvVFX_SetF32.argtypes = [c_void_p, c_char_p, c_float]
        self._dll.NvVFX_SetF32.restype = c_int

        # NvVFX_SetString
        self._dll.NvVFX_SetString.argtypes = [c_void_p, c_char_p, c_char_p]
        self._dll.NvVFX_SetString.restype = c_int

        # NvVFX_SetImage
        self._dll.NvVFX_SetImage.argtypes = [c_void_p, c_char_p, POINTER(NvCVImage)]
        self._dll.NvVFX_SetImage.restype = c_int

        # NvVFX_SetCudaStream
        self._dll.NvVFX_SetCudaStream.argtypes = [c_void_p, c_char_p, c_void_p]
        self._dll.NvVFX_SetCudaStream.restype = c_int

        # NvVFX_Load
        self._dll.NvVFX_Load.argtypes = [c_void_p]
        self._dll.NvVFX_Load.restype = c_int

        # NvVFX_Run
        self._dll.NvVFX_Run.argtypes = [c_void_p, c_int]
        self._dll.NvVFX_Run.restype = c_int

        # NvCVImage functions
        try:
            self._dll.NvCVImage_Alloc.argtypes = [
                POINTER(NvCVImage), c_uint, c_uint, c_int, c_int, c_int, c_int, c_uint
            ]
            self._dll.NvCVImage_Alloc.restype = c_int

            self._dll.NvCVImage_Dealloc.argtypes = [POINTER(NvCVImage)]
            self._dll.NvCVImage_Dealloc.restype = c_int

            self._dll.NvCVImage_Transfer.argtypes = [
                POINTER(NvCVImage), POINTER(NvCVImage), c_float, c_void_p, POINTER(NvCVImage)
            ]
            self._dll.NvCVImage_Transfer.restype = c_int
        except AttributeError:
            logger.debug("NvCVImage functions not available - using alternative approach")

    def _init_cuda(self):
        """Initialize CUDA context for processing."""
        # Try to use cupy for CUDA context if available
        try:
            import cupy as cp
            device = cp.cuda.Device(self.config.gpu_id)
            device.use()
            stream = cp.cuda.Stream()
            self._cuda_stream = c_void_p(stream.ptr)
            logger.debug(f"CUDA context initialized with CuPy on device {self.config.gpu_id}")
            return
        except ImportError:
            logger.debug("CuPy not available, using SDK default CUDA context")
        except Exception as e:
            logger.debug(f"CuPy initialization failed: {e}")

        # SDK will create its own CUDA context if none provided

    def _create_effect(self):
        """Create and configure the SDK effect."""
        effect_type = self.config.get_effect_type()
        effect_name = effect_type.value

        logger.debug(f"Creating effect: {effect_name}")

        status = self._dll.NvVFX_CreateEffect(
            effect_name.encode('utf-8'),
            byref(self._effect_handle)
        )
        _check_status(status, f"create effect '{effect_name}'")

        self._configure_effect()

    def _configure_effect(self):
        """Configure effect parameters based on config."""
        # Set model path
        model_path = self.config.model_path or str(self._sdk_path / "models")
        if Path(model_path).exists():
            status = self._dll.NvVFX_SetString(
                self._effect_handle,
                b"ModelDir",
                model_path.encode('utf-8')
            )
            if status != NvVFXStatus.SUCCESS:
                logger.warning(f"Failed to set model path: {status}")

        # Set CUDA stream if available
        if self._cuda_stream:
            status = self._dll.NvVFX_SetCudaStream(
                self._effect_handle,
                b"CudaStream",
                self._cuda_stream
            )
            if status != NvVFXStatus.SUCCESS:
                logger.debug(f"Failed to set CUDA stream: {status}")

        # Set effect-specific parameters
        effect_type = self.config.get_effect_type()

        if effect_type in [EffectType.SUPER_RESOLUTION, EffectType.UPSCALE_PIPELINE]:
            # Set resolution/mode for super resolution
            status = self._dll.NvVFX_SetU32(
                self._effect_handle,
                b"Resolution",
                self.config.target_resolution
            )
            if status != NvVFXStatus.SUCCESS:
                logger.debug(f"Failed to set Resolution: {status}")

            status = self._dll.NvVFX_SetU32(
                self._effect_handle,
                b"Mode",
                0  # 0 = quality, 1 = performance
            )
            if status != NvVFXStatus.SUCCESS:
                logger.debug(f"Failed to set Mode: {status}")

        if effect_type in [EffectType.ARTIFACT_REDUCTION, EffectType.UPSCALE_PIPELINE]:
            # Set artifact reduction strength
            status = self._dll.NvVFX_SetF32(
                self._effect_handle,
                b"Strength",
                self.config.artifact_strength
            )
            if status != NvVFXStatus.SUCCESS:
                logger.debug(f"Failed to set Strength: {status}")

        # Load the effect (initializes internal resources)
        status = self._dll.NvVFX_Load(self._effect_handle)
        _check_status(status, "load effect")

        logger.debug("Effect configured and loaded")

    def _allocate_images(self, input_shape: tuple, output_shape: tuple):
        """Allocate input/output GPU images."""
        in_h, in_w, in_c = input_shape
        out_h, out_w, out_c = output_shape

        # Allocate input image on GPU
        self._input_image = NvCVImage()
        status = self._dll.NvCVImage_Alloc(
            byref(self._input_image),
            in_w, in_h,
            NvCVImagePixelFormat.BGR,
            NvCVImageComponentType.UINT8,
            NvCVImageLayout.INTERLEAVED,
            32,  # alignment
            1    # GPU memory
        )
        _check_status(status, "allocate input image")

        # Allocate output image on GPU
        self._output_image = NvCVImage()
        status = self._dll.NvCVImage_Alloc(
            byref(self._output_image),
            out_w, out_h,
            NvCVImagePixelFormat.BGR,
            NvCVImageComponentType.UINT8,
            NvCVImageLayout.INTERLEAVED,
            32,  # alignment
            1    # GPU memory
        )
        _check_status(status, "allocate output image")

        # Set images on effect
        status = self._dll.NvVFX_SetImage(
            self._effect_handle, b"SrcImage", byref(self._input_image)
        )
        _check_status(status, "set source image")

        status = self._dll.NvVFX_SetImage(
            self._effect_handle, b"DstImage", byref(self._output_image)
        )
        _check_status(status, "set destination image")

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a single frame through the SDK.

        Args:
            frame: Input frame as numpy array (BGR, uint8)
                   Shape: (height, width, channels)

        Returns:
            Processed frame as numpy array (BGR, uint8)

        Raises:
            RuntimeError: If SDK not initialized or processing fails
        """
        if not self._initialized:
            raise RuntimeError("SDK not initialized. Call initialize() first.")

        if frame.dtype != np.uint8:
            raise ValueError(f"Unsupported frame dtype: {frame.dtype}. Expected uint8.")

        if len(frame.shape) != 3:
            raise ValueError(f"Expected 3D array (H, W, C), got shape: {frame.shape}")

        in_h, in_w, in_c = frame.shape
        out_h = self.config.target_resolution
        out_w = int(in_w * (out_h / in_h))
        out_c = in_c

        # Allocate images if needed
        if self._input_image is None:
            self._allocate_images(
                (in_h, in_w, in_c),
                (out_h, out_w, out_c)
            )

        # Transfer input frame to GPU
        cpu_input = NvCVImage()
        cpu_input.pixels = frame.ctypes.data_as(c_void_p)
        cpu_input.width = in_w
        cpu_input.height = in_h
        cpu_input.pitch = frame.strides[0]
        cpu_input.pixelFormat = NvCVImagePixelFormat.BGR
        cpu_input.componentType = NvCVImageComponentType.UINT8
        cpu_input.layout = NvCVImageLayout.INTERLEAVED

        status = self._dll.NvCVImage_Transfer(
            byref(cpu_input),
            byref(self._input_image),
            1.0,
            self._cuda_stream,
            None
        )
        _check_status(status, "transfer input to GPU")

        # Run effect
        status = self._dll.NvVFX_Run(self._effect_handle, 0)
        _check_status(status, "run effect")

        # Transfer output from GPU
        output_frame = np.empty((out_h, out_w, out_c), dtype=np.uint8)
        cpu_output = NvCVImage()
        cpu_output.pixels = output_frame.ctypes.data_as(c_void_p)
        cpu_output.width = out_w
        cpu_output.height = out_h
        cpu_output.pitch = output_frame.strides[0]
        cpu_output.pixelFormat = NvCVImagePixelFormat.BGR
        cpu_output.componentType = NvCVImageComponentType.UINT8
        cpu_output.layout = NvCVImageLayout.INTERLEAVED

        status = self._dll.NvCVImage_Transfer(
            byref(self._output_image),
            byref(cpu_output),
            1.0,
            self._cuda_stream,
            None
        )
        _check_status(status, "transfer output from GPU")

        self._stats.processed_frames += 1
        return output_frame

    def cleanup(self):
        """Release all SDK resources."""
        if self._output_image is not None:
            try:
                self._dll.NvCVImage_Dealloc(byref(self._output_image))
            except Exception:
                pass
            self._output_image = None

        if self._input_image is not None:
            try:
                self._dll.NvCVImage_Dealloc(byref(self._input_image))
            except Exception:
                pass
            self._input_image = None

        if self._effect_handle:
            try:
                self._dll.NvVFX_DestroyEffect(self._effect_handle)
            except Exception:
                pass
            self._effect_handle = c_void_p()

        self._initialized = False
        logger.debug("RTX Video SDK resources released")

    def __del__(self):
        """Destructor - ensure cleanup."""
        self.cleanup()

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False
