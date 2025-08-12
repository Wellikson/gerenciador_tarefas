from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "chave-secreta-para-sessao"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tarefas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    # poderia ter senha aqui para autenticação real (não implementado nesse exemplo)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    atividade = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pendente")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship("Usuario", backref=db.backref("tarefas", lazy=True))

# Rota para simular login simples (apenas para identificar usuário na sessão)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form.get("nome")
        if not nome:
            return "Nome obrigatório", 400
        usuario = Usuario.query.filter_by(nome=nome).first()
        if not usuario:
            usuario = Usuario(nome=nome)
            db.session.add(usuario)
            db.session.commit()
        session["usuario_id"] = usuario.id
        session["usuario_nome"] = usuario.nome
        return redirect("/")
    return '''
        <form method="POST">
            Nome: <input type="text" name="nome" required />
            <button type="submit">Entrar</button>
        </form>
    '''

# Rota logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Página principal com tarefas do usuário logado
@app.route("/")
def index():
    if "usuario_id" not in session:
        return redirect("/login")

    usuario_id = session["usuario_id"]

    pendentes = Tarefa.query.filter_by(usuario_id=usuario_id, status="Pendente").all()
    iniciadas = Tarefa.query.filter_by(usuario_id=usuario_id, status="Iniciado").all()
    completas = Tarefa.query.filter_by(usuario_id=usuario_id, status="Completo").all()

    return render_template(
        "index.html",
        usuario_nome=session["usuario_nome"],
        pendentes=pendentes,
        iniciadas=iniciadas,
        completas=completas,
    )

@app.route("/add", methods=["POST"])
def add():
    if "usuario_id" not in session:
        return redirect("/login")

    nome = request.form.get("atividade")
    status = request.form.get("status")
    if nome:
        tarefa = Tarefa(atividade=nome, status=status, usuario_id=session["usuario_id"])
        db.session.add(tarefa)
        db.session.commit()
    return redirect("/")

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if "usuario_id" not in session:
        return redirect("/login")

    tarefa = Tarefa.query.get_or_404(id)
    if tarefa.usuario_id != session["usuario_id"]:
        return "Não autorizado", 403

    novo_status = request.form.get("status")
    tarefa.status = novo_status
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    if "usuario_id" not in session:
        return redirect("/login")

    tarefa = Tarefa.query.get_or_404(id)
    if tarefa.usuario_id != session["usuario_id"]:
        return "Não autorizado", 403

    db.session.delete(tarefa)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
