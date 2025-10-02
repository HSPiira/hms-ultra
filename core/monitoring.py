"""
Monitoring and Health Checks
Implements comprehensive system monitoring
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import psutil
import time
import logging

from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class IHealthChecker(ABC):
    """Interface for health checking"""
    
    @abstractmethod
    def check_database_health(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def check_cache_health(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def check_system_resources(self) -> Dict[str, Any]:
        pass


class IPerformanceTracker(ABC):
    """Interface for performance tracking"""
    
    @abstractmethod
    def track_response_time(self, endpoint: str, response_time: float) -> None:
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        pass


class IAlertManager(ABC):
    """Interface for alert management"""
    
    @abstractmethod
    def check_alerts(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS
# =============================================================================

class HealthChecker(IHealthChecker):
    """Checks system health"""
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Check database size
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_database_size(current_database())")
                db_size = cursor.fetchone()[0]
            
            return {
                'status': 'HEALTHY',
                'response_time': response_time,
                'database_size': db_size,
                'connection_count': len(connection.queries),
                'last_check': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': 'UNHEALTHY',
                'error': str(e),
                'last_check': timezone.now().isoformat()
            }
    
    def check_cache_health(self) -> Dict[str, Any]:
        """Check cache connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test cache connection
            test_key = f"health_check_{int(time.time())}"
            test_value = "test_value"
            
            cache.set(test_key, test_value, 10)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'status': 'HEALTHY' if retrieved_value == test_value else 'UNHEALTHY',
                'response_time': response_time,
                'last_check': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {
                'status': 'UNHEALTHY',
                'error': str(e),
                'last_check': timezone.now().isoformat()
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                'status': 'HEALTHY' if cpu_percent < 80 and memory_percent < 80 else 'WARNING',
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_available': memory_available,
                'disk_percent': disk_percent,
                'disk_free': disk_free,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'last_check': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System resources check failed: {str(e)}")
            return {
                'status': 'UNHEALTHY',
                'error': str(e),
                'last_check': timezone.now().isoformat()
            }


class PerformanceTracker(IPerformanceTracker):
    """Tracks system performance"""
    
    def __init__(self):
        self.metrics = {}
        self.response_times = {}
    
    def track_response_time(self, endpoint: str, response_time: float) -> None:
        """Track API response time"""
        if endpoint not in self.response_times:
            self.response_times[endpoint] = []
        
        self.response_times[endpoint].append({
            'response_time': response_time,
            'timestamp': timezone.now()
        })
        
        # Keep only last 100 measurements per endpoint
        if len(self.response_times[endpoint]) > 100:
            self.response_times[endpoint] = self.response_times[endpoint][-100:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = {}
        
        for endpoint, times in self.response_times.items():
            if times:
                response_times = [t['response_time'] for t in times]
                metrics[endpoint] = {
                    'count': len(response_times),
                    'avg_response_time': sum(response_times) / len(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'last_response_time': times[-1]['response_time']
                }
        
        return metrics


class AlertManager(IAlertManager):
    """Manages system alerts"""
    
    def __init__(self):
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 80,
            'disk_percent': 90,
            'response_time': 5.0,
            'error_rate': 10
        }
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        
        # Check database health
        from .monitoring import HealthChecker
        health_checker = HealthChecker()
        
        db_health = health_checker.check_database_health()
        if db_health['status'] == 'UNHEALTHY':
            alerts.append({
                'type': 'DATABASE_ERROR',
                'severity': 'CRITICAL',
                'message': f"Database health check failed: {db_health.get('error', 'Unknown error')}",
                'timestamp': timezone.now()
            })
        
        # Check cache health
        cache_health = health_checker.check_cache_health()
        if cache_health['status'] == 'UNHEALTHY':
            alerts.append({
                'type': 'CACHE_ERROR',
                'severity': 'HIGH',
                'message': f"Cache health check failed: {cache_health.get('error', 'Unknown error')}",
                'timestamp': timezone.now()
            })
        
        # Check system resources
        system_health = health_checker.check_system_resources()
        if system_health['status'] == 'WARNING':
            if system_health['cpu_percent'] > self.alert_thresholds['cpu_percent']:
                alerts.append({
                    'type': 'HIGH_CPU_USAGE',
                    'severity': 'WARNING',
                    'message': f"High CPU usage: {system_health['cpu_percent']:.1f}%",
                    'timestamp': timezone.now()
                })
            
            if system_health['memory_percent'] > self.alert_thresholds['memory_percent']:
                alerts.append({
                    'type': 'HIGH_MEMORY_USAGE',
                    'severity': 'WARNING',
                    'message': f"High memory usage: {system_health['memory_percent']:.1f}%",
                    'timestamp': timezone.now()
                })
            
            if system_health['disk_percent'] > self.alert_thresholds['disk_percent']:
                alerts.append({
                    'type': 'HIGH_DISK_USAGE',
                    'severity': 'CRITICAL',
                    'message': f"High disk usage: {system_health['disk_percent']:.1f}%",
                    'timestamp': timezone.now()
                })
        
        return alerts
    
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """Send alert notification"""
        try:
            # Log alert
            logger.warning(f"System Alert: {alert['type']} - {alert['message']}")
            
            # TODO: Send to external monitoring system (e.g., Sentry, DataDog, etc.)
            # For now, just log the alert
            
            return True
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
            return False


# =============================================================================
# BUSINESS RULE COMPOSER
# =============================================================================

class MonitoringService:
    """Composes monitoring functionality"""
    
    def __init__(
        self,
        health_checker: IHealthChecker,
        performance_tracker: IPerformanceTracker,
        alert_manager: IAlertManager
    ):
        self.health_checker = health_checker
        self.performance_tracker = performance_tracker
        self.alert_manager = alert_manager
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        db_health = self.health_checker.check_database_health()
        cache_health = self.health_checker.check_cache_health()
        system_health = self.health_checker.check_system_resources()
        
        # Determine overall health
        overall_status = 'HEALTHY'
        if (db_health['status'] == 'UNHEALTHY' or 
            cache_health['status'] == 'UNHEALTHY' or 
            system_health['status'] == 'UNHEALTHY'):
            overall_status = 'UNHEALTHY'
        elif system_health['status'] == 'WARNING':
            overall_status = 'WARNING'
        
        return {
            'overall_status': overall_status,
            'database': db_health,
            'cache': cache_health,
            'system': system_health,
            'timestamp': timezone.now().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_tracker.get_performance_metrics()
    
    def track_api_call(self, endpoint: str, response_time: float) -> None:
        """Track API call performance"""
        self.performance_tracker.track_response_time(endpoint, response_time)
    
    def check_and_send_alerts(self) -> List[Dict[str, Any]]:
        """Check for alerts and send notifications"""
        alerts = self.alert_manager.check_alerts()
        
        for alert in alerts:
            self.alert_manager.send_alert(alert)
        
        return alerts
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get monitoring dashboard data"""
        health = self.get_system_health()
        performance = self.get_performance_metrics()
        alerts = self.check_and_send_alerts()
        
        return {
            'health': health,
            'performance': performance,
            'alerts': alerts,
            'timestamp': timezone.now().isoformat()
        }


# =============================================================================
# FACTORY PATTERN
# =============================================================================

class MonitoringFactory:
    """Factory for creating monitoring instances"""
    
    @staticmethod
    def create_monitoring_service() -> MonitoringService:
        """Create configured monitoring service"""
        health_checker = HealthChecker()
        performance_tracker = PerformanceTracker()
        alert_manager = AlertManager()
        
        return MonitoringService(
            health_checker, performance_tracker, alert_manager
        )
