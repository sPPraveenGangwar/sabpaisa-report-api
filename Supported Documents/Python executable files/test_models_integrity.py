#!/usr/bin/env python3
"""
Test script to verify model integrity with database
"""
import os
import sys
import django
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from apps.transactions.models import (
    TransactionDetail,
    ClientRequestTempStore,
    SettlementReportEntity,
    RefundReportEntity,
    ChargebackEntity,
    SettlementReport,
    SettlementReportDetail,
    RefundProcessEntity
)
from apps.transactions.serializers import (
    TransactionDetailSerializer,
    ClientRequestTempStoreSerializer,
    SettlementReportEntitySerializer,
    RefundReportEntitySerializer,
    ChargebackEntitySerializer
)


def test_model_fields(model_class, table_name):
    """Test if model fields match database columns"""
    logger.info(f"\nTesting {model_class.__name__} against table {table_name}")

    try:
        with connection.cursor() as cursor:
            # Get actual columns from database
            cursor.execute(f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                AND TABLE_SCHEMA = DATABASE()
            """)

            db_columns = set(row[0] for row in cursor.fetchall())

            if not db_columns:
                logger.warning(f"No columns found for table {table_name} - table might not exist")
                return False

            # Get model fields
            model_fields = set(f.name for f in model_class._meta.get_fields())

            # Find mismatches
            missing_in_db = model_fields - db_columns
            extra_in_db = db_columns - model_fields

            if missing_in_db:
                logger.warning(f"Fields in model but NOT in database: {missing_in_db}")

            if extra_in_db:
                logger.info(f"Fields in database but NOT in model: {extra_in_db}")

            if not missing_in_db:
                logger.info(f"✓ All model fields exist in database")
                return True
            else:
                logger.error(f"✗ Model has fields that don't exist in database")
                return False

    except Exception as e:
        logger.error(f"Error testing {model_class.__name__}: {e}")
        return False


def test_model_query(model_class):
    """Test if we can query the model"""
    logger.info(f"Testing query for {model_class.__name__}")

    try:
        # Try to query first record
        count = model_class.objects.using('default').count()
        logger.info(f"✓ Successfully queried {model_class.__name__}, found {count} records")

        # Try to get first record if any exist
        if count > 0:
            first = model_class.objects.using('default').first()
            logger.info(f"✓ Successfully retrieved first record: {first}")

        return True

    except Exception as e:
        logger.error(f"✗ Failed to query {model_class.__name__}: {e}")
        return False


def test_serializer(model_class, serializer_class):
    """Test if serializer works with model"""
    logger.info(f"Testing serializer for {model_class.__name__}")

    try:
        # Try to get a record and serialize it
        if model_class.objects.using('default').exists():
            obj = model_class.objects.using('default').first()
            serializer = serializer_class(obj)
            data = serializer.data
            logger.info(f"✓ Successfully serialized {model_class.__name__}")
            logger.debug(f"Sample data keys: {list(data.keys())[:10]}")
            return True
        else:
            logger.info(f"No records to test serializer for {model_class.__name__}")
            return True

    except Exception as e:
        logger.error(f"✗ Failed to serialize {model_class.__name__}: {e}")
        return False


def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("TESTING MODEL INTEGRITY")
    logger.info("=" * 60)

    # Test configurations
    tests = [
        (TransactionDetail, 'transaction_detail', TransactionDetailSerializer),
        (ClientRequestTempStore, 'client_request_temp_store', ClientRequestTempStoreSerializer),
        (SettlementReportEntity, 'settlement_report_entity', SettlementReportEntitySerializer),
        (RefundReportEntity, 'refund_report_entity', RefundReportEntitySerializer),
        (ChargebackEntity, 'chargback_entity', ChargebackEntitySerializer),
        (SettlementReport, 'settlement_report', None),
        (SettlementReportDetail, 'settlement_report_detail', None),
        (RefundProcessEntity, 'refund_process_entity', None),
    ]

    results = []

    for model_class, table_name, serializer_class in tests:
        logger.info("\n" + "-" * 40)

        # Test model fields
        field_test = test_model_fields(model_class, table_name)

        # Test model query
        query_test = test_model_query(model_class)

        # Test serializer if provided
        serializer_test = True
        if serializer_class:
            serializer_test = test_serializer(model_class, serializer_class)

        results.append({
            'model': model_class.__name__,
            'field_test': field_test,
            'query_test': query_test,
            'serializer_test': serializer_test
        })

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    for result in results:
        status = "✓" if all([result['field_test'], result['query_test'], result['serializer_test']]) else "✗"
        logger.info(f"{status} {result['model']:30} - Fields: {'✓' if result['field_test'] else '✗'}, "
                   f"Query: {'✓' if result['query_test'] else '✗'}, "
                   f"Serializer: {'✓' if result['serializer_test'] else '✗'}")

    # Overall result
    all_passed = all(
        result['field_test'] and result['query_test'] and result['serializer_test']
        for result in results
    )

    logger.info("\n" + "=" * 60)
    if all_passed:
        logger.info("✓ ALL TESTS PASSED - Models are properly configured")
    else:
        logger.warning("✗ SOME TESTS FAILED - Review the issues above")
    logger.info("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()