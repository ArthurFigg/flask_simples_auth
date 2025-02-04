from models.user import User
from database import db
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, UserMixin, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = "dragon-ball-z"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Modelo de Usuário corrigido (com UserMixin)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Corrigindo o decorador do user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Converte user_id para inteiro

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()  # Buscar usuário no banco

        if user and user.password == password:  # Comparação direta (idealmente, use hashing)
            login_user(user)  # Faz login do usuário
            print(current_user.is_authenticated)  # Verifica se o usuário está autenticado
            return jsonify({"message": "Credenciais válidas, login realizado com sucesso!"}), 200

    return jsonify({"message": "Credenciais inválidas"}), 401

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"}), 200   
       


@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "usuário criado com sucesso"})

    return jsonify({"message": "dados invalidso"}), 401
    


@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)

    if user:
        return{"username": user.username}
    
    return jsonify({"message": "usuário não encontrado"}), 404
       

@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit()
        
        return jsonify({"message": f"usuário {id_user} atualizado com sucesso"})
    
    return jsonify({"message": "usuário não encontrado"}), 404


@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if id_user == current_user.id:
        return jsonify({"message": "não é possível deletar o próprio usuário"}), 403
    
    if user: 
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"usuário {id_user} deletado com sucesso"})
    
    return jsonify({"message": "usuário não encontrado"}), 404

@app.route("/hello-world", methods=["GET"])
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Cria o banco se ainda não existir
    app.run(debug=True)
