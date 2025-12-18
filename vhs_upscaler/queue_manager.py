"""
Video Queue Manager for VHS Upscaler
====================================
Manages a queue of videos for batch processing with status tracking.
"""

import json
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Callable, Dict
import traceback


class JobStatus(Enum):
    """Status of a queue job."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PREPROCESSING = "preprocessing"
    UPSCALING = "upscaling"
    ENCODING = "encoding"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueueJob:
    """Represents a single video processing job."""
    id: str
    input_source: str
    output_path: str
    preset: str = "vhs"
    resolution: int = 1080
    quality: int = 0
    crf: int = 20
    encoder: str = "hevc_nvenc"

    # New options for engine and HDR
    upscale_engine: str = "auto"  # auto, maxine, realesrgan, ffmpeg
    hdr_mode: str = "sdr"  # sdr, hdr10, hlg
    realesrgan_model: str = "realesrgan-x4plus"
    realesrgan_denoise: float = 0.5  # 0-1 denoise strength
    ffmpeg_scale_algo: str = "lanczos"  # lanczos, bicubic, bilinear, spline, neighbor

    # HDR advanced options
    hdr_brightness: int = 400  # Peak brightness in nits
    hdr_color_depth: int = 10  # 8 or 10 bit

    # Audio options
    audio_enhance: str = "none"  # none, light, moderate, aggressive, voice, music
    audio_upmix: str = "none"  # none, simple, surround, prologic, demucs
    audio_layout: str = "original"  # original, stereo, 5.1, 7.1, mono
    audio_format: str = "aac"  # aac, ac3, eac3, dts, flac

    # Audio enhancement advanced options
    audio_target_loudness: float = -14.0  # LUFS target (-24 to -9)
    audio_noise_floor: float = -20.0  # dB noise floor (-30 to -10)

    # Demucs advanced options
    demucs_model: str = "htdemucs"  # htdemucs, htdemucs_ft, mdx_extra, mdx_extra_q
    demucs_device: str = "auto"  # auto, cuda, cpu
    demucs_shifts: int = 1  # 0-5, more = better quality, slower

    # Surround advanced options
    lfe_crossover: int = 120  # Hz (60-200)
    center_mix: float = 0.707  # 0-1, 0.707 = -3dB
    surround_delay: int = 15  # ms (0-50)

    # LUT color grading options
    lut_file: Optional[str] = None  # Path to .cube LUT file
    lut_strength: float = 1.0  # 0.0-1.0 blend intensity

    # Face restoration options
    face_restore: bool = False  # Enable AI face restoration
    face_restore_strength: float = 0.5  # 0.0-1.0 restoration strength
    face_restore_upscale: int = 2  # Upscale factor (1, 2, or 4)

    # Deinterlacing options
    deinterlace_algorithm: str = "yadif"  # yadif, bwdif, w3fdif, qtgmc
    qtgmc_preset: Optional[str] = None  # draft, medium, slow, very_slow

    # Runtime state
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    stage_progress: float = 0.0
    current_stage: str = ""
    error_message: str = ""
    video_title: str = ""

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Results
    output_size: int = 0
    processing_time: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'QueueJob':
        """Create from dictionary."""
        data['status'] = JobStatus(data.get('status', 'pending'))
        return cls(**data)


class VideoQueue:
    """
    Thread-safe video processing queue with callbacks.

    Features:
    - Add/remove/reorder jobs
    - Status tracking per job
    - Callbacks for UI updates
    - Persistence to disk
    - Pause/resume support
    """

    def __init__(self,
                 processor_func: Callable = None,
                 max_concurrent: int = 1,
                 auto_start: bool = False,
                 persistence_file: Optional[Path] = None):
        """
        Initialize the video queue.

        Args:
            processor_func: Function to process each job (receives QueueJob, returns bool)
            max_concurrent: Maximum concurrent processing jobs
            auto_start: Start processing immediately when jobs added
            persistence_file: File to save/load queue state
        """
        self.processor_func = processor_func
        self.max_concurrent = max_concurrent
        self.auto_start = auto_start
        self.persistence_file = persistence_file

        # Job storage
        self.jobs: Dict[str, QueueJob] = {}
        self.job_order: List[str] = []

        # Threading
        self._lock = threading.RLock()
        self._processing = False
        self._paused = False
        self._stop_flag = False
        self._worker_thread: Optional[threading.Thread] = None

        # Callbacks
        self._on_job_update: List[Callable[[QueueJob], None]] = []
        self._on_queue_update: List[Callable[[], None]] = []
        self._on_job_complete: List[Callable[[QueueJob], None]] = []
        self._on_job_error: List[Callable[[QueueJob, str], None]] = []

        # Load persisted state
        if persistence_file and persistence_file.exists():
            self.load_state()

    # =========================================================================
    # Job Management
    # =========================================================================

    def add_job(self,
                input_source: str,
                output_path: str,
                preset: str = "vhs",
                resolution: int = 1080,
                quality: int = 0,
                crf: int = 20,
                encoder: str = "hevc_nvenc",
                upscale_engine: str = "auto",
                hdr_mode: str = "sdr",
                realesrgan_model: str = "realesrgan-x4plus",
                realesrgan_denoise: float = 0.5,
                ffmpeg_scale_algo: str = "lanczos",
                hdr_brightness: int = 400,
                hdr_color_depth: int = 10,
                audio_enhance: str = "none",
                audio_upmix: str = "none",
                audio_layout: str = "original",
                audio_format: str = "aac",
                audio_target_loudness: float = -14.0,
                audio_noise_floor: float = -20.0,
                demucs_model: str = "htdemucs",
                demucs_device: str = "auto",
                demucs_shifts: int = 1,
                lfe_crossover: int = 120,
                center_mix: float = 0.707,
                surround_delay: int = 15,
                lut_file: Optional[str] = None,
                lut_strength: float = 1.0,
                face_restore: bool = False,
                face_restore_strength: float = 0.5,
                face_restore_upscale: int = 2,
                deinterlace_algorithm: str = "yadif",
                qtgmc_preset: Optional[str] = None) -> QueueJob:
        """Add a new job to the queue."""
        job = QueueJob(
            id=str(uuid.uuid4())[:8],
            input_source=input_source,
            output_path=output_path,
            preset=preset,
            resolution=resolution,
            quality=quality,
            crf=crf,
            encoder=encoder,
            upscale_engine=upscale_engine,
            hdr_mode=hdr_mode,
            realesrgan_model=realesrgan_model,
            realesrgan_denoise=realesrgan_denoise,
            ffmpeg_scale_algo=ffmpeg_scale_algo,
            hdr_brightness=hdr_brightness,
            hdr_color_depth=hdr_color_depth,
            audio_enhance=audio_enhance,
            audio_upmix=audio_upmix,
            audio_layout=audio_layout,
            audio_format=audio_format,
            audio_target_loudness=audio_target_loudness,
            audio_noise_floor=audio_noise_floor,
            demucs_model=demucs_model,
            demucs_device=demucs_device,
            demucs_shifts=demucs_shifts,
            lfe_crossover=lfe_crossover,
            center_mix=center_mix,
            surround_delay=surround_delay,
            lut_file=lut_file,
            lut_strength=lut_strength,
            face_restore=face_restore,
            face_restore_strength=face_restore_strength,
            face_restore_upscale=face_restore_upscale,
            deinterlace_algorithm=deinterlace_algorithm,
            qtgmc_preset=qtgmc_preset
        )

        with self._lock:
            self.jobs[job.id] = job
            self.job_order.append(job.id)
            self._notify_queue_update()
            self.save_state()

        if self.auto_start and not self._processing:
            self.start_processing()

        return job

    def add_jobs_batch(self, jobs_data: List[dict]) -> List[QueueJob]:
        """Add multiple jobs at once."""
        added_jobs = []
        for data in jobs_data:
            job = self.add_job(**data)
            added_jobs.append(job)
        return added_jobs

    def remove_job(self, job_id: str) -> bool:
        """Remove a job from the queue."""
        with self._lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                if job.status in (JobStatus.PENDING, JobStatus.COMPLETED,
                                  JobStatus.FAILED, JobStatus.CANCELLED):
                    del self.jobs[job_id]
                    self.job_order.remove(job_id)
                    self._notify_queue_update()
                    self.save_state()
                    return True
        return False

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job (mark as cancelled if pending/processing)."""
        with self._lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                if job.status in (JobStatus.PENDING,):
                    job.status = JobStatus.CANCELLED
                    self._notify_job_update(job)
                    self.save_state()
                    return True
        return False

    def move_job(self, job_id: str, new_position: int) -> bool:
        """Move a job to a new position in the queue."""
        with self._lock:
            if job_id in self.job_order:
                self.job_order.remove(job_id)
                self.job_order.insert(new_position, job_id)
                self._notify_queue_update()
                self.save_state()
                return True
        return False

    def clear_completed(self):
        """Remove all completed/failed/cancelled jobs."""
        with self._lock:
            to_remove = [
                jid for jid, job in self.jobs.items()
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)
            ]
            for jid in to_remove:
                del self.jobs[jid]
                self.job_order.remove(jid)
            self._notify_queue_update()
            self.save_state()

    def clear_all(self):
        """Remove all jobs from the queue."""
        with self._lock:
            self.jobs.clear()
            self.job_order.clear()
            self._notify_queue_update()
            self.save_state()

    def get_job(self, job_id: str) -> Optional[QueueJob]:
        """Get a job by ID."""
        return self.jobs.get(job_id)

    def get_status(self, job_id: str) -> dict:
        """Get job status as dictionary."""
        job = self.jobs.get(job_id)
        if job:
            return {
                'id': job.id,
                'status': job.status.value,
                'progress': job.progress,
                'stage': job.current_stage,
                'error': job.error_message,
            }
        return {'error': 'Job not found'}

    def get_all_jobs(self) -> List[QueueJob]:
        """Get all jobs in order."""
        with self._lock:
            return [self.jobs[jid] for jid in self.job_order if jid in self.jobs]

    def get_pending_jobs(self) -> List[QueueJob]:
        """Get all pending jobs."""
        return [j for j in self.get_all_jobs() if j.status == JobStatus.PENDING]

    def get_queue_stats(self) -> dict:
        """Get queue statistics."""
        with self._lock:
            jobs = list(self.jobs.values())
            return {
                'total': len(jobs),
                'pending': sum(1 for j in jobs if j.status == JobStatus.PENDING),
                'processing': sum(1 for j in jobs if j.status in (
                    JobStatus.DOWNLOADING, JobStatus.PREPROCESSING,
                    JobStatus.UPSCALING, JobStatus.ENCODING
                )),
                'completed': sum(1 for j in jobs if j.status == JobStatus.COMPLETED),
                'failed': sum(1 for j in jobs if j.status == JobStatus.FAILED),
                'cancelled': sum(1 for j in jobs if j.status == JobStatus.CANCELLED),
            }

    # =========================================================================
    # Processing Control
    # =========================================================================

    def start_processing(self):
        """Start processing the queue."""
        if self._processing:
            return

        self._processing = True
        self._stop_flag = False
        self._paused = False
        self._worker_thread = threading.Thread(target=self._process_loop, daemon=True)
        self._worker_thread.start()

    def stop_processing(self):
        """Stop processing (finish current job then stop)."""
        self._stop_flag = True
        self._processing = False

    def pause_processing(self):
        """Pause processing after current job."""
        self._paused = True

    def resume_processing(self):
        """Resume processing."""
        self._paused = False
        if not self._processing:
            self.start_processing()

    def is_processing(self) -> bool:
        """Check if queue is currently processing."""
        return self._processing and not self._paused

    def _process_loop(self):
        """Main processing loop (runs in thread)."""
        while not self._stop_flag:
            if self._paused:
                time.sleep(0.5)
                continue

            # Get next pending job
            job = self._get_next_pending_job()
            if not job:
                time.sleep(0.5)
                continue

            # Process the job
            self._process_job(job)

        self._processing = False

    def _get_next_pending_job(self) -> Optional[QueueJob]:
        """Get the next pending job from the queue."""
        with self._lock:
            for job_id in self.job_order:
                job = self.jobs.get(job_id)
                if job and job.status == JobStatus.PENDING:
                    return job
        return None

    def _process_job(self, job: QueueJob):
        """Process a single job."""
        job.started_at = datetime.now().isoformat()
        start_time = time.time()

        try:
            if self.processor_func:
                # Call the processor function
                success = self.processor_func(job, self._update_job_progress)

                if success:
                    job.status = JobStatus.COMPLETED
                    job.progress = 100.0
                else:
                    job.status = JobStatus.FAILED
                    if not job.error_message:
                        job.error_message = "Processing failed"
            else:
                job.status = JobStatus.FAILED
                job.error_message = "No processor function configured"

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            traceback.print_exc()

        finally:
            job.completed_at = datetime.now().isoformat()
            job.processing_time = time.time() - start_time

            # Check output file size
            output_path = Path(job.output_path)
            if output_path.exists():
                job.output_size = output_path.stat().st_size

            self._notify_job_update(job)

            if job.status == JobStatus.COMPLETED:
                for callback in self._on_job_complete:
                    callback(job)
            elif job.status == JobStatus.FAILED:
                for callback in self._on_job_error:
                    callback(job, job.error_message)

            self.save_state()

    def _update_job_progress(self, job: QueueJob, status: JobStatus,
                             progress: float, stage_progress: float = 0,
                             current_stage: str = "", video_title: str = ""):
        """Update job progress (called from processor)."""
        job.status = status
        job.progress = progress
        job.stage_progress = stage_progress
        job.current_stage = current_stage
        if video_title:
            job.video_title = video_title
        self._notify_job_update(job)

    # =========================================================================
    # Callbacks
    # =========================================================================

    def on_job_update(self, callback: Callable[[QueueJob], None]):
        """Register callback for job updates."""
        self._on_job_update.append(callback)

    def on_queue_update(self, callback: Callable[[], None]):
        """Register callback for queue changes."""
        self._on_queue_update.append(callback)

    def on_job_complete(self, callback: Callable[[QueueJob], None]):
        """Register callback for job completion."""
        self._on_job_complete.append(callback)

    def on_job_error(self, callback: Callable[[QueueJob, str], None]):
        """Register callback for job errors."""
        self._on_job_error.append(callback)

    def _notify_job_update(self, job: QueueJob):
        """Notify all job update callbacks."""
        for callback in self._on_job_update:
            try:
                callback(job)
            except Exception as e:
                print(f"Callback error: {e}")

    def _notify_queue_update(self):
        """Notify all queue update callbacks."""
        for callback in self._on_queue_update:
            try:
                callback()
            except Exception as e:
                print(f"Callback error: {e}")

    # =========================================================================
    # Persistence
    # =========================================================================

    def save_state(self):
        """Save queue state to disk."""
        if not self.persistence_file:
            return

        with self._lock:
            data = {
                'job_order': self.job_order,
                'jobs': {jid: job.to_dict() for jid, job in self.jobs.items()}
            }

        self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.persistence_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_state(self):
        """Load queue state from disk."""
        if not self.persistence_file or not self.persistence_file.exists():
            return

        try:
            with open(self.persistence_file) as f:
                data = json.load(f)

            with self._lock:
                self.job_order = data.get('job_order', [])
                self.jobs = {
                    jid: QueueJob.from_dict(jdata)
                    for jid, jdata in data.get('jobs', {}).items()
                }

                # Reset any processing jobs to pending
                for job in self.jobs.values():
                    if job.status in (JobStatus.DOWNLOADING, JobStatus.PREPROCESSING,
                                      JobStatus.UPSCALING, JobStatus.ENCODING):
                        job.status = JobStatus.PENDING
                        job.progress = 0
                        job.stage_progress = 0

        except Exception as e:
            print(f"Failed to load queue state: {e}")
