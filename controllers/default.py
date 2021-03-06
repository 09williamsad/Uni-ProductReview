# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
def index():
    category = request.args(0)
    product_name_default = request.vars.product_name
    #Search form
    form = SQLFORM.factory(
                 Field("product_name", default=product_name_default),
                 formstyle='divs',
                 submit_button="Search",
                 )
    search_query = db.product.id == "0"
    if form.process().accepted:
        product_name = form.vars.product_name
        search_query = db.product.product_name.like("%%%s%%" % product_name)
    #Count number of results.
    count = db(search_query).count()
    #Get results of user inputted value.
    search_results = db(search_query).select(orderby=db.product.product_name)
    #Message of the result count.
    msg = T("%s result/s" % count )
    #Random products and reviews
    random_results = db((db.product.id == db.review.product_id) & (db.auth_user.id == db.review.user_id)).select(limitby=(0, 3), orderby='<random>')
    #Return statement
    return dict(form=form, msg=msg, search_results=search_results, random_results=random_results)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

def call():
    return service()

def product():
    #Get and store args link value.
    product_link = request.args(0)
    #Get review data for product.
    product_reviews = db((db.auth_user.id == db.review.user_id) & db.review.product_id.like(product_link)).select()
    #Get product data.
    product_query = db(db.product.id.like(product_link)).select()
    #Get the average of the review scores.
    review_rating_sum = db(db.review.product_id.like(product_link)).select((db.review.review_rating).sum())
    #Convert sum of scores from an _extra row to a number.
    for row in review_rating_sum:
        sum_number = row._extra['SUM(review.review_rating)']
    #Check if the sum is null/none, needed as for the average it cannot divide none by a number.
    if sum_number != None:
        #Get number of reviews for product.
        review_count = db(db.review.product_id.like(product_link)).count()
        #Calculate average, both numbers are integers so one has to be converted to a float to prevent rounding to whole number.
        review_score_average = (float(sum_number)/review_count)
    else: review_score_average = 0
    #Review form
    if auth.is_logged_in() & db((db.review.product_id == product_link) & (db.review.user_id == auth.user_id)).count() == 0:
        review_form = SQLFORM(db.review)
        if review_form.process(session=None, formname='review_form').accepted:
            redirect(URL('my_reviews'), client_side=True)
        elif review_form.errors:
            response.flash = review_form.errors
        else:
            response.flash = 'Please enter something into all fields if you want to make a review.'
    #Return data
    return dict(product_query=product_query, product_reviews=product_reviews, review_score_average=review_score_average, product_link=product_link)

def my_reviews():
    #Check if logged in.
    if auth.is_logged_in():
        #Get users reviews.
        my_reviews = db((db.product.id == db.review.product_id) & db.review.user_id.like(auth.user_id)).select()
        #For reasons unknown the query for getting reviews does not become None when there are no reviews despite having no data.
        #Due to this the below if is used to determine if there are no results and if false then the view displays the appropiate message.
        if my_reviews:
            return dict(my_reviews=my_reviews)
        else:
            return dict(my_reviews=False)
    else:
        return dict()

def delete():
    #Get value from args link, value is a review ID which is used to delete the review.
    record = request.args(0)
    del db.review[record]
    redirect(URL('my_reviews'), client_side=True)

def add_product():
    #Is user logged in.
    if auth.is_logged_in():
        #Is user an admin.
        if db((auth.user.id == db.site_admin.user_id)).count():
            #Declare SQLFORM and the table connected to it.
            add_product_form = SQLFORM(db.product)
            if add_product_form.process(session=None, formname='add_product_form').accepted:
                response.flash = 'Product added, see new product on the search page.'
            elif add_product_form.errors:
                response.flash = add_product_form.errors
            else:
                response.flash = 'Please enter something into all fields if you want to add a product, all fields must have a value.'
    return dict()

def edit_product():
    #Get and store args value for the table to use.
    edit_record = db.product(request.args(0))
    #Check if user logged in.
    if auth.is_logged_in():
        #Check if user is an admin.
        if db((auth.user.id == db.site_admin.user_id)).count():
            #Get product date where the ID is the same as args value.
            product_query = db(db.product.id.like(request.args(0))).select()
            #Make SQLFORM as an edit form using edit_record.
            edit_product_form = SQLFORM(db.product, edit_record)
            if edit_product_form.process(session=None, formname='edit_product_form').accepted:
                response.flash = 'Product edited, please go to the products page to see changes.'
            elif edit_product_form.errors:
                response.flash = edit_product_form.errors
            else:
                response.flash = 'Please modify fields then submit if you want to edit a product, all fields must have a value.'
    return dict(product_query=product_query)

def delete_product():
    #Delete the product that has the same ID as the args value.
    record = request.args(0)
    del db.product[record]
    redirect(URL('index'), client_side=True)

def edit_review():
    #Get and store args value for the table to use.
    edit_review = db.review(request.args(0))
    #Check if logged in.
    if auth.is_logged_in():
        #Get data for review and product where the product id in the review is the same as the args value.
        product_review_data = db((db.product.id == db.review.product_id) & db.review.id.like(request.args(0))).select()
        #Cannot use a Row data type in if check, converted.
        for row in product_review_data:
            #Check if current user is the same as the one who made the review.
            if auth.user.id == row.review.user_id:
                #Declare and make edit SQLFORM.
                edit_review_form = SQLFORM(db.review, edit_review)
                if edit_review_form.process(session=None, formname='edit_review_form').accepted:
                    redirect(URL('my_reviews'), client_side=True)
                    response.flash = 'Review edited, please refresh or go my reviews to see changes.'
                elif edit_review_form.errors:
                    response.flash = edit_review_form.errors
                else:
                    response.flash = 'Please modify fields then submit, all fields must have a value.'
        return dict(product_review_data=product_review_data)

def admin_management():
    #Check if logged in.
    if auth.is_logged_in():
        #Check if user is a super admin.
        if db((auth.user.id == db.site_admin.user_id) & db.site_admin.admin_type.like('superadmin')).count():
            regular_users = db(~db.auth_user.id.belongs(db()._select(db.site_admin.user_id))).select(db.auth_user.ALL)
            admin_users = db((db.auth_user.id == db.site_admin.user_id) & db.site_admin.admin_type.like('admin')).select()
            return dict(regular_users=regular_users, admin_users=admin_users)
        else:
            return dict()

def promote_user():
    promote_id = request.args(0)
    db.site_admin.insert(user_id=promote_id, admin_type = "admin")
    redirect(URL('admin_management'), client_side=True)

def demote_admin():
    demote_id = request.args(0)
    del db.site_admin[demote_id]
    redirect(URL('admin_management'), client_side=True)
