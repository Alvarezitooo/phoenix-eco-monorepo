from phoenix_shared_db.services.supabase_batch_service import (
    SupabaseBatchService as _SupabaseBatchServiceLegacy,
    BatchOperation as _BatchOperationLegacy,
    BatchResult as _BatchResultLegacy,
    init_batch_service as _init_batch_service_legacy,
    get_batch_service as _get_batch_service_legacy,
)
from phoenix_shared_db.services_supabase.supabase_batch_service import (
    SupabaseBatchService as _SupabaseBatchService,
    BatchOperation as _BatchOperation,
    BatchResult as _BatchResult,
    init_batch_service as _init_batch_service,
    get_batch_service as _get_batch_service,
)

# Prefer the new path; fall back to legacy if needed
SupabaseBatchService = _SupabaseBatchService
BatchOperation = _BatchOperation
BatchResult = _BatchResult
init_batch_service = _init_batch_service
get_batch_service = _get_batch_service

__all__ = [
    "SupabaseBatchService",
    "BatchOperation",
    "BatchResult",
    "init_batch_service",
    "get_batch_service",
]


