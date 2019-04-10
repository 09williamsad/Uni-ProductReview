# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
# ----------------------------------------------------------------------------------------------------------------------
# Customize your APP title, subtitle and menus here
# ----------------------------------------------------------------------------------------------------------------------
response.title = request.application.replace('_', ' ').title()
response.subtitle = ''
# ----------------------------------------------------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# ----------------------------------------------------------------------------------------------------------------------
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')
# ----------------------------------------------------------------------------------------------------------------------
# your http://google.com/analytics id, Do not know if this is needed for cloud stuff
# ----------------------------------------------------------------------------------------------------------------------
response.google_analytics_id = None
# ----------------------------------------------------------------------------------------------------------------------
# Adam does not know what these do or are for but web2py breaks if they are removed or have the wrong indentation.
# ----------------------------------------------------------------------------------------------------------------------
DEVELOPMENT_MENU = True
def _():

    if DEVELOPMENT_MENU:
        _()

if "auth" in locals():
    auth.wikimenu()
    # ------------------------------------------------------------------------------------------------------------------
    # Drop down menu, navigation bar
    # ------------------------------------------------------------------------------------------------------------------
    response.menu += [(T('Search'), False, URL('default', 'index'), [])]
    #If user is logged in show my reviews link on menu bar.
    if auth.is_logged_in():
        response.menu += [('My reviews',  False,  URL('default', 'my_reviews')) ]
        #If user is an admin or super admin show the add product link on menu bar.
        if db((auth.user.id == db.site_admin.user_id)).count():
            response.menu += [(T('Add a product'),  False,  URL('default', 'add_product')) ]
        #If user is a super admin show permission management link on menu bar.
        if db((auth.user.id == db.site_admin.user_id) & db.site_admin.admin_type.like('superadmin')).count():
            response.menu += [(T('User management'),  False,  URL('default', 'admin_management')) ]
