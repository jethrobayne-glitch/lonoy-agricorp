"""
Add `units` and `receipt` columns to `finance_transactions` table on PostgreSQL.
This script reads `DATABASE_URL` from the environment and will ALTER the table
only if the columns are missing.
"""
import os
import sys

import psycopg2
from psycopg2 import sql


def main():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print('DATABASE_URL not set; skipping Postgres migration')
        return

    conn = None
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cur = conn.cursor()

        # Check for existing columns
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'finance_transactions' AND table_schema = 'public'
        """)
        existing = {row[0] for row in cur.fetchall()}

        if 'units' not in existing:
            print('Adding units column...')
            cur.execute(sql.SQL("ALTER TABLE finance_transactions ADD COLUMN units INTEGER NOT NULL DEFAULT 1"))
            print('Added units')
        else:
            print('units column already exists')

        if 'receipt' not in existing:
            print('Adding receipt column...')
            cur.execute(sql.SQL("ALTER TABLE finance_transactions ADD COLUMN receipt TEXT"))
            print('Added receipt')
        else:
            print('receipt column already exists')

        conn.commit()
        print('Postgres migration completed')

    except Exception as e:
        if conn:
            conn.rollback()
        print(f'Error during Postgres migration: {e}')
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
