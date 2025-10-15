"""
Views for reports app
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, FileResponse
from django.utils import timezone
import os
import logging
import json
from datetime import datetime
import io
import uuid

from apps.core.cache import CacheDecorator

logger = logging.getLogger(__name__)

# Try to import pandas, but provide fallback if not available
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logger.warning("Pandas not available. Excel generation will use CSV format.")


class ReportGenerateView(views.APIView):
    """
    Generate various types of reports
    POST /api/v1/reports/generate/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Generate a report based on specified parameters
        """
        logger.info(f"Report generation request | User: {request.user.username}")

        # Extract parameters
        report_type = request.data.get('report_type', 'transaction')
        format_type = request.data.get('format', 'excel')
        date_filter = request.data.get('date_filter', 'month')
        payment_mode = request.data.get('payment_mode', 'ALL')
        status_filter = request.data.get('status', 'ALL')
        merchant_code = request.data.get('merchant_code')
        include_summary = request.data.get('include_summary', True)
        include_charts = request.data.get('include_charts', False)
        max_records = request.data.get('max_records', 50000)

        # Validate report type
        valid_report_types = ['transaction', 'settlement', 'refund', 'chargeback', 'merchant', 'analytics']
        if report_type not in valid_report_types:
            return Response({
                'success': False,
                'error': f'Invalid report_type. Must be one of: {", ".join(valid_report_types)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate format
        valid_formats = ['excel', 'csv', 'pdf', 'json']
        if format_type not in valid_formats:
            return Response({
                'success': False,
                'error': f'Invalid format. Must be one of: {", ".join(valid_formats)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate task ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Log report generation details
        logger.info(f"Report generation initiated | Task ID: {task_id} | Type: {report_type} | Format: {format_type}")

        # Estimate time based on records
        if max_records <= 10000:
            estimated_time = "2-5 seconds"
        elif max_records <= 50000:
            estimated_time = "5-10 seconds for 50K records"
        elif max_records <= 100000:
            estimated_time = "10-20 seconds for 100K records"
        else:
            estimated_time = "20-60 seconds for large datasets"

        # In production, this would initiate an async task using Celery
        # For now, we'll simulate the task creation
        try:
            # Here you would typically call a Celery task like:
            # from apps.reports.tasks import generate_report_task
            # generate_report_task.delay(
            #     task_id=task_id,
            #     user_id=request.user.id,
            #     report_type=report_type,
            #     format_type=format_type,
            #     filters={
            #         'date_filter': date_filter,
            #         'payment_mode': payment_mode,
            #         'status': status_filter,
            #         'merchant_code': merchant_code,
            #         'include_summary': include_summary,
            #         'include_charts': include_charts,
            #         'max_records': max_records
            #     }
            # )

            # Simulate successful task creation
            response_data = {
                'success': True,
                'message': 'Report generation initiated',
                'task_id': task_id,
                'report_type': report_type,
                'format': format_type,
                'estimated_time': estimated_time
            }

            logger.info(f"Report task created successfully | Task ID: {task_id}")
            return Response(response_data, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            logger.error(f"Failed to initiate report generation | Error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to initiate report generation',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportDownloadView(views.APIView):
    """
    Download generated report
    GET /api/v1/reports/download/<task_id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        """
        Download report file by task ID
        """
        logger.info(f"Report download request | User: {request.user.username} | Task ID: {task_id}")

        # In production, you would:
        # 1. Check if the task belongs to the user
        # 2. Check if the file exists in storage (S3, local filesystem, etc.)
        # 3. Serve the actual file

        # For now, generate a sample file
        try:
            # Create sample data
            data = {
                'Transaction ID': ['SP202412270001', 'SP202412270002', 'SP202412270003'],
                'Client Transaction ID': ['MERC001_TXN_001', 'MERC001_TXN_002', 'MERC001_TXN_003'],
                'Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 3,
                'Status': ['SUCCESS', 'SUCCESS', 'FAILED'],
                'Amount': [1000.00, 2500.00, 750.00],
                'Payment Mode': ['UPI', 'CREDIT_CARD', 'DEBIT_CARD'],
                'Client Name': ['ABC Merchants Pvt Ltd'] * 3
            }

            if HAS_PANDAS:
                # Create DataFrame
                df = pd.DataFrame(data)

                # Create Excel file in memory
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Transactions', index=False)

                    # Add summary sheet
                    summary_data = {
                        'Metric': ['Total Transactions', 'Successful', 'Failed', 'Total Amount'],
                        'Value': [3, 2, 1, 4250.00]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)

                output.seek(0)

                # Create response
                response = HttpResponse(
                    output.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="transaction_report_{task_id}.xlsx"'
            else:
                # Fallback to CSV if pandas not available
                import csv
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data.keys())
                writer.writeheader()

                # Write rows
                for i in range(len(data['Transaction ID'])):
                    row = {key: values[i] for key, values in data.items()}
                    writer.writerow(row)

                # Create response
                response = HttpResponse(output.getvalue(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="transaction_report_{task_id}.csv"'

            logger.info(f"Report downloaded successfully | User: {request.user.username} | Task ID: {task_id}")
            return response

        except Exception as e:
            logger.error(f"Error generating report | Task ID: {task_id} | Error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to generate report',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportStatusView(views.APIView):
    """
    Check report generation status
    GET /api/v1/reports/status/<task_id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        """
        Check status of report generation task
        """
        logger.info(f"Report status check | User: {request.user.username} | Task ID: {task_id}")

        # In production, check actual task status from Celery
        # For now, return mock status

        # Simulate different statuses based on task_id timestamp
        if 'task_' in task_id:
            try:
                # Extract timestamp from task_id
                timestamp_str = task_id.split('_')[1] + task_id.split('_')[2].split('-')[0] if '-' in task_id else task_id.split('_')[1] + task_id.split('_')[2][:6]

                # For demo, all tasks are completed
                status_response = {
                    'success': True,
                    'task_id': task_id,
                    'status': 'COMPLETED',
                    'progress': 100,
                    'message': 'Report generated successfully',
                    'download_url': f'/api/v1/reports/download/{task_id}/',
                    'created_at': timezone.now().isoformat(),
                    'completed_at': timezone.now().isoformat()
                }
            except (IndexError, ValueError, TypeError):
                status_response = {
                    'success': True,
                    'task_id': task_id,
                    'status': 'PENDING',
                    'progress': 50,
                    'message': 'Report generation in progress',
                    'created_at': timezone.now().isoformat()
                }
        else:
            status_response = {
                'success': False,
                'error': 'Invalid task ID format'
            }

        return Response(status_response)


class ReportListView(views.APIView):
    """
    List user's generated reports
    GET /api/v1/reports/list/
    """
    permission_classes = [IsAuthenticated]

    @CacheDecorator.cache_result(timeout=300, key_prefix='report_list')  # 5 min cache
    def get(self, request):
        """
        Get list of user's generated reports
        """
        # In production, fetch from database
        # For now, return mock data

        reports = [
            {
                'task_id': f'task_20241227_143000_{i}',
                'type': 'transaction_report',
                'status': 'COMPLETED',
                'created_at': '2024-12-27T14:30:00+05:30',
                'completed_at': '2024-12-27T14:30:03+05:30',
                'file_size': '125KB',
                'download_url': f'/api/v1/reports/download/task_20241227_143000_{i}/'
            }
            for i in range(1, 4)
        ]

        return Response({
            'success': True,
            'count': len(reports),
            'reports': reports
        })