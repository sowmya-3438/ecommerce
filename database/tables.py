
from database.connection import DatabaseConnection


def createTables():
    db_config = cursor = None

    try:
        db_config = DatabaseConnection()

        if db_config is None:
            return "Database connection failed"

        cursor = db_config.cursor()

        # 1. Users Table
        users_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            hashpassword VARCHAR(255) NOT NULL,
            role ENUM('admin', 'user') DEFAULT 'user',
            phone VARCHAR(15),
            dateofbirth DATE,
            profilename VARCHAR(255),
            profilepath VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
        )
        """

        # 2. Products Table
        products_table_query = """
        CREATE TABLE IF NOT EXISTS products (
            productid BIGINT AUTO_INCREMENT PRIMARY KEY,
            productname VARCHAR(150) NOT NULL,
            description TEXT,
            quantity INT UNSIGNED DEFAULT 0,
            category VARCHAR(100),
            imgname VARCHAR(255),
            buyprice DECIMAL(15,2) DEFAULT 0,
            saleprice DECIMAL(15,2) DEFAULT 0,
            storedpath VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
        )
        """

        # 3. Cart Table
        cart_table_query = """
        CREATE TABLE IF NOT EXISTS cart (
            cartid BIGINT AUTO_INCREMENT PRIMARY KEY,
            userid BIGINT,
            productid BIGINT,
            quantity INT UNSIGNED DEFAULT 1,
            FOREIGN KEY (userid) REFERENCES users(user_id),
            FOREIGN KEY (productid) REFERENCES products(productid)
        )
        """

        # 4. Orders Table
        orders_table_query = """
        CREATE TABLE IF NOT EXISTS orders (
            order_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT,
            status ENUM('shipped', 'delivered', 'cancelled', 'pending')
                DEFAULT 'pending',
            address VARCHAR(255),
            total DECIMAL(15,2) DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """

        # 5. OrderDetails Table
        orderdetails_table_query = """
        CREATE TABLE IF NOT EXISTS orderdetails (
            order_detail_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            order_id BIGINT,
            product_id BIGINT,
            quantity INT UNSIGNED DEFAULT 1,
            price DECIMAL(15,2) DEFAULT 0.0,
            subtotal DECIMAL(20,2)
                GENERATED ALWAYS AS (quantity * price) STORED,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(productid)
        )
        """

        # 6. Payment Table
        payments_table_query = """
        CREATE TABLE IF NOT EXISTS payment (
            payment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT,
            order_id BIGINT,
            method ENUM('cash', 'upi', 'netbanking'),
            amount DECIMAL(20,2) DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(100) DEFAULT 'pending',
            razorpay_id VARCHAR(100),
            razorpay_order_id VARCHAR(255),
            razorpay_payment_id VARCHAR(255),
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """

        tables = [
            users_table_query,
            products_table_query,
            cart_table_query,
            orders_table_query,
            orderdetails_table_query,
            payments_table_query
        ]

        for table_query in tables:
            cursor.execute(table_query)

        db_config.commit()

        return "Tables Created Successfully"

    except Exception as e:
        if db_config:
            db_config.rollback()

        return f"Something went wrong in database/tables.py: {e}"

    finally:
        if cursor:
            cursor.close()

        if db_config:
            db_config.close()
