from flask import Flask, render_template, request, redirect

app = Flask(__name__)

tarefas = []

@app.route("/")
def index():
    return render_template("index.html", tarefas=list(enumerate(tarefas)))

@app.route("/add", methods=["POST"])
def add():
    nome = request.form.get("atividade")
    status = request.form.get("status")
    if nome:
        tarefas.append({"atividade": nome, "status": status})
    return redirect("/")

@app.route("/update/<int:index>", methods=["POST"])
def update(index):
    novo_status = request.form.get("status")
    if 0 <= index < len(tarefas):
        tarefas[index]["status"] = novo_status
    return redirect("/")

@app.route("/delete/<int:index>")
def delete(index):
    if 0 <= index < len(tarefas):
        tarefas.pop(index)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
