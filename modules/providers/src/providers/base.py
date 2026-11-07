import asyncio
import functools
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from contracts.models import Entity, TranslationResult, WSEventEnvelope


@dataclass
class TimingRecord:
    stage: str
    duration_ms: float
    success: bool
    error: Optional[str] = None


class STTProvider(ABC):
    """Abstract interface for streaming Speech-to-Text providers."""

    @abstractmethod
    async def transcribe_stream(
        self, audio_chunks: AsyncIterator[bytes], lang: str
    ) -> AsyncIterator[WSEventEnvelope]:
        """Transcribe streaming audio chunks into partial and final utterance events."""
        yield  # type: ignore


class Translator(ABC):
    """Abstract interface for machine translation providers."""

    @abstractmethod
    async def translate(
        self,
        text: str,
        src: str,
        tgt: str,
        glossary: Optional[Dict[str, str]] = None,
        entities: Optional[List[Entity]] = None,
    ) -> TranslationResult:
        """Translate source text into target language preserving entities and glossary terms."""
        pass


class TTSProvider(ABC):
    """Abstract interface for Text-to-Speech providers."""

    @abstractmethod
    async def synthesize_stream(
        self,
        text: str,
        lang: str,
        voice: Optional[str] = None,
        ssml: bool = False,
    ) -> AsyncIterator[bytes]:
        """Synthesize text into streaming audio chunks (PCM / WAV / MP3)."""
        yield  # type: ignore


def timing_decorator(stage_name: str, callback: Optional[Callable[[TimingRecord], None]] = None):
    """Measures execution latency of an async function and records duration in milliseconds."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            err_msg = None
            success = False
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                err_msg = str(e)
                raise
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                record = TimingRecord(
                    stage=stage_name,
                    duration_ms=elapsed_ms,
                    success=success,
                    error=err_msg,
                )
                if callback:
                    callback(record)
        return wrapper
    return decorator


def with_retry(max_retries: int = 2, delay_seconds: float = 0.1, backoff: float = 2.0):
    """Wraps an async function with retry logic and exponential backoff."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay_seconds
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    if retries >= max_retries:
                        raise
                    retries += 1
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


def with_timeout(timeout_seconds: float):
    """Wraps an async function with a timeout constraint."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
        return wrapper
    return decorator
