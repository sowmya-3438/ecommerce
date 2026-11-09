from flask import Flask, redirect, render_template, url_for, session, request, flash
from database import createTables, AuthQueries, AdminQueries,UserQueries
import bcrypt
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = "Swathi@1234"

# create images folder if not exists
if not os.path.exists('static/images'):
    os.mkdir('static/images')

# create static/images/products
if not os.path.exists('static/images/products'):
    os.mkdir('static/images/products')

#======================================
#       Authentication Routes
#======================================
# home route
@app.route('/')
def home():
    return render_template('home.html')
   
# register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # check password and confirm_password both same or not
        if password != confirm_password:
            flash('Password missmatch', 'err')
            return redirect(url_for('register'))

        # check email exist or not
        status, user = AuthQueries.getUserData(email=email)
        if status:
            flash("Email Already Exists", 'err')
            return redirect(url_for('register'))
        
        # generate hashpassword
        hash_password = bcrypt.hashpw(password=password.encode('utf-8'),
                                      salt=bcrypt.gensalt(4))
        
        # insert user data into users table
        status, msg = AuthQueries.createUserAccount(name=name,
                                                    email=email,
                                                    password=hash_password,
                                                    phone=phone)
        if not status:
            flash(msg, 'err')
            return redirect(url_for('register'))
        flash(msg, 'msg')
        return redirect(url_for('login'))


# login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # check email exists or not
        status, user = AuthQueries.getUserData(email=email)
        if not status:
            flash(user, 'err')
            return redirect(url_for('login'))
                
        # verify hashpassword
        verify_password_status = bcrypt.checkpw(password=password.encode('utf-8'),
                                                hashed_password=user['hashpassword'].encode('utf-8'))
    
        if not verify_password_status:
            flash('Password incorrect', 'err')
            return redirect(url_for('login'))
        # store user data in session
        
        session['username'] = user['username']
        session['role'] = user['role']
        session['id'] = user['user_id']
        session['email'] = user['email']
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('products'))


#========================================================
#                   User Routes
#========================================================
@app.route('/products')
def products():
    _, products = AdminQueries.getAllProducts()
    _, categories = AdminQueries.getAllCategories()
    return render_template('user/products.html', products=products, categories=categories)


@app.route('/products/<int:product_id>/details')
def product_details(product_id):
    _, product = AdminQueries.getAllProducts(product_id=product_id)
    return render_template('user/product_details.html', product=product)



# VIEW CART
@app.route('/cart')
def cart():
    _, items = UserQueries.getCartItems(userid=session['id'])
    
    # Wrap item['subtotal'] in float() to prevent Decimal/float type mismatch
    sub_total = sum([float(item['subtotal']) for item in items])
    
    total_items = sum(int(item.get('quantity', 0)) for item in items)
    
    shipping = sub_total * 0.01  # This will now work because sub_total is a float

    return render_template(
        'user/cart.html', 
        cart_items=items, 
        total_items=total_items,
        subtotal=sub_total,
        shipping=shipping,
        total=sub_total + shipping
    )
# ADD TO CART
@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):

    if 'id' not in session:
        return redirect(url_for('login'))

    quantity = int(request.form.get('quantity', 1))

    if quantity < 1:
        flash('Please select a valid quantity.', 'err')
        return redirect(url_for('products'))

    status, msg = UserQueries.addCartitem(
        product_id=product_id,
        userid=session['id'],
        quantity=quantity
    )

    flash(msg, 'msg' if status else 'err')

    return redirect(url_for('cart'))


# UPDATE CART QUANTITY
@app.route('/cart/<int:cartid>/update', methods=['POST'])
def update_cart_quantity(cartid):

    

    quantity = request.form.get('quantity', type=int)

    
    status, msg = UserQueries.updateCartQuantity(
        cartid=cartid,
        
        quantity=quantity
    )

    flash(msg, 'msg' if status else 'err')

    return redirect('/cart')


# REMOVE FROM CART
@app.route('/cart/<int:cartid>/remove', methods=['POST'])
def remove_from_cart(cartid):

    if 'id' not in session:
        return redirect(url_for('login'))

    status, msg = UserQueries.deleteCartItem(
        cartid=cartid,
       
    )

    flash(msg, 'msg' if status else 'err')

    return redirect(url_for('cart'))
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
        _, items = UserQueries.getCartItems(userid=session['id'])
        sub_total = sum([float(item['subtotal']) for item in items])
        
        total_items = sum(int(item.get('quantity', 0)) for item in items)
        
        shipping = sub_total * 0.01  # This will now work because sub_total is a float
    
        return render_template(
            'user/checkout.html', 
            cart_items=items, 
            total_items=total_items,
            subtotal=sub_total,
            shipping=shipping,
            total=sub_total + shipping
        )

    
#========================================================
#                   Admin Routes
#========================================================
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')


