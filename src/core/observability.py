from prometheus_client import Counter, Histogram, make_asgi_app
from fastapi import FastAPI, Request
import time
import os

# Try to import OpenTelemetry components
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    OTEL_AVAILABLE = True
except ImportError as e:
    OTEL_AVAILABLE = False
    print(f"[observability] OpenTelemetry not fully available: {e}")

# ---- tracing ----
if OTEL_AVAILABLE:
    trace.set_tracer_provider(TracerProvider())

    # Try OTLP exporter (Tempo), fall back to console for local dev
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if otlp_endpoint:
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))
        except Exception as e:
            print(f"[observability] OTLP exporter failed, falling back to console: {e}")
            console_exporter = ConsoleSpanExporter()
            trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(console_exporter))
    else:
        # No OTLP endpoint configured, use console exporter for local development
        console_exporter = ConsoleSpanExporter()
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(console_exporter))

# ---- metrics ----
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency", ["method", "endpoint"]
)

def init_observability(app: FastAPI):
    if OTEL_AVAILABLE:
        # Try to instrument, but skip if dependencies are missing
        try:
            FastAPIInstrumentor.instrument_app(app)
        except ImportError:
            print("[observability] FastAPI instrumentation skipped (missing dependencies)")
        try:
            AsyncPGInstrumentor().instrument()
        except ImportError:
            print("[observability] AsyncPG instrumentation skipped (missing dependencies)")
        try:
            RedisInstrumentor().instrument()
        except ImportError:
            print("[observability] Redis instrumentation skipped (missing dependencies)")

    @app.middleware("http")
    async def prom_middleware(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, request.url.path).observe(duration)
        return response

    # expose /metrics
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)