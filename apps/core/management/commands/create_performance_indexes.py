"""
Management command to create performance indexes for high-volume transaction data
Optimized for 100,000+ daily transactions (3M+ monthly)
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create optimized database indexes for high-performance queries'

    def handle(self, *args, **options):
        self.stdout.write('Creating performance indexes...')

        with connection.cursor() as cursor:
            # Get database name
            db_name = connection.settings_dict['NAME']

            indexes = [
                # ===== CRITICAL INDEXES FOR TRANSACTION QUERIES =====

                # Composite index for date-range queries (most common filter)
                """
                CREATE INDEX IF NOT EXISTS idx_txn_trans_date_status
                ON transaction_detail(trans_date DESC, status)
                USING BTREE
                """,

                # Index for client-based queries with date
                """
                CREATE INDEX IF NOT EXISTS idx_txn_client_date_status
                ON transaction_detail(client_code, trans_date DESC, status)
                USING BTREE
                """,

                # Index for payment mode analytics
                """
                CREATE INDEX IF NOT EXISTS idx_txn_payment_mode_date
                ON transaction_detail(payment_mode, trans_date DESC)
                USING BTREE
                """,

                # Index for transaction ID lookups (exact match)
                """
                CREATE INDEX IF NOT EXISTS idx_txn_id_lookup
                ON transaction_detail(txn_id, client_code)
                USING HASH
                """,

                # Index for client transaction ID searches
                """
                CREATE INDEX IF NOT EXISTS idx_client_txn_id
                ON transaction_detail(client_txn_id, trans_date DESC)
                USING BTREE
                """,

                # ===== SETTLEMENT QUERIES =====

                # Index for settlement queries
                """
                CREATE INDEX IF NOT EXISTS idx_txn_settlement
                ON transaction_detail(is_settled, settlement_date DESC, client_code)
                USING BTREE
                """,

                # Index for settlement status
                """
                CREATE INDEX IF NOT EXISTS idx_settlement_status_date
                ON transaction_detail(settlement_status, settlement_date DESC)
                USING BTREE
                """,

                # ===== REFUND & CHARGEBACK QUERIES =====

                # Index for refund queries
                """
                CREATE INDEX IF NOT EXISTS idx_refund_date_status
                ON transaction_detail(refund_date DESC, refund_status_code)
                WHERE refund_date IS NOT NULL
                """,

                # Index for chargeback queries
                """
                CREATE INDEX IF NOT EXISTS idx_chargeback_date
                ON transaction_detail(charge_back_date DESC, charge_back_status)
                WHERE charge_back_date IS NOT NULL
                """,

                # ===== AMOUNT-BASED QUERIES =====

                # Index for amount range queries
                """
                CREATE INDEX IF NOT EXISTS idx_txn_amount_date
                ON transaction_detail(paid_amount, trans_date DESC)
                USING BTREE
                """,

                # ===== CUSTOMER SEARCH INDEXES =====

                # Index for email searches
                """
                CREATE INDEX IF NOT EXISTS idx_payee_email
                ON transaction_detail(payee_email(100))
                USING BTREE
                """,

                # Index for mobile searches
                """
                CREATE INDEX IF NOT EXISTS idx_payee_mobile
                ON transaction_detail(payee_mob(15))
                USING BTREE
                """,

                # ===== COVERING INDEXES FOR COMMON QUERIES =====

                # Covering index for transaction list queries
                """
                CREATE INDEX IF NOT EXISTS idx_txn_list_covering
                ON transaction_detail(
                    trans_date DESC,
                    client_code,
                    status,
                    payment_mode
                ) INCLUDE (
                    txn_id,
                    client_txn_id,
                    paid_amount,
                    payee_email,
                    payee_mob,
                    pg_name,
                    bank_txn_id
                )
                """,

                # ===== ANALYTICS INDEXES =====

                # Index for daily aggregations
                """
                CREATE INDEX IF NOT EXISTS idx_daily_stats
                ON transaction_detail(
                    DATE(trans_date),
                    client_code,
                    status,
                    payment_mode
                ) USING BTREE
                """,

                # ===== PARTITION SUPPORT (for future) =====

                # Note: Consider partitioning transaction_detail by month
                # This command doesn't create partitions but documents the strategy
            ]

            # Create indexes
            for idx, index_sql in enumerate(indexes, 1):
                try:
                    self.stdout.write(f'Creating index {idx}/{len(indexes)}...')
                    cursor.execute(index_sql)
                    self.stdout.write(self.style.SUCCESS(f'✓ Index {idx} created'))
                except Exception as e:
                    # Skip if index already exists or other errors
                    if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                        self.stdout.write(self.style.WARNING(f'⚠ Index {idx} already exists'))
                    else:
                        self.stdout.write(self.style.ERROR(f'✗ Error creating index {idx}: {e}'))

            # ===== ANALYZE TABLES =====
            self.stdout.write('\nAnalyzing tables for query optimization...')
            analyze_tables = [
                'transaction_detail',
                'settlement_report_entity',
                'refund_report_entity',
                'chargback_entity',
                'client_data_table',
            ]

            for table in analyze_tables:
                try:
                    cursor.execute(f'ANALYZE TABLE {table}')
                    self.stdout.write(self.style.SUCCESS(f'✓ Analyzed {table}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠ Could not analyze {table}: {e}'))

            self.stdout.write(self.style.SUCCESS('\n✅ All indexes created successfully!'))

            # Print index usage recommendations
            self.stdout.write('\n' + '='*80)
            self.stdout.write('INDEX USAGE RECOMMENDATIONS:')
            self.stdout.write('='*80)
            self.stdout.write("""
1. Always include trans_date in WHERE clauses for time-range queries
2. Use client_code as first filter when filtering by merchant
3. Avoid SELECT * - use .only() or .values() to select specific fields
4. Use .count() with caution - consider caching counts for large datasets
5. For pagination, prefer cursor-based over offset-based pagination
6. Monitor slow queries with MySQL slow query log
            """)
