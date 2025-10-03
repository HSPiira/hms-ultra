"""
Notification and Alert System
Implements SOLID principles for comprehensive notification management
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import logging

from django.db import models, IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from core.models import Claim, Member, Hospital, Scheme, Company


logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification type enumeration"""
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    IN_APP = "IN_APP"
    SYSTEM = "SYSTEM"


class NotificationPriority(Enum):
    """Notification priority enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class NotificationStatus(Enum):
    """Notification status enumeration"""
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    READ = "READ"


class AlertType(Enum):
    """Alert type enumeration"""
    CLAIM_SUBMITTED = "CLAIM_SUBMITTED"
    CLAIM_APPROVED = "CLAIM_APPROVED"
    CLAIM_REJECTED = "CLAIM_REJECTED"
    CLAIM_PAID = "CLAIM_PAID"
    MEMBER_ENROLLED = "MEMBER_ENROLLED"
    MEMBER_DEACTIVATED = "MEMBER_DEACTIVATED"
    PROVIDER_REGISTERED = "PROVIDER_REGISTERED"
    PROVIDER_SUSPENDED = "PROVIDER_SUSPENDED"
    PAYMENT_OVERDUE = "PAYMENT_OVERDUE"
    SYSTEM_ERROR = "SYSTEM_ERROR"


# =============================================================================
# INTERFACES (SOLID: Interface Segregation Principle)
# =============================================================================

class INotificationChannel(ABC):
    """Interface for notification channels"""
    
    @abstractmethod
    def send_notification(
        self, 
        recipient: str, 
        subject: str, 
        message: str, 
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        pass


class IAlertManager(ABC):
    """Interface for alert management"""
    
    @abstractmethod
    def create_alert(
        self, 
        alert_type: AlertType, 
        recipient: str, 
        message: str, 
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def process_alert(self, alert_id: str) -> Dict[str, Any]:
        pass


class INotificationTemplate(ABC):
    """Interface for notification templates"""
    
    @abstractmethod
    def get_template(self, template_name: str) -> str:
        pass
    
    @abstractmethod
    def render_template(
        self, 
        template_name: str, 
        context: Dict[str, Any]
    ) -> str:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS (SOLID: Single Responsibility Principle)
# =============================================================================

class EmailNotificationChannel(INotificationChannel):
    """Email notification channel implementation"""
    
    def send_notification(
        self, 
        recipient: str, 
        subject: str, 
        message: str, 
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        """Send email notification"""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False
            )
            
            return {
                'success': True,
                'channel': 'EMAIL',
                'recipient': recipient,
                'status': NotificationStatus.SENT.value
            }
            
        except Exception as e:
            return {
                'success': False,
                'channel': 'EMAIL',
                'recipient': recipient,
                'error': str(e),
                'status': NotificationStatus.FAILED.value
            }


class SMSNotificationChannel(INotificationChannel):
    """SMS notification channel implementation"""
    
    def send_notification(
        self, 
        recipient: str, 
        subject: str, 
        message: str, 
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        """Send SMS notification"""
        # TODO: Implement actual SMS sending using Twilio, AWS SNS, etc.
        # For now, return a placeholder
        return {
            'success': True,
            'channel': 'SMS',
            'recipient': recipient,
            'status': NotificationStatus.SENT.value,
            'message': 'SMS notification sent (placeholder)'
        }


class PushNotificationChannel(INotificationChannel):
    """Push notification channel implementation"""
    
    def send_notification(
        self, 
        recipient: str, 
        subject: str, 
        message: str, 
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        """Send push notification"""
        # TODO: Implement actual push notification using FCM, APNS, etc.
        # For now, return a placeholder
        return {
            'success': True,
            'channel': 'PUSH',
            'recipient': recipient,
            'status': NotificationStatus.SENT.value,
            'message': 'Push notification sent (placeholder)'
        }


class NotificationTemplate(INotificationTemplate):
    """Notification template management"""
    
    def __init__(self):
        self.templates = {
            'claim_submitted': """
            Dear {member_name},
            
            Your claim #{claim_number} has been submitted successfully.
            
            Claim Details:
            - Amount: {amount}
            - Hospital: {hospital_name}
            - Service Date: {service_date}
            
            We will process your claim and notify you of the outcome.
            
            Best regards,
            HMS Team
            """,
            
            'claim_approved': """
            Dear {member_name},
            
            Great news! Your claim #{claim_number} has been approved.
            
            Approved Amount: {approved_amount}
            Payment will be processed within 3-5 business days.
            
            Best regards,
            HMS Team
            """,
            
            'claim_rejected': """
            Dear {member_name},
            
            Your claim #{claim_number} has been reviewed and unfortunately rejected.
            
            Reason: {rejection_reason}
            
            If you have any questions, please contact our support team.
            
            Best regards,
            HMS Team
            """,
            
            'member_enrolled': """
            Dear {member_name},
            
            Welcome to our health insurance scheme!
            
            Your membership details:
            - Member ID: {member_id}
            - Scheme: {scheme_name}
            - Effective Date: {effective_date}
            
            Best regards,
            HMS Team
            """,
            
            'provider_registered': """
            Dear {contact_person},
            
            Your hospital {hospital_name} has been successfully registered.
            
            Registration Details:
            - Hospital ID: {hospital_id}
            - Reference: {hospital_reference}
            - Status: Pending Approval
            
            We will review your application and notify you of the outcome.
            
            Best regards,
            HMS Team
            """
        }
    
    def get_template(self, template_name: str) -> str:
        """Get notification template"""
        return self.templates.get(template_name, "")
    
    def render_template(
        self, 
        template_name: str, 
        context: Dict[str, Any]
    ) -> str:
        """Render template with context"""
        template = self.get_template(template_name)
        if not template:
            return ""
        
        try:
            return template.format(**context)
        except KeyError as e:
            return f"Template rendering error: Missing key {e}"


class AlertManager(IAlertManager):
    """Manages alerts and notifications"""
    
    def __init__(self, template_manager: INotificationTemplate):
        self.template_manager = template_manager
        self.email_channel = EmailNotificationChannel()
        self.sms_channel = SMSNotificationChannel()
        self.push_channel = PushNotificationChannel()
    
    def create_alert(
        self, 
        alert_type: AlertType, 
        recipient: str, 
        message: str, 
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        """Create and send alert"""
        try:
            # Determine notification channels based on priority
            channels = self._get_channels_for_priority(priority)
            
            results = []
            successful_channels = []
            failed_channels = []
            
            for channel in channels:
                try:
                    result = channel.send_notification(
                        recipient=recipient,
                        subject=self._get_subject_for_alert_type(alert_type),
                        message=message,
                        priority=priority
                    )
                    results.append(result)
                    
                    # Track success/failure per channel
                    if result.get('success', False):
                        successful_channels.append(result)
                    else:
                        failed_channels.append(result)
                        
                except Exception as channel_error:
                    # Log individual channel exceptions but don't stop processing other channels
                    logger.error(f"Channel {channel.__class__.__name__} failed: {str(channel_error)}")
                    error_result = {
                        'success': False,
                        'channel': channel.__class__.__name__,
                        'error': str(channel_error),
                        'status': 'FAILED'
                    }
                    results.append(error_result)
                    failed_channels.append(error_result)
            
            # Determine overall success: at least one channel must succeed
            overall_success = len(successful_channels) > 0
            
            # Build response with detailed channel results
            response = {
                'success': overall_success,
                'alert_type': alert_type.value,
                'recipient': recipient,
                'priority': priority.value,
                'channels': results,
                'successful_channels': len(successful_channels),
                'failed_channel_count': len(failed_channels)
            }
            
            # Add failure details if there were any failures
            if failed_channels:
                response['failed_channels'] = failed_channels
                if not overall_success:
                    response['error'] = 'All notification channels failed'
                else:
                    response['partial_failures'] = failed_channels
            
            return response
            
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid parameters for alert creation: {str(e)}")
            return {
                'success': False,
                'error': f'Invalid parameters: {str(e)}',
                'alert_type': alert_type.value,
                'recipient': recipient,
                'priority': priority.value
            }
        except Exception as e:
            # Log the exception and propagate it
            logger.error(f"Alert creation failed: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'alert_type': alert_type.value,
                'recipient': recipient,
                'priority': priority.value
            }
    
    def process_alert(self, alert_id: str) -> Dict[str, Any]:
        """Process a specific alert"""
        # TODO: Implement alert processing logic
        # For now, return a placeholder
        return {
            'success': True,
            'alert_id': alert_id,
            'status': 'PROCESSED'
        }
    
    def _get_channels_for_priority(self, priority: NotificationPriority) -> List[INotificationChannel]:
        """Get notification channels based on priority"""
        if priority == NotificationPriority.CRITICAL:
            return [self.email_channel, self.sms_channel, self.push_channel]
        elif priority == NotificationPriority.HIGH:
            return [self.email_channel, self.push_channel]
        elif priority == NotificationPriority.MEDIUM:
            return [self.email_channel]
        else:
            return [self.email_channel]
    
    def _get_subject_for_alert_type(self, alert_type: AlertType) -> str:
        """Get subject line for alert type"""
        subjects = {
            AlertType.CLAIM_SUBMITTED: "Claim Submitted - HMS",
            AlertType.CLAIM_APPROVED: "Claim Approved - HMS",
            AlertType.CLAIM_REJECTED: "Claim Rejected - HMS",
            AlertType.CLAIM_PAID: "Claim Paid - HMS",
            AlertType.MEMBER_ENROLLED: "Welcome to HMS",
            AlertType.MEMBER_DEACTIVATED: "Member Deactivated - HMS",
            AlertType.PROVIDER_REGISTERED: "Provider Registration - HMS",
            AlertType.PROVIDER_SUSPENDED: "Provider Suspended - HMS",
            AlertType.PAYMENT_OVERDUE: "Payment Overdue - HMS",
            AlertType.SYSTEM_ERROR: "System Alert - HMS"
        }
        return subjects.get(alert_type, "HMS Notification")


# =============================================================================
# BUSINESS RULE COMPOSER (SOLID: Open/Closed Principle)
# =============================================================================

class NotificationService:
    """
    Composes notification and alert functionality
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(
        self,
        alert_manager: IAlertManager,
        template_manager: INotificationTemplate
    ):
        self.alert_manager = alert_manager
        self.template_manager = template_manager
    
    def notify_claim_submitted(self, claim_id: str) -> Dict[str, Any]:
        """Notify stakeholders of claim submission"""
        try:
            claim = Claim.objects.get(id=claim_id)
            member = claim.member
            
            # Render notification template
            context = {
                'member_name': member.member_name,
                'claim_number': claim.claimform_number,
                'amount': claim.hospital_claimamount,
                'hospital_name': claim.hospital.hospital_name,
                'service_date': claim.service_date
            }
            
            message = self.template_manager.render_template('claim_submitted', context)
            
            # Send notification
            return self.alert_manager.create_alert(
                alert_type=AlertType.CLAIM_SUBMITTED,
                recipient=member.email or 'no-email@example.com',
                message=message,
                priority=NotificationPriority.MEDIUM
            )
            
        except Claim.DoesNotExist:
            return {
                'success': False,
                'error': 'Claim not found'
            }
        except (ValueError, IntegrityError, ValidationError) as e:
            return {
                'success': False,
                'error': f'Validation or database error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def notify_claim_approved(self, claim_id: str) -> Dict[str, Any]:
        """Notify stakeholders of claim approval"""
        try:
            claim = Claim.objects.get(id=claim_id)
            member = claim.member
            
            # Render notification template
            context = {
                'member_name': member.member_name,
                'claim_number': claim.claimform_number,
                'approved_amount': claim.member_claimamount
            }
            
            message = self.template_manager.render_template('claim_approved', context)
            
            # Send notification
            return self.alert_manager.create_alert(
                alert_type=AlertType.CLAIM_APPROVED,
                recipient=member.email or 'no-email@example.com',
                message=message,
                priority=NotificationPriority.HIGH
            )
            
        except Claim.DoesNotExist:
            return {
                'success': False,
                'error': 'Claim not found'
            }
        except (ValueError, IntegrityError, ValidationError) as e:
            return {
                'success': False,
                'error': f'Validation or database error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def notify_claim_rejected(self, claim_id: str, reason: str) -> Dict[str, Any]:
        """Notify stakeholders of claim rejection"""
        try:
            claim = Claim.objects.get(id=claim_id)
            member = claim.member
            
            # Render notification template
            context = {
                'member_name': member.member_name,
                'claim_number': claim.claimform_number,
                'rejection_reason': reason
            }
            
            message = self.template_manager.render_template('claim_rejected', context)
            
            # Send notification
            return self.alert_manager.create_alert(
                alert_type=AlertType.CLAIM_REJECTED,
                recipient=member.email or 'no-email@example.com',
                message=message,
                priority=NotificationPriority.HIGH
            )
            
        except Claim.DoesNotExist:
            return {
                'success': False,
                'error': 'Claim not found'
            }
        except (ValueError, IntegrityError, ValidationError) as e:
            return {
                'success': False,
                'error': f'Validation or database error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def notify_member_enrolled(self, member_id: str) -> Dict[str, Any]:
        """Notify member of enrollment"""
        try:
            member = Member.objects.get(id=member_id)
            
            # Render notification template
            context = {
                'member_name': member.member_name,
                'member_id': member.id,
                'scheme_name': member.scheme.scheme_name if member.scheme else 'N/A',
                'effective_date': member.date_of_joining or timezone.now().date()
            }
            
            message = self.template_manager.render_template('member_enrolled', context)
            
            # Send notification
            return self.alert_manager.create_alert(
                alert_type=AlertType.MEMBER_ENROLLED,
                recipient=member.email or 'no-email@example.com',
                message=message,
                priority=NotificationPriority.MEDIUM
            )
            
        except Member.DoesNotExist:
            return {
                'success': False,
                'error': 'Member not found'
            }
        except (ValueError, IntegrityError, ValidationError) as e:
            return {
                'success': False,
                'error': f'Validation or database error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def notify_provider_registered(self, provider_id: str) -> Dict[str, Any]:
        """Notify provider of registration"""
        try:
            provider = Hospital.objects.get(id=provider_id)
            
            # Render notification template
            context = {
                'contact_person': provider.contact_person,
                'hospital_name': provider.hospital_name,
                'hospital_id': provider.id,
                'hospital_reference': provider.hospital_reference
            }
            
            message = self.template_manager.render_template('provider_registered', context)
            
            # Send notification
            return self.alert_manager.create_alert(
                alert_type=AlertType.PROVIDER_REGISTERED,
                recipient=provider.hospital_email or 'no-email@example.com',
                message=message,
                priority=NotificationPriority.MEDIUM
            )
            
        except Hospital.DoesNotExist:
            return {
                'success': False,
                'error': 'Provider not found'
            }
        except (ValueError, IntegrityError, ValidationError) as e:
            return {
                'success': False,
                'error': f'Validation or database error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def send_system_alert(
        self, 
        message: str, 
        priority: NotificationPriority = NotificationPriority.HIGH
    ) -> Dict[str, Any]:
        """Send system alert to administrators"""
        return self.alert_manager.create_alert(
            alert_type=AlertType.SYSTEM_ERROR,
            recipient=settings.ADMINS[0][1] if settings.ADMINS else 'admin@example.com',
            message=message,
            priority=priority
        )


# =============================================================================
# FACTORY PATTERN (SOLID: Dependency Inversion Principle)
# =============================================================================

class NotificationServiceFactory:
    """Factory for creating notification service instances"""
    
    @staticmethod
    def create_notification_service() -> NotificationService:
        """Create configured notification service"""
        template_manager = NotificationTemplate()
        alert_manager = AlertManager(template_manager)
        
        return NotificationService(alert_manager, template_manager)
