from flask import Flask, render_template, request, redirect, url_for
import todo_app.data.session_items as session
#from todo_app.flask_config import Config
import requests
def create_app():
    app = Flask(__name__)
    #app.config.from_object(Config)
    # All the routes and setup code etc

    @app.route('/')
    def index():             
        items = session.get_items()
        item_view_model = session.ViewModel(items)
        return render_template('index.html',view_model=item_view_model)
                   

    @app.route('/', methods=['POST'])
    def add_item():   
        title = request.form.get('title') 
        if title!='':
            session.add_item(title)
        return redirect('/')
        
    @app.route('/<id>')
    def complete_item(id):   
        if(id!="favicon.ico"):
            item=session.get_item(id)
            item['status'] = "Completed"
            session.save_item(item)    
        return redirect('/')  

    @app.route('/todo/<id>')
    def uncomplete_item(id):   
        if(id!="favicon.ico"):
            item=session.get_item(id)
            item['status'] = "Not Started"
            session.save_item(item)    
        return redirect('/') 
    
    @app.route('/doing/<id>')
    def start_item(id):   
        if(id!="favicon.ico"):
            item=session.get_item(id)
            item['status'] = "Doing"
            session.save_item(item)    
        return redirect('/') 
    

    @app.route('/remove/<id>')
    def delete_item(id):   
        session.remove_item(id)           
        return redirect('/')    


    return app

if __name__ == '__main__':
    create_app().run()



