from functools import wraps
import io
from flask import Flask, Response, render_template, jsonify, request, redirect, url_for, flash, session
import mysql.connector
import hashlib
from Models.trading import Trading
from Models.personnel import Personnel
from Models.academy import Academy
from Models.digital import Digital
from Models.materiel import Materiel
from Models.finance import Finance
from Models.evenementiel import Evenementiel
from Models.projet import Projet
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
application = app

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bd_kounda"
    )
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personnels (
            id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
            nom VARCHAR(20),
            prenom VARCHAR(50),
            username VARCHAR(25) UNIQUE,
            email VARCHAR(50) UNIQUE,
            phone VARCHAR(15),
            departement ENUM ('Direction', 'Trading', 'Academy', 'Digital') DEFAULT 'Trading',
            date_arrivee DATE,
            date_depart DATE,
            ecole VARCHAR(100),
            convention ENUM ('Stage', 'CDD', 'CDI') DEFAULT 'Stage',
            password VARCHAR(255),
            role ENUM ('Administrator', 'Trading', 'Academy', 'Digital') DEFAULT 'Academy',
            observations TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trading (
            id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
            date_const DATE,
            personnel_id INT,
            type_libelle VARCHAR(255),
            nom_client VARCHAR(255),
            prenom_client VARCHAR(255),
            phone_client VARCHAR(255),
            email_client VARCHAR(255),
            items VARCHAR(255),
            quantite INT,
            prix_unit FLOAT,
            montant_ht FLOAT,
            tva FLOAT,
            montant_ttc FLOAT,
            modalite_paiement VARCHAR(255),
            type_paiement ENUM ('Virement bancaire', 'Cheque','Especes', 'Paiement mobile') DEFAULT 'Especes',
            observations TEXT,
            FOREIGN KEY (personnel_id) REFERENCES personnels(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS academy (
            id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
            date_const DATE,
            personnel_id INT,
            type_libelle VARCHAR(255),
            nom_client VARCHAR(255),
            prenom_client VARCHAR(255),
            phone_client VARCHAR(255),
            email_client VARCHAR(255),
            items VARCHAR(255),
            quantite INT,
            prix_unit FLOAT,
            montant_ht FLOAT,
            tva FLOAT,
            montant_ttc FLOAT,
            modalite_paiement VARCHAR(255),
            type_paiement ENUM ('Virement bancaire', 'Cheque','Especes', 'Paiement mobile') DEFAULT 'Especes',
            observations TEXT,
            FOREIGN KEY (personnel_id) REFERENCES personnels(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS digital (
            id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
            date_const DATE,
            personnel_id INT,
            type_libelle VARCHAR(255),
            nom_client VARCHAR(255),
            prenom_client VARCHAR(255),
            phone_client VARCHAR(255),
            email_client VARCHAR(255),
            items VARCHAR(255),
            quantite INT,
            prix_unit FLOAT,
            montant_ht FLOAT,
            tva FLOAT,
            montant_ttc FLOAT,
            modalite_paiement VARCHAR(255),
            type_paiement ENUM ('Virement bancaire', 'Cheque','Especes', 'Paiement mobile') DEFAULT 'Especes',
            observations TEXT,
            FOREIGN KEY (personnel_id) REFERENCES personnels(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materiels (
            id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
            nom_produit VARCHAR(255),
            fournisseur VARCHAR(255),
            date_sortie DATE,
            date_reception DATE,
            quantite INT,
            prix_unit FLOAT,
            montant_ht FLOAT,
            tva FLOAT,
            montant_ttc FLOAT,
            observations TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finances (
            id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
            date DATE,
            libelle TEXT,
            numero_compte VARCHAR(255),
            credit FLOAT,
            debit FLOAT,
            montant_ht FLOAT,
            tva FLOAT,
            montant_ttc FLOAT,
            observations TEXT
        )
    ''')
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nom VARCHAR(255) NOT NULL,
        description TEXT,
        date_debut DATE NOT NULL,
        date_fin DATE,
        budget FLOAT,
        statut ENUM('en attente', 'en cours', 'terminé', 'annulé') NOT NULL DEFAULT 'en attente',
        departement ENUM('Trading', 'Academy', 'Digital') NOT NULL 
    )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evenementiels (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nom VARCHAR(255) NOT NULL,
        description TEXT,
        date_debut DATE NOT NULL,
        date_fin DATE,
        budget FLOAT,
        statut ENUM('en attente', 'en cours', 'terminé', 'annulé') NOT NULL DEFAULT 'en attente',
        departement ENUM('Trading', 'Academy', 'Digital') NOT NULL 
    )
    """)
    cursor.execute("SELECT * FROM personnels WHERE role='Administrator' and username='admin' ")
    existing_admin = cursor.fetchone()
    if not existing_admin:
        password = hash_password("adminSLC123")
        cursor.execute("INSERT INTO personnels (nom, prenom, username, email, phone, departement, date_arrivee, date_depart, ecole, convention, password, role, observations) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", ('Administrateur', 'Administrateur', 'admin', 'sano-logistic@sano-logistic.com', '777777777','Direction', '2025-01-01','2025-01-01', 'SLC', 'CDI', password, 'Administrator', 'Test'))
    conn.commit()
    return conn, cursor

# Login Required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Required decorator
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'role' in session and session['role'] == 'Administrator':
            return f(*args, **kwargs)
        else:
            return render_template('not_access.html')
    return wrapper

# Role-Based Access decorator
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'role' not in session:
                flash('Vous n\'avez pas les permissions pour accéder à cette page.', 'danger')
                return redirect(url_for('login'))

            user_role = session['role']
            if user_role in roles or user_role == 'Administrator':
                return f(*args, **kwargs)
            else:
                return render_template('not_access.html')
        return wrapper
    return decorator

@app.route('/')
@login_required
def index():
    conn, cursor = init_db()
    # Récupérer les statistiques des projets
    cursor.execute("SELECT COUNT(*) FROM projets WHERE statut = 'En cours'")
    projets_en_cours = cursor.fetchone()[0] # type: ignore

    cursor.execute("SELECT COUNT(*) FROM projets WHERE statut = 'Terminé'")
    projets_termines = cursor.fetchone()[0] # type: ignore

    # Récupérer le nombre total d'événements
    cursor.execute("SELECT COUNT(*) FROM evenementiels")
    total_evenements = cursor.fetchone()[0] # type: ignore

    # Récupérer la comptabilité financière (total des crédits et débits)
    cursor.execute("SELECT SUM(credit) AS total_credit, SUM(debit) AS total_debit FROM finances")
    result = cursor.fetchone()
    total_credit, total_debit = result if result else (0, 0)

    # Récupérer la comptabilité des matières (nombre total d'articles)
    cursor.execute("SELECT COUNT(*) FROM materiels")
    total_matieres = cursor.fetchone()[0] # type: ignore
    cursor.close()
    return render_template('index.html', projets_en_cours=projets_en_cours,
        projets_termines=projets_termines,
        total_evenements=total_evenements,
        total_credit=total_credit,
        total_debit=total_debit,
        total_matieres=total_matieres)

# TRADING
@app.route('/trading')
@login_required
@role_required('Trading')
def trading():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM trading t JOIN personnels p ON t.personnel_id = p.id")
    data_trading = cursor.fetchall()
    cursor.execute("SELECT * FROM personnels")
    data_personnels = cursor.fetchall()
    cursor.close()
    return render_template('trading.html', tradings=data_trading, personnels=data_personnels)

@app.route('/trading/insert', methods=['POST'])
@login_required
@role_required('Trading')
def insert_trading():
    if request.method == "POST":
        flash('Dossier créé avec succés!')
        date_const = request.form['date_const']
        personnel_id = request.form['personnel_id']
        type_libelle = request.form['type_libelle']
        nom_client = request.form['nom_client']
        prenom_client = request.form['prenom_client']
        phone_client = request.form['phone_client']
        email_client = request.form['email_client']
        items = request.form['items']
        quantite = float(request.form['quantite'])
        prix_unit = float(request.form['prix_unit'])
        # Calculer Montants HT et TTC côté serveur
        montant_ht = quantite * prix_unit
        taux_tva = 0.18  # TVA à 20 %
        tva = montant_ht * taux_tva
        montant_ttc = montant_ht * (1 + taux_tva)
        modalite_paiement = request.form['modalite_paiement']
        type_paiement = request.form['type_paiement']
        observations = request.form['observations']
        conn, cursor = init_db()
        trading = Trading(None, date_const, personnel_id, type_libelle, nom_client, prenom_client, phone_client, email_client, items, quantite, prix_unit, montant_ht, tva, montant_ttc, modalite_paiement, type_paiement, observations)
        trading.save(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('trading'))

@app.route('/trading/update', methods=['POST', 'GET'])
@login_required
@role_required('Trading')
def update_trading():
    if request.method == "POST":
        flash('Dossier modifié avec succés!')
        id_data = request.form['id']
        date_const = request.form['date_const']
        personnel_id = request.form['personnel_id']
        type_libelle = request.form['type_libelle']
        nom_client = request.form['nom_client']
        prenom_client = request.form['prenom_client']
        phone_client = request.form['phone_client']
        email_client = request.form['email_client']
        items = request.form['items']
        quantite = float(request.form['quantite'])
        prix_unit = float(request.form['prix_unit'])
        # Calculer Montants HT et TTC côté serveur
        montant_ht = quantite * prix_unit
        taux_tva = 0.18  # TVA à 20 %
        tva = montant_ht * taux_tva
        montant_ttc = montant_ht * (1 + taux_tva)
        modalite_paiement = request.form['modalite_paiement']
        type_paiement = request.form['type_paiement']
        observations = request.form['observations']
        conn, cursor = init_db()
        trading = Trading(id_data, date_const, personnel_id, type_libelle, nom_client, prenom_client, phone_client, email_client, items, quantite, prix_unit, montant_ht, tva, montant_ttc, modalite_paiement, type_paiement, observations)
        trading.update(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('trading'))

@app.route('/trading/delete/<string:id_data>', methods = ['POST', 'GET'])
@login_required
@role_required('Trading')
def delete_trading(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM trading WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('trading'))

@app.route('/export-trading')
def export_trading():
    conn, cursor = init_db()
    # Charger les données depuis la base de données dans un DataFrame
    df = pd.read_sql_query("SELECT * FROM trading", conn)
    cursor.close()
    
    # Créer un fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Trading')
    output.seek(0)  # Revenir au début du fichier mémoire

    # Retourner le fichier pour téléchargement
    return Response(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment;filename=trading.xlsx'
        }
    )

# ACADEMY
@app.route('/academy')
@login_required
@role_required('Academy')
def academy():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM academy t JOIN personnels p ON t.personnel_id = p.id")
    data_academy = cursor.fetchall()
    cursor.execute("SELECT * FROM personnels")
    data_personnels = cursor.fetchall()
    cursor.close()
    return render_template('academy.html', academys=data_academy, personnels=data_personnels)

@app.route('/academy/insert', methods=['POST'])
@login_required
@role_required('Academy')
def insert_academy():
    if request.method == "POST":
        flash('Dossier créé avec succés!')
        date_const = request.form['date_const']
        personnel_id = request.form['personnel_id']
        type_libelle = request.form['type_libelle']
        nom_client = request.form['nom_client']
        prenom_client = request.form['prenom_client']
        phone_client = request.form['phone_client']
        email_client = request.form['email_client']
        items = request.form['items']
        quantite = float(request.form['quantite'])
        prix_unit = float(request.form['prix_unit'])
        # Calculer Montants HT et TTC côté serveur
        montant_ht = quantite * prix_unit
        taux_tva = 0.18  # TVA à 18% 
        tva = montant_ht * taux_tva
        montant_ttc = montant_ht * (1 + taux_tva)
        modalite_paiement = request.form['modalite_paiement']
        type_paiement = request.form['type_paiement']
        observations = request.form['observations']
        conn, cursor = init_db()
        academy = Academy(None, date_const, personnel_id, type_libelle, nom_client, prenom_client, phone_client, email_client, items, quantite, prix_unit, montant_ht, tva, montant_ttc, modalite_paiement, type_paiement, observations)
        academy.save(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('academy'))

@app.route('/academy/update', methods=['POST', 'GET'])
@login_required
@role_required('Academy')
def update_academy():
    if request.method == "POST":
        flash('Dossier modifié avec succés!')
        id_data = request.form['id']
        date_const = request.form['date_const']
        personnel_id = request.form['personnel_id']
        type_libelle = request.form['type_libelle']
        nom_client = request.form['nom_client']
        prenom_client = request.form['prenom_client']
        phone_client = request.form['phone_client']
        email_client = request.form['email_client']
        items = request.form['items']
        quantite = float(request.form['quantite'])
        prix_unit = float(request.form['prix_unit'])
        # Calculer Montants HT et TTC côté serveur
        montant_ht = quantite * prix_unit
        taux_tva = 0.18  # TVA à 20 %
        tva = montant_ht * taux_tva
        montant_ttc = montant_ht * (1 + taux_tva)
        modalite_paiement = request.form['modalite_paiement']
        type_paiement = request.form['type_paiement']
        observations = request.form['observations']
        conn, cursor = init_db()
        academy = Academy(id_data, date_const, personnel_id, type_libelle, nom_client, prenom_client, phone_client, email_client, items, quantite, prix_unit, montant_ht, tva, montant_ttc, modalite_paiement, type_paiement, observations)
        academy.update(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('academy'))

@app.route('/academy/delete/<string:id_data>', methods = ['POST', 'GET'])
@login_required
@role_required('Academy')
def delete_academy(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM academy WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('academy'))

@app.route('/export-academy')
def export_academy():
    conn, cursor = init_db()
    # Charger les données depuis la base de données dans un DataFrame
    df = pd.read_sql_query("SELECT * FROM academy", conn)
    cursor.close()
    
    # Créer un fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Academy')
    output.seek(0)  # Revenir au début du fichier mémoire

    # Retourner le fichier pour téléchargement
    return Response(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment;filename=academy.xlsx'
        }
    )

# DIGITAL
@app.route('/digital')
@login_required
@role_required('Digital')
def digital():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM digital t JOIN personnels p ON t.personnel_id = p.id")
    data_digital = cursor.fetchall()
    cursor.execute("SELECT * FROM personnels")
    data_personnels = cursor.fetchall()
    cursor.close()
    return render_template('digital.html', digitals=data_digital, personnels=data_personnels)

@app.route('/digital/insert', methods=['POST'])
@login_required
@role_required('Digital')
def insert_digital():
    if request.method == "POST":
        flash('Dossier créé avec succés!')
        date_const = request.form['date_const']
        personnel_id = request.form['personnel_id']
        type_libelle = request.form['type_libelle']
        nom_client = request.form['nom_client']
        prenom_client = request.form['prenom_client']
        phone_client = request.form['phone_client']
        email_client = request.form['email_client']
        items = request.form['items']
        quantite = float(request.form['quantite'])
        prix_unit = float(request.form['prix_unit'])
        # Calculer Montants HT et TTC côté serveur
        montant_ht = quantite * prix_unit
        taux_tva = 0.18  # TVA à 18% 
        tva = montant_ht * taux_tva
        montant_ttc = montant_ht * (1 + taux_tva)
        modalite_paiement = request.form['modalite_paiement']
        type_paiement = request.form['type_paiement']
        observations = request.form['observations']
        conn, cursor = init_db()
        digital = Digital(None, date_const, personnel_id, type_libelle, nom_client, prenom_client, phone_client, email_client, items, quantite, prix_unit, montant_ht, tva, montant_ttc, modalite_paiement, type_paiement, observations)
        digital.save(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('digital'))

@app.route('/digital/update', methods=['POST', 'GET'])
@login_required
@role_required('Digital')
def update_digital():
    if request.method == "POST":
        flash('Dossier modifié avec succés!')
        id_data = request.form['id']
        date_const = request.form['date_const']
        personnel_id = request.form['personnel_id']
        type_libelle = request.form['type_libelle']
        nom_client = request.form['nom_client']
        prenom_client = request.form['prenom_client']
        phone_client = request.form['phone_client']
        email_client = request.form['email_client']
        items = request.form['items']
        quantite = float(request.form['quantite'])
        prix_unit = float(request.form['prix_unit'])
        # Calculer Montants HT et TTC côté serveur
        montant_ht = quantite * prix_unit
        taux_tva = 0.18  # TVA à 20 %
        tva = montant_ht * taux_tva
        montant_ttc = montant_ht * (1 + taux_tva)
        modalite_paiement = request.form['modalite_paiement']
        type_paiement = request.form['type_paiement']
        observations = request.form['observations']
        conn, cursor = init_db()
        digital = Digital(id_data, date_const, personnel_id, type_libelle, nom_client, prenom_client, phone_client, email_client, items, quantite, prix_unit, montant_ht, tva, montant_ttc, modalite_paiement, type_paiement, observations)
        digital.update(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('digital'))

@app.route('/digital/delete/<string:id_data>', methods = ['POST', 'GET'])
@login_required
@role_required('Digital')
def delete_digital(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM digital WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('digital'))

@app.route('/export-digital')
def export_digital():
    conn, cursor = init_db()
    # Charger les données depuis la base de données dans un DataFrame
    df = pd.read_sql_query("SELECT * FROM digital", conn)
    cursor.close()
    
    # Créer un fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Digital')
    output.seek(0)  # Revenir au début du fichier mémoire

    # Retourner le fichier pour téléchargement
    return Response(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment;filename=digital.xlsx'
        }
    )


# COMPTABILITE MATIERE
@app.route('/comptabilite-matiere')
@login_required
@role_required('Digital')
def comptabilite_matiere():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM materiels")
    data_materiels = cursor.fetchall()
    cursor.close()
    return render_template('comptabilite-matiere.html', materiels=data_materiels)

@app.route('/comptabilite-matiere/insert', methods=['POST'])
@login_required
@role_required('Digital')
def insert_comptabilite_matiere():
    if request.method == "POST":
        flash('Dossier créé avec succés!')
        nom_produit = request.form['nom_produit']
        fournisseur = request.form['fournisseur']
        date_sortie = request.form['date_sortie']
        date_reception = request.form['date_reception']
        quantite = float(request.form['quantite'])
        prix_unit = float(request.form['prix_unit'])
        # Calculer Montants HT et TTC côté serveur
        montant_ht = quantite * prix_unit
        taux_tva = 0.18  # TVA à 18% 
        tva = montant_ht * taux_tva
        montant_ttc = montant_ht * (1 + taux_tva)
        observations = request.form['observations']
        conn, cursor = init_db()
        materiels = Materiel(None, nom_produit, fournisseur, date_sortie, date_reception, quantite, prix_unit, montant_ht, tva, montant_ttc, observations)
        materiels.save(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('comptabilite_matiere'))

@app.route('/comptabilite-matiere/update', methods=['POST', 'GET'])
@login_required
@role_required('Digital')
def update_comptabilite_matiere():
    if request.method == "POST":
        flash('Dossier modifié avec succés!')
        id_data = request.form['id']
        nom_produit = request.form['nom_produit']
        fournisseur = request.form['fournisseur']
        date_sortie = request.form['date_sortie']
        date_reception = request.form['date_reception']
        quantite = float(request.form['quantite'])
        prix_unit = float(request.form['prix_unit'])
        # Calculer Montants HT et TTC côté serveur
        montant_ht = quantite * prix_unit
        taux_tva = 0.18  # TVA à 18% 
        tva = montant_ht * taux_tva
        montant_ttc = montant_ht * (1 + taux_tva)
        observations = request.form['observations']
        conn, cursor = init_db()
        materiels = Materiel(id_data, nom_produit, fournisseur, date_sortie, date_reception, quantite, prix_unit, montant_ht, tva, montant_ttc, observations)
        materiels.update(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('comptabilite_matiere'))

@app.route('/comptabilite-matiere/delete/<string:id_data>', methods = ['POST', 'GET'])
@login_required
@role_required('Digital')
def delete_comptabilite_matiere(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM materiels WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('materiels'))

@app.route('/export-comptabilite-matiere')
def export_materiels():
    conn, cursor = init_db()
    # Charger les données depuis la base de données dans un DataFrame
    df = pd.read_sql_query("SELECT * FROM materiels", conn)
    cursor.close()
    
    # Créer un fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Comptabilité Matière')
    output.seek(0)  # Revenir au début du fichier mémoire

    # Retourner le fichier pour téléchargement
    return Response(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment;filename=comptabilite-matiere.xlsx'
        }
    )

# COMPTABILITE FINANCIERE
@app.route('/comptabilite-financiere')
@login_required
@role_required('Digital')
def comptabilite_financiere():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM finances")
    data_finances = cursor.fetchall()
    cursor.close()
    return render_template('comptabilite-financiere.html', finances=data_finances)

@app.route('/comptabilite-financiere/insert', methods=['POST'])
@login_required
@role_required('Digital')
def insert_comptabilite_financiere():
    if request.method == "POST":
        flash('Dossier créé avec succés!')
        date = request.form['date']
        libelle = request.form['libelle']
        numero_compte = request.form['numero_compte']
        credit = float(request.form['credit'])
        debit = float(request.form['debit'])
        # Calculer Montants HT et TTC côté serveur
        montant_ht = float(request.form['montant_ht'])
        taux_tva = 0.18  # TVA à 18% 
        tva = montant_ht * taux_tva
        montant_ttc = montant_ht * (1 + taux_tva)
        observations = request.form['observations']
        conn, cursor = init_db()
        finances = Finance(None, date, libelle, numero_compte, credit, debit, montant_ht, tva, montant_ttc, observations)
        finances.save(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('comptabilite_financiere'))

@app.route('/comptabilite-financiere/update', methods=['POST', 'GET'])
@login_required
@role_required('Digital')
def update_comptabilite_financiere():
    if request.method == "POST":
        flash('Dossier modifié avec succés!')
        id_data = request.form['id']
        date = request.form['date']
        libelle = request.form['libelle']
        numero_compte = request.form['numero_compte']
        credit = float(request.form['credit'])
        debit = float(request.form['debit'])
        # Calculer Montants HT et TTC côté serveur
        montant_ht = float(request.form['montant_ht'])
        taux_tva = 0.18  # TVA à 18% 
        tva = montant_ht * taux_tva
        montant_ttc = montant_ht * (1 + taux_tva)
        observations = request.form['observations']
        conn, cursor = init_db()
        finances = Finance(id_data, date, libelle, numero_compte, credit, debit, montant_ht, tva, montant_ttc, observations)
        finances.update(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('comptabilite_financiere'))

@app.route('/comptabilite-financiere/delete/<string:id_data>', methods = ['POST', 'GET'])
@login_required
@role_required('Digital')
def delete_comptabilite_financiere(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM finances WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('comptabilite_financiere'))

@app.route('/export-comptabilite-financiere')
def export_finances():
    conn, cursor = init_db()
    # Charger les données depuis la base de données dans un DataFrame
    df = pd.read_sql_query("SELECT * FROM finances", conn)
    cursor.close()
    
    # Créer un fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Comptabilité Financière')
    output.seek(0)  # Revenir au début du fichier mémoire

    # Retourner le fichier pour téléchargement
    return Response(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment;filename=comptabilite-financiere.xlsx'
        }
    )

# PROJETS
@app.route('/projets')
@login_required
def projets():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM projets")
    data_projets = cursor.fetchall()
    cursor.close()
    return render_template('projet.html', projets=data_projets)

@app.route('/projets/insert', methods=['POST'])
@login_required
def insert_projet():
    if request.method == "POST":
        flash('Dossier créé avec succés!')
        nom = request.form['nom']
        description = request.form['description']
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin'] or None
        budget = float(request.form['budget'])
        statut = request.form['statut']
        departement = request.form['departement']
        conn, cursor = init_db()
        projets = Projet(None, nom, description, date_debut, date_fin, budget, statut, departement)
        projets.save(cursor)
        conn.commit()
        conn.close()
    return redirect(url_for('projets'))

@app.route('/projets/update', methods=['POST', 'GET'])
@login_required
def update_projet():
    if request.method == "POST":
        flash('Dossier modifié avec succés!')
        id_data = request.form['id']
        nom = request.form['nom']
        description = request.form['description']
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin'] or None
        budget = float(request.form['budget']) or 0
        statut = request.form['statut']
        departement = request.form['departement']
        conn, cursor = init_db()
        projets = Projet(id_data, nom, description, date_debut, date_fin, budget, statut, departement)
        projets.update(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('projets'))

@app.route('/projets/delete/<string:id_data>', methods = ['POST', 'GET'])
@login_required
def delete_projet(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM projets WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('projets'))

@app.route('/export-projets')
def export_projets():
    conn, cursor = init_db()
    # Charger les données depuis la base de données dans un DataFrame
    df = pd.read_sql_query("SELECT * FROM projets", conn)
    cursor.close()
    
    # Créer un fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Projets')
    output.seek(0)  # Revenir au début du fichier mémoire

    # Retourner le fichier pour téléchargement
    return Response(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment;filename=projets.xlsx'
        }
    )

# EVENEMENTIELS
@app.route('/evenementiels')
@login_required
def evenementiels():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM evenementiels")
    data_evenementiels = cursor.fetchall()
    cursor.close()
    return render_template('evenementiel.html', evenementiels=data_evenementiels)

@app.route('/evenementiels/insert', methods=['POST'])
@login_required
def insert_evenementiel():
    if request.method == "POST":
        flash('Dossier créé avec succés!')
        nom = request.form['nom']
        description = request.form['description']
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin'] or None
        budget = float(request.form['budget'])
        statut = request.form['statut']
        departement = request.form['departement']
        conn, cursor = init_db()
        evenementiels = Evenementiel(None, nom, description, date_debut, date_fin, budget, statut, departement)
        evenementiels.save(cursor)
        conn.commit()
        conn.close()
    return redirect(url_for('evenementiels'))

@app.route('/evenementiels/update', methods=['POST', 'GET'])
@login_required
def update_evenementiel():
    if request.method == "POST":
        flash('Dossier modifié avec succés!')
        id_data = request.form['id']
        nom = request.form['nom']
        description = request.form['description']
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin'] or None
        budget = float(request.form['budget']) or 0
        statut = request.form['statut']
        departement = request.form['departement']
        conn, cursor = init_db()
        evenementiels = Evenementiel(id_data, nom, description, date_debut, date_fin, budget, statut, departement)
        evenementiels.update(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('projets'))

@app.route('/evenementiels/delete/<string:id_data>', methods = ['POST', 'GET'])
@login_required
def delete_evenementiel(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM evenementiels WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('evenementiels'))

@app.route('/export-evenementiels')
def export_evenementiels():
    conn, cursor = init_db()
    # Charger les données depuis la base de données dans un DataFrame
    df = pd.read_sql_query("SELECT * FROM evenementiels", conn)
    cursor.close()
    
    # Créer un fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Evenementiels')
    output.seek(0)  # Revenir au début du fichier mémoire

    # Retourner le fichier pour téléchargement
    return Response(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment;filename=evenementiels.xlsx'
        }
    )

# PERSONNELS
@app.route('/personnels')
@login_required
@role_required('Administrator')
def personnels():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM personnels")
    data_personnels = cursor.fetchall()
    cursor.close()
    return render_template('personnel.html', personnels=data_personnels)

@app.route('/personnels/insert', methods=['POST'])
@login_required
@role_required('Administrator')
def insert_personnels():
    if request.method == "POST":
        flash('Dossier créé avec succés!')
        nom = request.form['nom']
        prenom = request.form['prenom']
        username = request.form['username']
        phone = request.form['phone']
        email = request.form['email']
        departement = request.form['departement']
        date_arrivee = request.form['date_arrivee']
        date_depart = request.form['date_depart'] if request.form['date_depart'] else None
        ecole = request.form['ecole']
        convention = request.form['convention']
        password = hash_password(request.form['password'])
        role = request.form['role']
        observations = request.form['observations'] if request.form['observations'] else None
        conn, cursor = init_db()
        personnel = Personnel(None, nom, prenom, username, email, phone, departement, date_arrivee, date_depart, ecole, convention, password, role, observations)
        personnel.save(cursor)
        conn.commit()
        conn.close()
    
    return redirect(url_for('personnels'))

@app.route('/personnels/update', methods=['POST', 'GET'])
@login_required
@role_required('Administrator')
def update_personnels():
    if request.method == "POST":
        # Récupération des données du formulaire
        id_data = request.form.get('id')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        departement = request.form.get('departement')
        date_arrivee = request.form.get('date_arrivee')
        date_depart = request.form.get('date_depart') or None
        ecole = request.form.get('ecole')
        convention = request.form.get('convention')
        password_form = request.form.get('password', '').strip()
        role = request.form.get('role')
        observations = request.form.get('observations')

        # Connexion à la base de données
        conn, cursor = init_db()
        cursor = conn.cursor(dictionary=True)

        # Récupération de l'utilisateur existant
        cursor.execute("SELECT * FROM personnels WHERE id=%s", (id_data,))
        data_personnel_id = cursor.fetchone()

        if not data_personnel_id:
            flash("Utilisateur introuvable !", "danger")
            return redirect(url_for('personnels'))

        # Obtenir l'ancien mot de passe
        existing_password = data_personnel_id['password'] # type: ignore

        # Gestion du mot de passe (conserver l'ancien si le champ est vide)
        password = hash_password(password_form) if password_form else existing_password

        # Mise à jour des données dans la base
        personnel = Personnel(id=id_data, nom=nom, prenom=prenom, username=username, email=email, phone=phone, departement=departement, date_arrivee=date_arrivee, date_depart=date_depart, ecole=ecole, convention=convention, password=password, role=role, observations=observations)

        try:
            personnel.update(cursor)  # Mise à jour
            conn.commit()
            flash("Les informations du personnel ont été mises à jour avec succès.", "success")
        except mysql.connector.Error as e:
            flash(f"Erreur lors de la mise à jour : {e}", "danger")
        finally:
            conn.close()

        # Redirection vers la liste des personnels
        return redirect(url_for('personnels'))

    return redirect(url_for('personnels'))


@app.route('/personnels/delete/<string:id_data>', methods = ['POST', 'GET'])
@login_required
@role_required('Administrator')
def delete_personnels(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM personnels WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('personnels'))

@app.route('/export-personnels')
def export_personnels():
    conn, cursor = init_db()
    # Charger les données depuis la base de données dans un DataFrame
    df = pd.read_sql_query("SELECT * FROM personnels", conn)
    cursor.close()
    
    # Créer un fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Personnels')
    output.seek(0)  # Revenir au début du fichier mémoire

    # Retourner le fichier pour téléchargement
    return Response(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment;filename=personnels.xlsx'
        }
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    conn, cursor = init_db()
    conn.commit()
    conn.close()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = hash_password(password)
        conn, cursor = init_db()
        cursor.execute("SELECT * FROM personnels WHERE username=%s AND password=%s", (username, hashed_password))
        user = cursor.fetchone()
        conn.commit()
        conn.close()        
        if user:
            session['id'] = user[0] # type: ignore
            session['username'] = user[3] # type: ignore
            session['role'] = user[12] # type: ignore
            return redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous êtes déconnecté', 'success')
    return redirect(url_for('login'))

@app.route('/api/dashboard-data')
def dashboard_data():
    conn, cursor = init_db()

    # Récupérer les données financières
    cursor.execute("SELECT SUM(credit), SUM(debit) FROM finances")
    total_credit, total_debit = cursor.fetchone() # type: ignore
    
    # Récupérer les ventes et dépenses par mois
    cursor.execute("SELECT DATE_FORMAT(date, '%d/%m') AS jour, SUM(credit), SUM(debit) FROM finances GROUP BY jour ORDER BY date ASC LIMIT 8")
    finance_data = cursor.fetchall()
    dates, credits, debits = zip(*finance_data) if finance_data else ([], [], [])

    # Récupérer les projets par statut
    cursor.execute("SELECT statut, COUNT(*) FROM projets GROUP BY statut")
    projets_data = dict(cursor.fetchall()) # type: ignore

    # Récupérer les 7 derniers jours de transactions (crédit - débit par jour)
    cursor.execute("""
        SELECT DATE_FORMAT(date, '%d/%m') AS jour, SUM(credit) - SUM(debit) AS earnings
        FROM finances
        GROUP BY jour
        ORDER BY date DESC
        LIMIT 7
    """)
    earning_results = cursor.fetchall()

    # Transformer les résultats en listes
    dates, earnings = zip(*earning_results) if earning_results else ([], [])

    conn.close()

    return jsonify({
        "dates": list(dates),
        "earnings": list(credits),
        "expenses": list(debits),
        "total_credit": total_credit or 0,
        "total_debit": total_debit or 0,
        "projets": projets_data,
        "dates": list(dates),
        "gains": list(earnings)
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")