@app.route('/admin/products')
def admin_products():
    category = request.args.get('category')
    product_name = request.args.get('search')
    page = int(request.args.get('page', 1))
    per_page = 7

    status, products = AdminQueries.getAllProducts(
        product_name=product_name,
        category=category,
        page_no=page,
        per_page=per_page
    )

    if not status:
        print("Database Error:", products)
        products = []

    total = len(products)
    total_pages = (total + per_page - 1) // per_page

    cat_status, categories = AdminQueries.getAllCategories()

    if cat_status:
        print("Category records:", categories)

    if categories:
        print("First category:", categories[0])
        print("Available keys:", categories[0].keys())
    else:
        categories = []

    return render_template(
        'admin/products.html',
        products=products,
        categories=categories,
        total_pages=total_pages,
        page=page,
        total=total,
        per_page=per_page,
    )


@app.route('/admin/products/<int:product_id>/edit-product',
           methods=['GET', 'POST'])
def admin_edit_product(product_id):

    # ================= GET METHOD =================
    if request.method == 'GET':

        # Get existing product details
        status, product = AdminQueries.getAllProducts(
            product_id=product_id
        )

        if not status or not product:
            flash("Product not found", 'err')
            return redirect(url_for('admin_products'))

        # Get all categories
        category_status, categories = AdminQueries.getAllCategories()

        if not category_status:
            flash("Unable to fetch categories", 'err')
            return redirect(url_for('admin_products'))

        return render_template(
            'admin/edit_product.html',
            product=product,
            categories=categories
        )

    # ================= POST METHOD =================
    if request.method == 'POST':

        # Get form data
        product_name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        stock = request.form.get('stock')
        description = request.form.get('description')

        # Get existing product details
        status, product = AdminQueries.getAllProducts(
            product_id=product_id
        )

        if not status or not product:
            flash("Product not found", 'err')
            return redirect(url_for('admin_products'))

        # Keep existing image details
        img_name = product['imgname']
        img_path = product['storedpath']

        # Get uploaded image
        image = request.files.get('image')

        # Check new image uploaded or not
        if image and image.filename:

            secure_img_name = secure_filename(image.filename)

            unique_img_name = str(uuid.uuid4()) + "_" + secure_img_name

            img_path = os.path.join(
                'static',
                'images',
                'products',
                unique_img_name
            )

            image.save(img_path)

            img_name = unique_img_name

        # Prepare product data
        product_data = (
            product_name,
            description,
            category,
            price,
            stock,
            img_name,
            img_path
        )

        # Update product in database
        status, msg = AdminQueries.updateProductRecord(
            product_id=product_id,
            product_data=product_data
        )

        if status:
            flash("Product Updated Successfully", 'msg')
        else:
            flash(msg, 'err')

        return redirect(url_for('admin_products'))
@app.route('/admin/products/<int:product_id>/deactivate')
def admin_deactivate_product(product_id):
    pass


@app.route('/admin/products/add-products', methods=['GET', 'POST'])
def admin_add_product():
    if request.method == 'GET':
        _, categories = AdminQueries.getAllCategories()
        return render_template('admin/add_product.html', categories=categories)

    if request.method == 'POST':
        product_name = request.form.get('name')
        category = request.form.get('category')
        new_category = request.form.get('new_category')
    
        price = request.form.get('price')
        stock = request.form.get('stock')
        description = request.form.get('description')
        image = request.files.get('image')

        img_name = image.filename
        secure_img_name = secure_filename(img_name)
        unique_img_name = str(uuid.uuid1()) + "_" + secure_img_name

        img_path = os.path.join('static', 'images', 'products', unique_img_name)
        image.save(img_path)
        data = (product_name, description, category, price, stock, unique_img_name, img_path)
        status, msg = AdminQueries.insertProductRecord(product_data=data)
        flash(msg, 'msg' if status else 'err')
        return redirect(url_for('admin_products'))



@app.route('/admin/categories', endpoint='admin_categories')
def admin_categories():
    pass

@app.route('/admin/categories/add', methods=['GET', 'POST'], endpoint='admin_add_category')
def admin_add_category():
    flash("Category management functionality is under development.", "msg")
    return redirect(url_for('admin_categories'))


@app.route('/admin/categories/<int:category_id>/edit', methods=['GET', 'POST'], endpoint='admin_edit_category')
def admin_edit_category(category_id):
    flash("Category management functionality is under development.", "msg")
    return redirect(url_for('admin_categories'))


@app.route('/admin/categories/<int:category_id>/delete', methods=['POST'], endpoint='admin_delete_category')
def admin_delete_category(category_id):
    flash("Category management functionality is under development.", "msg")
    return redirect(url_for('admin_categories'))


@app.route('/admin/orders')
def admin_orders():
    total_pages = 4
    return render_template('admin/orders.html',
                           total_pages=total_pages,
                           page=1,
                           total=10,
                           per_page=7)


@app.route('/admin/orders/<int:order_id>')
def admin_order_details(order_id):
    flash("Order details feature is under development.", "msg")
    return redirect(url_for('admin_orders'))


@app.route('/admin/users')
def admin_users():
    _, users = AdminQueries.getAllUsers()
    return render_template('admin/users.html', users=users)


# user details
@app.route('/admin/users/<int:user_id>/details')
def admin_user_details(user_id):
    pass


@app.route('/admin/users/<int:user_id>/edit')
def admin_edit_user(user_id):
    pass


# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", 'msg')
    return redirect(url_for('login'))


# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)
