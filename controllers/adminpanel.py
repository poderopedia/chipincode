# -*- coding: utf-8 -*-
#@auth.requires_membership('admin')
def index():
    return locals()

def list_all_projects():
    query = db.project
    maxtextlength = {
                'project.project_name':50,
                'project.project_total_collected':10,
                'project.id_auth_user':50,
                'project.status_text':50
    }

    headers = {
                'project.project_name':T('Name'),
                'project.project_total_collected':T('Total Collected'),
                'project.id_auth_user':T('Owner'),
                'project.status_text':T('Project Status')
    }
    fields = [
                db.project.id,
                db.project.project_name,
                db.project.project_total_collected,
                db.project.id_auth_user,
                db.project.status_text
        ]
    grid = SQLFORM.grid(
        query=query, 
        headers=headers, 
        fields=fields,
        _class='table table-striped',
        deletable=False,
        editable=False,
        create=False,
        maxtextlength = maxtextlength
    )
    return locals()

def list_actives_projects():
    query = db.project.status == True
    maxtextlength = {
                'project.project_name':50,
                'project.project_total_collected':10,
                'project.id_auth_user':50,
                'project.status_text':50
    }

    headers = {
                'project.project_name':T('Name'),
                'project.project_total_collected':T('Total Collected'),
                'project.id_auth_user':T('Owner'),
                'project.status_text':T('Project Status')
    }
    fields = [
                db.project.id,
                db.project.project_name,
                db.project.project_value,
                db.project.project_total_collected,
                db.project.id_auth_user,
                db.project.status_text
        ]
    grid = SQLFORM.grid(
        query=query, 
        headers=headers, 
        fields=fields,
        _class='table table-striped',
        deletable=False,
        editable=False,
        create=False,
        maxtextlength = maxtextlength
    )
    return locals()


def list_pending_projects():
    query = ((db.project.status == False)&(db.project.finalized == False))
    extra_links = [
        lambda row:A(T('Authorize'),_class="btn btn-success",_href=URL("adminpanel","authorize_project",user_signature=True,args=[row.id]))
    ] 
    maxtextlength = {
                'project.project_name':50,
                'project.status_text':50
    }

    headers = {
                'project.project_name':T('Name'),
                'project.id_auth_user':T('Owner'),
                'project.status_text':T('Project Status'),
                'project.project_value':T('Value Required')
    }
    fields = [
                db.project.id,
                db.project.project_name,
                db.project.id_auth_user,
                db.project.status_text,
                db.project.project_value
        ]
    grid = SQLFORM.grid(
        searchable=False,
        links=extra_links,
        query=query, 
        headers=headers, 
        fields=fields,
        _class='table table-striped',
        deletable=False,
        editable=False,
        create=False,
        maxtextlength = maxtextlength
    )
    return locals()

def authorize_project():
    id_project = request.args(0) or redirect(URL('adminpanel', 'index'))

    project_data = db(db.project.id == id_project).select()
    for item in project_data:
        project_name = item.project_name
    start_date = date.today()
    end_date = date.today() + timedelta(days=int(funding_time))
    db(db.project.id == id_project).update(
            start_date = start_date,
            end_date = end_date,
            status = True,
            status_text = "Raising Funding"
            )
    session.flash="Project Authorized With Successful."
    redirect(URL('adminpanel', 'list_pending_projects'))

    pass

def list_expired_projects():
    query = ((db.project.end_date < date.today())&(db.project.finalized == False))
    extra_links = [
        lambda row:A(T('Finish Successfully'),_class="btn btn-success",_href=URL("adminpanel","finish_successfully",user_signature=True,args=[row.id])),
        lambda row:A(T('Finish Unsuccessfully'),_class="btn btn-danger",_href=URL("adminpanel","finish_unsuccessfully",user_signature=True,args=[row.id]))
    ] 
    maxtextlength = {
                'project.project_name':50,
                'project.project_total_collected':10,
    }

    headers = {
                'project.project_name':T('Name'),
                'project.project_total_collected':T('Total Collected'),
    }
    fields = [
                db.project.project_name,
                db.project.project_value,
                db.project.project_total_collected,
                db.project.end_date
        ]
    grid = SQLFORM.grid(
        links = extra_links,
        searchable=False,
        query=query, 
        headers=headers, 
        fields=fields,
        _class='table table-striped',
        deletable=False,
        editable=False,
        create=False,
        maxtextlength = maxtextlength
    )
    return locals()

def finish_successfully():
    if request.post_vars:
        project_data = db(db.project.id == request.post_vars.project_id).select()
        for item in project_data:
            total_project = item.project_value or 0.0
            total_collected = item.project_total_collected or 0.0
            user_data = db['auth_user'][item.id_auth_user]
            body_email = """<html>Seu projeto <b>"""+item.project_name+"""</b>, alcançou a meta desejada. <br>
            <b>Total Pretendido</b>:"""+str(('%.2f' % total_project))+"""<br> 
            <b>Total Arrecadado</b>:"""+str(('%.2f' % total_collected))+"""<br>
            Logo nossa equipe entrará em contato com você.</html>"""
            mail.send(user_data.email, 'Seu Projeto foi finalizado.', body_email)

        db(db.project.id == request.post_vars.project_id).update(
            status = False,
            status_text = T("Finalized"),
            finalized = True,
            goal = True
            )
        session.flash="Project Finalized With Successful."
        redirect(URL('adminpanel', 'list_expired_projects'))
    return locals()

