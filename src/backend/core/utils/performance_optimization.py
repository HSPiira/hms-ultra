"""
Performance Optimization and Caching
Implements caching, query optimization, and performance monitoring
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import logging

from django.core.cache import cache
from django.db import connection
from django.db.models import QuerySet
from django.conf import settings

logger = logging.getLogger(__name__)


class ICacheManager(ABC):
    """Interface for cache management"""
    
    @abstractmethod
    def get_cached_data(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def set_cached_data(self, key: str, data: Any, timeout: int = 300) -> bool:
        pass
    
    @abstractmethod
    def invalidate_cache(self, pattern: str) -> bool:
        pass


class IQueryOptimizer(ABC):
    """Interface for query optimization"""
    
    @abstractmethod
    def optimize_queryset(self, queryset: QuerySet) -> QuerySet:
        pass
    
    @abstractmethod
    def get_query_performance(self, queryset: QuerySet) -> Dict[str, Any]:
        pass


class IPerformanceMonitor(ABC):
    """Interface for performance monitoring"""
    
    @abstractmethod
    def start_timer(self, operation: str) -> str:
        pass
    
    @abstractmethod
    def end_timer(self, timer_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS
# =============================================================================

class CacheManager(ICacheManager):
    """Manages application caching"""
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Get data from cache"""
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None
    
    def set_cached_data(self, key: str, data: Any, timeout: int = 300) -> bool:
        """Set data in cache"""
        try:
            cache.set(key, data, timeout)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def invalidate_cache(self, pattern: str) -> bool:
        """Invalidate cache by pattern"""
        try:
            # Try to use delete_pattern if available (Redis)
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
                return True
            else:
                # Fallback: iterate through keys and delete matching ones
                logger.warning(f"delete_pattern not available, using scoped fallback for pattern: {pattern}")
                
                # Get all cache keys (this might be expensive for large caches)
                try:
                    # Try to get keys using Redis-style pattern matching
                    if hasattr(cache, 'keys'):
                        keys = cache.keys(pattern)
                        for key in keys:
                            cache.delete(key)
                    else:
                        # Last resort: clear all cache if pattern matching not available
                        logger.warning("Pattern-based cache invalidation not supported, clearing all cache")
                        cache.clear()
                except Exception as fallback_error:
                    logger.error(f"Fallback cache invalidation failed: {str(fallback_error)}")
                    # Last resort: clear all cache
                    cache.clear()
                
                return True
        except Exception as e:
            logger.error(f"Cache invalidation error for pattern {pattern}: {str(e)}")
            return False


class QueryOptimizer(IQueryOptimizer):
    """Optimizes database queries"""
    
    def optimize_queryset(self, queryset: QuerySet) -> QuerySet:
        """Optimize queryset with select_related and prefetch_related"""
        try:
            # Add select_related for foreign keys
            if hasattr(queryset.model, 'member'):
                queryset = queryset.select_related('member')
            if hasattr(queryset.model, 'hospital'):
                queryset = queryset.select_related('hospital')
            if hasattr(queryset.model, 'scheme'):
                queryset = queryset.select_related('scheme')
            
            # Add prefetch_related for many-to-many and reverse foreign keys
            if hasattr(queryset.model, 'claimdetail_set'):
                queryset = queryset.prefetch_related('claimdetail_set')
            if hasattr(queryset.model, 'claimpayment_set'):
                queryset = queryset.prefetch_related('claimpayment_set')
            
            return queryset
        except Exception as e:
            logger.error(f"Query optimization error: {str(e)}")
            return queryset
    
    def get_query_performance(self, queryset: QuerySet) -> Dict[str, Any]:
        """Analyze query performance"""
        try:
            # Get query count before execution
            initial_queries = len(connection.queries)
            
            # Execute query
            start_time = time.time()
            results = list(queryset)
            end_time = time.time()
            
            # Get query count after execution
            final_queries = len(connection.queries)
            query_count = final_queries - initial_queries
            
            return {
                'execution_time': end_time - start_time,
                'query_count': query_count,
                'result_count': len(results),
                'queries': connection.queries[initial_queries:final_queries]
            }
        except Exception as e:
            logger.error(f"Query performance analysis error: {str(e)}")
            return {'error': str(e)}


