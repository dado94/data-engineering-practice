create table accounts (
    customer_id INTEGER,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    address_1 VARCHAR(50),
    address_2 VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code INTEGER,
    join_date DATE
);
alter table accounts add primary key (customer_id);

create table products (
    product_id INTEGER,
    product_code INTEGER,
    product_description VARCHAR(50)
);
alter table products add primary key (product_id, product_code);

create table transactions (
    transaction_id VARCHAR(50),
    transaction_date DATE,
    product_id INTEGER,
    product_code INTEGER,
    product_description VARCHAR(50), -- probably denormalized
    quantity INTEGER,
    account_id INTEGER
);
alter table transactions add primary key (transaction_id);
alter table transactions add constraint transactions_products_fk 
    foreign key (product_id, product_code) 
    references products(product_id, product_code);
alter table transactions add constraint transactions_accounts_fk 
    foreign key (account_id)
    references accounts(customer_id);
create index transactions_products_ix ON transactions(product_id, product_code);
create index transactions_accounts_ix ON transactions(account_id);

