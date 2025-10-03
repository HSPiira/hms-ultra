"""
Reporting and Analytics Engine
Implements SOLID principles for comprehensive reporting and analytics
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from django.db import models, connection
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q

from core.models import (
    Claim, Member, Hospital, Scheme, Company, BillingSession,
    ClaimPayment, MemberDependant
)


class ReportType(Enum):
    """Report type enumeration"""
    CLAIMS_SUMMARY = "CLAIMS_SUMMARY"
    MEMBER_ANALYTICS = "MEMBER_ANALYTICS"
    PROVIDER_ANALYTICS = "PROVIDER_ANALYTICS"
    FINANCIAL_SUMMARY = "FINANCIAL_SUMMARY"
    UTILIZATION_REPORT = "UTILIZATION_REPORT"
    PAYMENT_ANALYSIS = "PAYMENT_ANALYSIS"


class ReportFormat(Enum):
    """Report format enumeration"""
    JSON = "JSON"
    CSV = "CSV"
    PDF = "PDF"
    EXCEL = "EXCEL"


class ReportPeriod(Enum):
    """Report period enumeration"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"


# =============================================================================
# INTERFACES (SOLID: Interface Segregation Principle)
# =============================================================================

class IReportGenerator(ABC):
    """Interface for report generation"""
    
    @abstractmethod
    def generate_claims_summary(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def generate_member_analytics(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def generate_provider_analytics(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        pass


class IReportExporter(ABC):
    """Interface for report export"""
    
    @abstractmethod
    def export_to_csv(self, data: Dict[str, Any], filename: str) -> str:
        pass
    
    @abstractmethod
    def export_to_pdf(self, data: Dict[str, Any], filename: str) -> str:
        pass
    
    @abstractmethod
    def export_to_excel(self, data: Dict[str, Any], filename: str) -> str:
        pass


class IReportScheduler(ABC):
    """Interface for report scheduling"""
    
    @abstractmethod
    def schedule_report(
        self, 
        report_type: ReportType, 
        period: ReportPeriod, 
        recipients: List[str]
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_scheduled_reports(self) -> List[Dict[str, Any]]:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS (SOLID: Single Responsibility Principle)
# =============================================================================

class ReportGenerator(IReportGenerator):
    """Generates various types of reports"""
    
    def generate_claims_summary(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Generate claims summary report"""
        try:
            # Get claims in date range
            claims = Claim.objects.filter(
                service_date__gte=start_date,
                service_date__lte=end_date
            )
            
            # Calculate summary statistics
            total_claims = claims.count()
            total_amount = claims.aggregate(
                total=Sum('hospital_claimamount')
            )['total'] or Decimal('0')
            
            # Status breakdown
            status_breakdown = claims.values('transaction_status').annotate(
                count=Count('id'),
                amount=Sum('hospital_claimamount')
            )
            
            # Top hospitals by claim count
            top_hospitals = claims.values(
                'hospital__hospital_name'
            ).annotate(
                claim_count=Count('id'),
                total_amount=Sum('hospital_claimamount')
            ).order_by('-claim_count')[:10]
            
            # Average processing time (if we had processing dates)
            avg_amount = claims.aggregate(avg=Avg('hospital_claimamount'))['avg'] or Decimal('0')
            
            return {
                'report_type': 'CLAIMS_SUMMARY',
                'period': f"{start_date} to {end_date}",
                'generated_at': timezone.now().isoformat(),
                'summary': {
                    'total_claims': total_claims,
                    'total_amount': float(total_amount),
                    'average_amount': float(avg_amount)
                },
                'status_breakdown': list(status_breakdown),
                'top_hospitals': list(top_hospitals)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'report_type': 'CLAIMS_SUMMARY'
            }
    
    def generate_member_analytics(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Generate member analytics report"""
        try:
            # Get members with claims in date range
            members_with_claims = Member.objects.filter(
                claim__service_date__gte=start_date,
                claim__service_date__lte=end_date
            ).distinct()
            
            # Member statistics
            total_members = Member.objects.count()
            active_members = Member.objects.filter(member_status='ACTIVE').count()
            members_with_claims_count = members_with_claims.count()
            
            # Utilization rate
            utilization_rate = (members_with_claims_count / total_members * 100) if total_members > 0 else 0
            
            # Top members by claim count
            top_members = members_with_claims.annotate(
                claim_count=Count('claim'),
                total_amount=Sum('claim__hospital_claimamount')
            ).order_by('-claim_count')[:10]
            
            # Member status distribution
            status_distribution = Member.objects.values('member_status').annotate(
                count=Count('id')
            )
            
            # Age group analysis (if we had birth dates)
            age_groups = {
                'under_30': 0,
                '30_50': 0,
                'over_50': 0
            }
            
            return {
                'report_type': 'MEMBER_ANALYTICS',
                'period': f"{start_date} to {end_date}",
                'generated_at': timezone.now().isoformat(),
                'summary': {
                    'total_members': total_members,
                    'active_members': active_members,
                    'members_with_claims': members_with_claims_count,
                    'utilization_rate': round(utilization_rate, 2)
                },
                'top_members': [
                    {
                        'member_name': member.member_name,
                        'claim_count': member.claim_count,
                        'total_amount': float(member.total_amount or 0)
                    }
                    for member in top_members
                ],
                'status_distribution': list(status_distribution),
                'age_groups': age_groups
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'report_type': 'MEMBER_ANALYTICS'
            }
    
    def generate_provider_analytics(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Generate provider analytics report"""
        try:
            # Get providers with claims in date range
            providers_with_claims = Hospital.objects.filter(
                claim__service_date__gte=start_date,
                claim__service_date__lte=end_date
            ).distinct()
            
            # Provider statistics
            total_providers = Hospital.objects.count()
            active_providers = Hospital.objects.filter(status='ACTIVE').count()
            providers_with_claims_count = providers_with_claims.count()
            
            # Top providers by claim count
            top_providers = providers_with_claims.annotate(
                claim_count=Count('claim'),
                total_amount=Sum('claim__hospital_claimamount')
            ).order_by('-claim_count')[:10]
            
            # Provider status distribution
            status_distribution = Hospital.objects.values('status').annotate(
                count=Count('id')
            )
            
            # Average claim amount per provider
            avg_claim_amount = providers_with_claims.annotate(
                avg_amount=Avg('claim__hospital_claimamount')
            ).aggregate(overall_avg=Avg('avg_amount'))['overall_avg'] or Decimal('0')
            
            return {
                'report_type': 'PROVIDER_ANALYTICS',
                'period': f"{start_date} to {end_date}",
                'generated_at': timezone.now().isoformat(),
                'summary': {
                    'total_providers': total_providers,
                    'active_providers': active_providers,
                    'providers_with_claims': providers_with_claims_count,
                    'average_claim_amount': float(avg_claim_amount)
                },
                'top_providers': [
                    {
                        'hospital_name': provider.hospital_name,
                        'claim_count': provider.claim_count,
                        'total_amount': float(provider.total_amount or 0)
                    }
                    for provider in top_providers
                ],
                'status_distribution': list(status_distribution)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'report_type': 'PROVIDER_ANALYTICS'
            }


class ReportExporter(IReportExporter):
    """Exports reports to various formats"""
    
    def export_to_csv(self, data: Dict[str, Any], filename: str) -> str:
        """Export report data to CSV format"""
        import csv
        import os
        
        # Create reports directory if it doesn't exist
        reports_dir = 'reports'
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, f"{filename}.csv")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Report Type', 'Period', 'Generated At'])
            writer.writerow([
                data.get('report_type', ''),
                data.get('period', ''),
                data.get('generated_at', '')
            ])
            
            # Write summary data
            if 'summary' in data:
                writer.writerow([])
                writer.writerow(['Summary'])
                for key, value in data['summary'].items():
                    writer.writerow([key, value])
            
            # Write breakdown data
            if 'status_breakdown' in data:
                writer.writerow([])
                writer.writerow(['Status Breakdown'])
                writer.writerow(['Status', 'Count', 'Amount'])
                for item in data['status_breakdown']:
                    writer.writerow([
                        item.get('transaction_status', ''),
                        item.get('count', 0),
                        item.get('amount', 0)
                    ])
        
        return filepath
    
    def export_to_pdf(self, data: Dict[str, Any], filename: str) -> str:
        """Export report data to PDF format"""
        # TODO: Implement PDF generation using reportlab or weasyprint
        # For now, return a placeholder
        return f"PDF export not implemented for {filename}"
    
    def export_to_excel(self, data: Dict[str, Any], filename: str) -> str:
        """Export report data to Excel format"""
        # TODO: Implement Excel generation using openpyxl or xlsxwriter
        # For now, return a placeholder
        return f"Excel export not implemented for {filename}"


class ReportScheduler(IReportScheduler):
    """Schedules and manages report generation"""
    
    def schedule_report(
        self, 
        report_type: ReportType, 
        period: ReportPeriod, 
        recipients: List[str]
    ) -> Dict[str, Any]:
        """Schedule a report for automatic generation"""
        # TODO: Implement actual scheduling using Celery or similar
        # For now, return a placeholder
        return {
            'success': True,
            'message': f'Report {report_type.value} scheduled for {period.value}',
            'recipients': recipients,
            'schedule_id': f"schedule_{report_type.value}_{period.value}_{timezone.now().timestamp()}"
        }
    
    def get_scheduled_reports(self) -> List[Dict[str, Any]]:
        """Get list of scheduled reports"""
        # TODO: Implement actual scheduled reports retrieval
        # For now, return empty list
        return []


# =============================================================================
# BUSINESS RULE COMPOSER (SOLID: Open/Closed Principle)
# =============================================================================

class ReportingEngine:
    """
    Composes reporting and analytics functionality
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(
        self,
        generator: IReportGenerator,
        exporter: IReportExporter,
        scheduler: IReportScheduler
    ):
        self.generator = generator
        self.exporter = exporter
        self.scheduler = scheduler
    
    def generate_report(
        self, 
        report_type: ReportType, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Generate a specific type of report"""
        if report_type == ReportType.CLAIMS_SUMMARY:
            return self.generator.generate_claims_summary(start_date, end_date)
        elif report_type == ReportType.MEMBER_ANALYTICS:
            return self.generator.generate_member_analytics(start_date, end_date)
        elif report_type == ReportType.PROVIDER_ANALYTICS:
            return self.generator.generate_provider_analytics(start_date, end_date)
        else:
            return {
                'error': f'Report type {report_type.value} not implemented'
            }
    
    def export_report(
        self, 
        data: Dict[str, Any], 
        format_type: ReportFormat, 
        filename: str
    ) -> str:
        """Export report to specified format"""
        if format_type == ReportFormat.CSV:
            return self.exporter.export_to_csv(data, filename)
        elif format_type == ReportFormat.PDF:
            return self.exporter.export_to_pdf(data, filename)
        elif format_type == ReportFormat.EXCEL:
            return self.exporter.export_to_excel(data, filename)
        else:
            return f"Export format {format_type.value} not implemented"
    
    def schedule_automatic_report(
        self, 
        report_type: ReportType, 
        period: ReportPeriod, 
        recipients: List[str]
    ) -> Dict[str, Any]:
        """Schedule automatic report generation"""
        return self.scheduler.schedule_report(report_type, period, recipients)
    
    def get_dashboard_metrics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get key metrics for dashboard"""
        try:
            # Claims metrics
            claims = Claim.objects.filter(
                service_date__gte=start_date,
                service_date__lte=end_date
            )
            
            total_claims = claims.count()
            total_amount = claims.aggregate(
                total=Sum('hospital_claimamount')
            )['total'] or Decimal('0')
            
            # Member metrics
            total_members = Member.objects.count()
            active_members = Member.objects.filter(member_status='ACTIVE').count()
            
            # Provider metrics
            total_providers = Hospital.objects.count()
            active_providers = Hospital.objects.filter(status='ACTIVE').count()
            
            # Payment metrics
            payments = ClaimPayment.objects.filter(
                payment_date__gte=start_date,
                payment_date__lte=end_date
            )
            
            total_payments = payments.count()
            total_payment_amount = payments.aggregate(
                total=Sum('payment_amount')
            )['total'] or Decimal('0')
            
            return {
                'period': f"{start_date} to {end_date}",
                'claims': {
                    'total': total_claims,
                    'amount': float(total_amount)
                },
                'members': {
                    'total': total_members,
                    'active': active_members
                },
                'providers': {
                    'total': total_providers,
                    'active': active_providers
                },
                'payments': {
                    'total': total_payments,
                    'amount': float(total_payment_amount)
                }
            }
            
        except Exception as e:
            return {
                'error': str(e)
            }


# =============================================================================
# FACTORY PATTERN (SOLID: Dependency Inversion Principle)
# =============================================================================

class ReportingEngineFactory:
    """Factory for creating reporting engine instances"""
    
    @staticmethod
    def create_reporting_engine() -> ReportingEngine:
        """Create configured reporting engine"""
        generator = ReportGenerator()
        exporter = ReportExporter()
        scheduler = ReportScheduler()
        
        return ReportingEngine(generator, exporter, scheduler)
