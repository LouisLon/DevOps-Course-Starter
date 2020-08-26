from flask import Flask, render_template, request, redirect, url_for
import session_items as session

app = Flask(__name__)
app.config.from_object('flask_config.Config')

@app.route('/')
def index():    
    items = session.get_items()
    return  render_template("index.html",todoitems=items)

if __name__ == '__main__':
    app.run()

@app.route('/', methods=['POST'])
def add_item():   
    title = request.form.get('title') 
    if title!='':
        session.add_item(title)
    return redirect('/')
    
@app.route('/<id>')
def complete_item(id):   
    item=session.get_item(id)
    item['status'] = "Completed"
    session.save_item(item)    
    return redirect('/')  

@app.route('/remove/<id>')
def delete_item(id):   
    session.remove_item(id)           
    return redirect('/')  

@app.route('/clear')
def reinitialize_list():
    session.clear_items()
    return redirect('/')  

   