from database.connection import DatabaseConnection
class UserQueries:
    @staticmethod
    def addCartitem(product_id:int, userid:int, quantity:int):
        cursor = db_config = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            #update cart item quantity if item already exists
            query= """update cart set quantity = quantity + %s
                        where productid = %s and userid = %s"""
            cursor.execute(query, (quantity, product_id, userid))
            if cursor.rowcount:
                db_config.commit()
                return True, "Cart item Quantity Updated"

            # insert item to cart
            query ="""insert into cart(userid, productid, quantity) 
                    values (%s, %s, %s)"""
            cursor.execute(query, (userid, product_id, quantity))
            db_config.commit()
            return True, "item added to cart"
        except Exception as e:
            return False,f"Something wrong in database/userDB.UserQueries.addCartitem():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()


    @staticmethod
    def getCartItems(userid: int):

        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """
                SELECT
                    c.cartid,
                    c.productid,
                    c.quantity,
                    p.productname,
                    p.category ,
                    p.saleprice,
                    p.storedpath,
        
                    (c.quantity * p.saleprice) AS subtotal
                FROM cart c
                INNER JOIN products p
                ON c.productid = p.productid
                WHERE c.userid = %s
            """

            cursor.execute(query, (userid,))
            items = cursor.fetchall()

            return True, items

        except Exception as e:
            return False,f"Something wrong in database/userDB.UserQueries.getCartItems():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()




    @staticmethod
    def updateCartQuantity(cartid: int, quantity: int):

        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """
                update cart set quantity = %s where cartid= %d
            """

            cursor.execute(query, (cartid, quantity))
            

           
            db_config.commit()

            return True, "Cart quantity updated successfully"

        except Exception as e:
            return False,f"Something wrong in database/userDB.UserQueries.updateCartQuantity():{e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()


    @staticmethod
    def deleteCartItem(cartid: int):

        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                DELETE FROM cart
                WHERE cartid = %s 
            """

            cursor.execute(query, (cartid,))

           
            db_config.commit()

            return True, "item deleted"

        except Exception as e:
            return False,f"Something wrong in database/userDB.UserQueries.deleteCartItem():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()


                


