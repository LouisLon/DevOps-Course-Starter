from flask import Flask, render_template, request, redirect, url_for
import todo_app.data.session_items as session
#from todo_app.flask_config import Config
import requests
import os
from flask_login import LoginManager,login_required, login_user,logout_user,current_user
from oauthlib.oauth2 import WebApplicationClient
import json
from todo_app.data.user import User,ROLES,requires_roles
from flask import session as appsession


def create_app():
    app = Flask(__name__)      
    CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", None)
    CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", None)
    SECRET_KEY = os.environ.get("SECRET_KEY", None)
    WRITER_ROLE = os.environ.get("ROLEWRITER_USER", None)  
    app.secret_key = SECRET_KEY   
    client = WebApplicationClient(CLIENT_ID)
    login_manager = LoginManager()
    login_manager.init_app(app)
          
    @login_manager.unauthorized_handler
    def unauthenticated():        
        identity_url=client.prepare_request_uri('https://github.com/login/oauth/authorize')      
        return redirect(identity_url)

    @app.route("/login/callback")
    def callback():    
        code = request.args.get("code")           
        token_url, headers, body = client.prepare_token_request(
            "https://github.com/login/oauth/access_token",
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code,
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(CLIENT_ID, CLIENT_SECRET),
        )

        # Parse the tokens!
        params=client.parse_request_body_response(token_response.text)
        uri, headers, body = client.add_token("https://api.github.com/user")
        
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        users_name = userinfo_response.json()["login"]
        users_id = userinfo_response.json()["id"]        
        email = userinfo_response.json()["email"]             
        user = User(users_id,users_name,email,ROLES['reader'])
        appsession['users_id'] = users_id
        appsession['users_name'] = users_name   
        appsession['email'] = email
        if users_name == WRITER_ROLE:
            user.access=ROLES['writer']
        else:
            user.access=ROLES['reader']

        appsession['roles'] = user.access    
        login_user(user)
        return redirect(url_for('index'))

     

    @login_manager.user_loader
    def load_user(user_id):         
        m_user_id = appsession.get('users_id')
        m_users_name = appsession.get('users_name') 
        m_users_roles = appsession.get('roles')  
        m_email = appsession.get('email')      
        user = User(m_user_id,m_users_name,m_email,m_users_roles)         
        return user

   
    
    @app.route('/')
    @login_required
    @requires_roles('reader','writer')
    def index():             
        items = session.Boards().get_items()
        item_view_model = session.ViewModel(items)  
        if current_user.is_anonymous:
            mcurrent_user=''  
            misWriter=True #for E2E testing
        else:
            mcurrent_user=current_user.username  
            misWriter=(appsession.get('roles')==ROLES['writer'])     
        return render_template('index.html',view_model=item_view_model,isWriter=misWriter,currentuser=mcurrent_user)
                   

    @app.route('/', methods=['POST'])
    @login_required
    @requires_roles('writer')
    def add_item():   
        title = request.form.get('title') 
        if title!='':
            session.Boards().add_item(title)
        return redirect('/')
        
    @app.route('/<id>')
    @login_required
    @requires_roles('writer')
    def complete_item(id):   
        if(id!="favicon.ico"):
            todo_class=session.Boards()
            item=todo_class.get_item(id)
            item['status'] = "Completed"
            todo_class.save_item(item)    
        return redirect('/')  

    @app.route('/todo/<id>')
    @login_required
    @requires_roles('writer')
    def uncomplete_item(id):   
        if(id!="favicon.ico"):
            todo_class=session.Boards()
            item=todo_class.get_item(id)
            item['status'] = "Not Started"
            todo_class.save_item(item)    
        return redirect('/') 
    
    @app.route('/doing/<id>')
    @login_required
    @requires_roles('writer')
    def start_item(id):   
        if(id!="favicon.ico"):
            todo_class=session.Boards()
            item=todo_class.get_item(id)
            item['status'] = "Doing"
            todo_class.save_item(item)    
        return redirect('/') 
    

    @app.route('/remove/<id>')
    @login_required
    @requires_roles('writer')
    def delete_item(id):  
        todo_class=session.Boards() 
        todo_class.remove_item(id)           
        return redirect('/')    


    return app

if __name__ == '__main__':
    create_app().run(debug=True,host='0.0.0.0',port=port)
    



