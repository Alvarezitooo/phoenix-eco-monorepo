"""
Service de batch optimisé pour opérations Supabase.
Permet le batching et les opérations asynchrones pour réduire la latence.

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Performance Architecture Pattern
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class BatchOperation:
    """Représente une opération batch."""

    table: str
    operation: str  # insert, update, delete
    data: Any
    callback: Optional[Callable] = None
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class BatchResult:
    """Résultat d'une opération batch."""

    success: bool
    operation_count: int
    error: Optional[str] = None
    execution_time: float = 0.0


class SupabaseBatchService:
    """✅ Service optimisé pour opérations Supabase par batch."""

    def __init__(self, supabase_client, batch_size: int = 10, flush_interval: float = 2.0):
        """
        Initialise le service batch.

        Args:
            supabase_client: Client Supabase
            batch_size: Taille maximale du batch
            flush_interval: Intervalle de flush automatique (secondes)
        """

        self.client = supabase_client
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        # Queue des opérations
        self._operations: List[BatchOperation] = []
        self._lock = Lock()
        self._executor = ThreadPoolExecutor(max_workers=3)

        # Métriques
        self._total_operations = 0
        self._successful_batches = 0
        self._failed_batches = 0
        self._last_flush = time.time()

        # Démarrer le flush automatique
        self._start_auto_flush()
        logger.info(
            f"✅ SupabaseBatchService initialized (batch_size={batch_size}, flush_interval={flush_interval}s)"
        )

    def queue_insert(self, table: str, data: Any, callback: Optional[Callable] = None) -> None:
        """
        Met en queue une opération d'insertion.

        Args:
            table: Nom de la table
            data: Données à insérer (dict ou list de dict)
            callback: Callback optionnel à exécuter après succès
        """

        operation = BatchOperation(table=table, operation="insert", data=data, callback=callback)

        with self._lock:
            self._operations.append(operation)
            self._total_operations += 1

            # Flush automatique si batch plein
            if len(self._operations) >= self.batch_size:
                self._trigger_flush()

    def queue_update(
        self, table: str, data: Dict[str, Any], filters: Dict[str, Any], callback: Optional[Callable] = None
    ) -> None:
        """
        Met en queue une opération de mise à jour.

        Args:
            table: Nom de la table
            data: Données à mettre à jour
            filters: Filtres WHERE
            callback: Callback optionnel
        """

        operation = BatchOperation(
            table=table,
            operation="update",
            data={"updates": data, "filters": filters},
            callback=callback,
        )

        with self._lock:
            self._operations.append(operation)
            self._total_operations += 1

            if len(self._operations) >= self.batch_size:
                self._trigger_flush()

    def flush_now(self) -> BatchResult:
        """Force le flush immédiat de toutes les opérations en queue."""
        with self._lock:
            if not self._operations:
                return BatchResult(success=True, operation_count=0)

            operations_to_process = self._operations.copy()
            self._operations.clear()

        return self._execute_batch(operations_to_process)

    def _start_auto_flush(self) -> None:
        """Démarre le flush automatique en arrière-plan."""

        def auto_flush_loop():
            while True:
                time.sleep(self.flush_interval)

                with self._lock:
                    should_flush = len(self._operations) > 0 and time.time() - self._last_flush > self.flush_interval

                if should_flush:
                    self._trigger_flush()

        self._executor.submit(auto_flush_loop)

    def _trigger_flush(self) -> None:
        """Déclenche un flush asynchrone."""
        operations_to_process = self._operations.copy()
        self._operations.clear()
        self._last_flush = time.time()

        # Exécuter en arrière-plan
        self._executor.submit(self._execute_batch, operations_to_process)

    def _execute_batch(self, operations: List[BatchOperation]) -> BatchResult:
        """
        Exécute un batch d'opérations.

        Args:
            operations: Liste des opérations à exécuter

        Returns:
            BatchResult: Résultat du batch
        """
        if not operations:
            return BatchResult(success=True, operation_count=0)

        start_time = time.time()

        try:
            # Grouper par table et opération pour optimisation
            grouped_ops = self._group_operations(operations)

            for group_key, group_ops in grouped_ops.items():
                table, operation = group_key

                if operation == "insert":
                    self._execute_insert_batch(table, group_ops)
                elif operation == "update":
                    self._execute_update_batch(table, group_ops)
                # TODO: Ajouter delete si nécessaire

            # Exécuter les callbacks
            self._execute_callbacks(operations)

            execution_time = time.time() - start_time
            self._successful_batches += 1

            logger.info(
                f"✅ Batch executed successfully: {len(operations)} operations in {execution_time:.2f}s"
            )

            return BatchResult(success=True, operation_count=len(operations), execution_time=execution_time)

        except Exception as e:
            self._failed_batches += 1
            logger.error(f"❌ Batch execution failed: {e}")

            # Retry les opérations échouées
            self._retry_failed_operations(operations)

            return BatchResult(
                success=False,
                operation_count=len(operations),
                error=str(e),
                execution_time=time.time() - start_time,
            )

    def _group_operations(self, operations: List[BatchOperation]) -> Dict[tuple, List[BatchOperation]]:
        """Groupe les opérations par table et type."""
        grouped: Dict[tuple, List[BatchOperation]] = {}

        for op in operations:
            key = (op.table, op.operation)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(op)

        return grouped

    def _execute_insert_batch(self, table: str, operations: List[BatchOperation]) -> None:
        """Exécute un batch d'insertions optimisé."""
        # Combiner toutes les données d'insertion
        all_data: List[Any] = []

        for op in operations:
            if isinstance(op.data, list):
                all_data.extend(op.data)
            else:
                all_data.append(op.data)

        # Insérer par chunks pour éviter les timeouts
        chunk_size = min(50, len(all_data))  # Limiter les chunks

        for i in range(0, len(all_data), chunk_size):
            chunk = all_data[i : i + chunk_size]

            try:
                result = self.client.table(table).insert(chunk).execute()
                logger.debug(f"✅ Insert chunk {i//chunk_size + 1}: {len(chunk)} records")
            except Exception as e:
                logger.error(f"❌ Insert chunk {i//chunk_size + 1} failed: {e}")
                raise

    def _execute_update_batch(self, table: str, operations: List[BatchOperation]) -> None:
        """Exécute un batch de mises à jour."""
        for op in operations:
            data = op.data
            updates = data["updates"]
            filters = data["filters"]

            try:
                query = self.client.table(table).update(updates)

                # Appliquer les filtres
                for key, value in filters.items():
                    query = query.eq(key, value)

                result = query.execute()
                logger.debug(f"✅ Update operation on {table}")

            except Exception as e:
                logger.error(f"❌ Update operation failed on {table}: {e}")
                raise

    def _execute_callbacks(self, operations: List[BatchOperation]) -> None:
        """Exécute les callbacks des opérations réussies."""
        for op in operations:
            if op.callback:
                try:
                    op.callback()
                except Exception as e:
                    logger.warning(f"⚠️ Callback execution failed: {e}")

    def _retry_failed_operations(self, operations: List[BatchOperation]) -> None:
        """Remet en queue les opérations échouées pour retry."""
        with self._lock:
            for op in operations:
                if op.retry_count < op.max_retries:
                    op.retry_count += 1
                    self._operations.append(op)
                    logger.info(
                        f"🔄 Retrying operation (attempt {op.retry_count}/{op.max_retries})"
                    )
                else:
                    logger.error(f"❌ Operation failed after {op.max_retries} retries")

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du service."""
        with self._lock:
            queue_size = len(self._operations)

        return {
            "queue_size": queue_size,
            "total_operations": self._total_operations,
            "successful_batches": self._successful_batches,
            "failed_batches": self._failed_batches,
            "batch_success_rate": self._successful_batches
            / max(self._successful_batches + self._failed_batches, 1),
            "last_flush": self._last_flush,
        }

    def shutdown(self) -> None:
        """Arrête le service et flush les opérations restantes."""
        logger.info("🔄 Shutting down SupabaseBatchService...")

        # Flush final
        final_result = self.flush_now()

        # Arrêter l'executor
        self._executor.shutdown(wait=True)

        logger.info(
            f"✅ SupabaseBatchService shutdown complete. Final batch: {final_result.operation_count} operations"
        )


# Instance globale pour l'application
supabase_batch_service: Optional[SupabaseBatchService] = None


def init_batch_service(
    supabase_client, batch_size: int = 10, flush_interval: float = 2.0
) -> SupabaseBatchService:
    """Initialise le service batch global."""
    global supabase_batch_service
    supabase_batch_service = SupabaseBatchService(
        supabase_client, batch_size, flush_interval
    )
    return supabase_batch_service


def get_batch_service() -> Optional[SupabaseBatchService]:
    """Retourne l'instance du service batch."""
    return supabase_batch_service