def finish_unsuccessfully():
    if request.post_vars:
        project_data = db(db.project.id == request.post_vars.project_id).select()
        for item in project_data:
            total_project = item.project_value or 0.0
            total_collected = item.project_total_collected or 0.0
            user_data = db['auth_user'][item.id_auth_user]
            body_email = """<html>Seu projeto <b>"""+item.project_name+"""</b>, não alcançou a meta. <br>
            Ele foi finalizado e o valor arrecadado foi devolvido para os doadores.<br>
            <b>Total Pretendido</b>:"""+str(('%.2f' % total_project))+"""<br> 
            <b>Total Arrecadado</b>:"""+str(('%.2f' % total_collected))+"""<br></html>"""
            mail.send(user_data.email, 'Seu Projeto foi finalizado.', body_email)

        db(db.project.id == request.post_vars.project_id).update(
            status = False,
            status_text = T("Finalized"),
            finalized = True
            )

        donation_data = db((db.project_donation.id_project == request.post_vars.project_id)&(db.project_donation.status == True)).select()
        for donation in donation_data:
            project_name = db['project'][donation.id_project]
            user_data = db['auth_user'][donation.id_auth_user]
            
            body_message = """O projeto <b>"""+project_name.project_name+"""</b>, para o qual você fez uma doação
            não alcançou a meta. <br>
            Ele foi finalizado, e o valor de """+str(('%.2f' % donation.donation_value))+""" 
            foi creditado em sua conta.<br>"""
            title = "Você recebeu um crédito"
            db.user_messages.insert(message_title=title, message_content=body_message, id_auth_user=user_data.id, message_read=False)     

            status = "Estornada"
            db(db.project_donation.id == donation.id).update(status_text = status)

            get_user_credit = db(db.user_credit.id_auth_user == donation.id_auth_user).select()
            for credit in get_user_credit:
                user_credit = credit.credit_value             
            if not  get_user_credit:
                db.user_credit.insert(id_auth_user= user_data.id, credit_value=donation.donation_value)
            else:
                total_user_credit = user_credit
                new_credit = total_user_credit + donation.donation_value
                db(db.user_credit.id_auth_user == user_data.id).update(credit_value=new_credit)
        session.flash="Project Finalized With Successful."
        redirect(URL('adminpanel', 'list_expired_projects'))
       
    return locals()

def config_website_meta():
    crud.settings.formstyle = 'divs'
    crud.messages.submit_button = T('Insert')
    meta_data = db(db.website_meta.id > 0).select()
    for item in meta_data:
        data_id = item.id
    if not meta_data:
        form = crud.create(db.website_meta, next=URL('adminpanel', 'config_website_meta'))
    else:
        form = crud.update(db.website_meta, data_id)
    form.element(_name='site_title')['_class'] = "span6"
    form.element(_name='meta_author')['_class'] = "span6"
    form.element(_name='meta_description')['_class'] = "span6"
    form.element(_name='meta_keywords')['_class'] = "span6"
    return dict(form=form)

def config_website_images():
    crud.settings.formstyle = 'divs'
    logo_data = db(db.logo_image.id > 0).select()
    for item in logo_data:
        logo_id = item.id
    if not logo_data:
        form_logo = crud.create(db.logo_image, next=URL('adminpanel', 'config_website_images'))
    else:
        form_logo = crud.update(db.logo_image, logo_id)

    banner_data = db(db.home_banner.id > 0).select()
    for banner in banner_data:
        banner_id = banner.id
    if not banner_data:
        form_banner = crud.create(db.home_banner, next=URL('adminpanel', 'config_website_images'))
    else:
        form_banner = crud.update(db.home_banner, banner_id)

    default_avatar = db(db.default_avatar.id > 0).select()
    for avatar in default_avatar:
        avatar_id = avatar.id
    if not default_avatar:
        form_avatar = crud.create(db.default_avatar, next=URL('adminpanel', 'config_website_images'))
    else:
        form_avatar = crud.update(db.default_avatar, avatar_id)

    anonymous_avatar = db(db.anonymous_avatar.id > 0).select()
    for anonymous in anonymous_avatar:
        anonymous_id = anonymous.id
    if not anonymous_avatar:
        form_anonymous = crud.create(db.anonymous_avatar, next=URL('adminpanel', 'config_website_images'))
    else:
        form_anonymous = crud.update(db.anonymous_avatar, anonymous_id)


    return dict(form_logo=form_logo, form_banner=form_banner, form_avatar=form_avatar, form_anonymous=form_anonymous)



def request_password():
    """
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """ 
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())