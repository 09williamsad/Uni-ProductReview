# -*- coding: utf-8 -*-
#import os is used so that images are stored to a specified folder on the server.
import os

db.define_table('product',
                db.Field('product_name', 'string', required=True, notnull=True),
                db.Field('product_type', 'string', required=True, notnull=True),
				db.Field('product_stock', 'integer', required=True, notnull=True),
				db.Field('product_price', 'double', required=True, notnull=True),
                db.Field('product_description', 'text', required=True, notnull=True, requires=IS_NOT_EMPTY()),
				db.Field('product_image', 'upload', notnull=True, uploadfolder=os.path.join(request.folder,'static/images/products'), requires=IS_IMAGE()))
db.product.product_name.requires= IS_NOT_IN_DB(db, db.product.product_name)

db.define_table('site_admin',
                db.Field('user_id', db.auth_user, 'string', required=True, notnull=True),
				db.Field('admin_type', 'string', required=True, notnull=True))
db.site_admin.user_id.requires= IS_NOT_IN_DB(db, db.site_admin.user_id)

db.define_table('review',
                db.Field('review_text', 'text', required=True, notnull=True, requires=IS_NOT_EMPTY()),
				db.Field('review_rating', 'integer', notnull=True, required=True, requires=IS_IN_SET(['0', '1', '2', '3', '4', '5'])),
                db.Field('product_id', db.product, 'integer', required=True, notnull=True),
                db.Field('user_id', db.auth_user, 'integer', required=True, notnull=True))
db.review.product_id.requires=IS_NOT_IN_DB(db(db.review.user_id==request.vars.user_id),'review.product_id')