class PerformanceMonitor(IPerformanceMonitor):
    """Monitors application performance"""
    
    def __init__(self):
        self.timers = {}
    
    def start_timer(self, operation: str) -> str:
        """Start performance timer"""
        timer_id = f"{operation}_{int(time.time() * 1000)}"
        self.timers[timer_id] = {
            'operation': operation,
            'start_time': time.time(),
            'start_datetime': datetime.now()
        }
        return timer_id
    
    def end_timer(self, timer_id: str) -> Dict[str, Any]:
        """End performance timer and return metrics"""
        if timer_id not in self.timers:
            return {'error': 'Timer not found'}
        
        timer_data = self.timers[timer_id]
        end_time = time.time()
        execution_time = end_time - timer_data['start_time']
        
        metrics = {
            'operation': timer_data['operation'],
            'execution_time': execution_time,
            'start_time': timer_data['start_datetime'].isoformat(),
            'end_time': datetime.now().isoformat()
        }
        
        # Log performance metrics
        if execution_time > 1.0:  # Log slow operations
            logger.warning(f"Slow operation: {timer_data['operation']} took {execution_time:.2f}s")
        
        # Remove timer
        del self.timers[timer_id]
        
        return metrics
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get overall performance metrics"""
        return {
            'active_timers': len(self.timers),
            'timers': list(self.timers.keys())
        }


# =============================================================================
# BUSINESS RULE COMPOSER
# =============================================================================

class PerformanceOptimizationService:
    """Composes performance optimization functionality"""
    
    def __init__(
        self,
        cache_manager: ICacheManager,
        query_optimizer: IQueryOptimizer,
        performance_monitor: IPerformanceMonitor
    ):
        self.cache_manager = cache_manager
        self.query_optimizer = query_optimizer
        self.performance_monitor = performance_monitor
    
    def get_cached_member_data(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get cached member data"""
        cache_key = f"member_{member_id}"
        return self.cache_manager.get_cached_data(cache_key)
    
    def cache_member_data(self, member_id: str, data: Dict[str, Any]) -> bool:
        """Cache member data"""
        cache_key = f"member_{member_id}"
        return self.cache_manager.set_cached_data(cache_key, data, timeout=600)
    
    def get_cached_provider_data(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get cached provider data"""
        cache_key = f"provider_{provider_id}"
        return self.cache_manager.get_cached_data(cache_key)
    
    def cache_provider_data(self, provider_id: str, data: Dict[str, Any]) -> bool:
        """Cache provider data"""
        cache_key = f"provider_{provider_id}"
        return self.cache_manager.set_cached_data(cache_key, data, timeout=600)
    
    def optimize_claims_queryset(self, queryset: QuerySet) -> QuerySet:
        """Optimize claims queryset"""
        return self.query_optimizer.optimize_queryset(queryset)
    
    def optimize_members_queryset(self, queryset: QuerySet) -> QuerySet:
        """Optimize members queryset"""
        return self.query_optimizer.optimize_queryset(queryset)
    
    def optimize_providers_queryset(self, queryset: QuerySet) -> QuerySet:
        """Optimize providers queryset"""
        return self.query_optimizer.optimize_queryset(queryset)
    
    def monitor_operation(self, operation: str):
        """Context manager for monitoring operations"""
        return OperationTimer(self.performance_monitor, operation)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return self.performance_monitor.get_performance_metrics()


class OperationTimer:
    """Context manager for operation timing"""
    
    def __init__(self, monitor: IPerformanceMonitor, operation: str):
        self.monitor = monitor
        self.operation = operation
        self.timer_id = None
    
    def __enter__(self):
        self.timer_id = self.monitor.start_timer(self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timer_id:
            metrics = self.monitor.end_timer(self.timer_id)
            logger.info(f"Operation {self.operation} completed in {metrics['execution_time']:.2f}s")


# =============================================================================
# FACTORY PATTERN
# =============================================================================

class PerformanceOptimizationFactory:
    """Factory for creating performance optimization instances"""
    
    @staticmethod
    def create_performance_service() -> PerformanceOptimizationService:
        """Create configured performance optimization service"""
        cache_manager = CacheManager()
        query_optimizer = QueryOptimizer()
        performance_monitor = PerformanceMonitor()
        
        return PerformanceOptimizationService(
            cache_manager, query_optimizer, performance_monitor
        )
