import psycopg2
from psycopg2 import Error

clean_script = " \
drop index transactions_products_ix; \
drop index transactions_accounts_ix; \
ALTER TABLE transactions DROP CONSTRAINT transactions_products_fk; \
ALTER TABLE transactions DROP CONSTRAINT transactions_accounts_fk; \
drop table accounts; \
drop table products; \
drop table transactions; \
"

def main():
    host = "postgres" # test with localhost, run on docker with postgres
    database = "postgres"
    user = "postgres"
    pas = "postgres"
    conn = psycopg2.connect(host=host, database=database, user=user, password=pas)
    cur = conn.cursor()

    # init
    try:
        cur.execute(clean_script)
        conn.commit();
        with open("ddl.sql") as ddl:
            cur.execute(ddl.read())
            conn.commit
    except psycopg2.Error as e:
        print(f"Error: {e}")
        conn.rollback()

    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    print(f"Testing if table exists: {cur.fetchall()}")

    # accounts
    with open("data/accounts.csv") as f:
        next(f)
        cur.copy_from(f, 'accounts', sep=',')
    conn.commit()
    cur.execute("SELECT * FROM accounts;")
    print(f"accounts: {cur.fetchall()}")

    # products
    with open("data/products.csv") as f:
        next(f)
        cur.copy_from(f, 'products', sep=',')
    conn.commit()
    cur.execute("SELECT * FROM products;")
    print(f"products: {cur.fetchall()}")

        # transactions
    with open("data/transactions.csv") as f:
        next(f)
        cur.copy_from(f, 'transactions', sep=',')
    conn.commit()
    cur.execute("SELECT * FROM transactions;")
    print(f"transactions: {cur.fetchall()}")


    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
