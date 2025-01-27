from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
import mysql.connector
import hashlib
from Models.trading import Trading
from Models.personnel import Personnel
from Models.academy import Academy
from Models.digital import Digital
from Models.materiel import Materiel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

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
            email VARCHAR(25) UNIQUE,
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
    """cursor.execute("SELECT * FROM users WHERE role='Administrator' and username='admin' ")
    existing_admin = cursor.fetchone()
    if not existing_admin:
        password = hash_password("admin")
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)", ('admin', 'mldiop08@gmail.com', password, 'Administrator'))"""
    conn.commit()
    return conn, cursor

@app.route('/')
def index():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM trading")
    data_trading = cursor.fetchall()
    cursor.close()
    return render_template('index.html', trading=data_trading)

# TRADING
@app.route('/trading')
def trading():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM trading t JOIN personnels p ON t.personnel_id = p.id")
    data_trading = cursor.fetchall()
    cursor.execute("SELECT * FROM personnels")
    data_personnels = cursor.fetchall()
    cursor.close()
    return render_template('trading.html', tradings=data_trading, personnels=data_personnels)

@app.route('/trading/insert', methods=['POST'])
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
def delete_trading(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM trading WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('trading'))

# ACADEMY
@app.route('/academy')
def academy():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM academy t JOIN personnels p ON t.personnel_id = p.id")
    data_academy = cursor.fetchall()
    cursor.execute("SELECT * FROM personnels")
    data_personnels = cursor.fetchall()
    cursor.close()
    return render_template('academy.html', academys=data_academy, personnels=data_personnels)

@app.route('/academy/insert', methods=['POST'])
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
def delete_academy(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM academy WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('academy'))

# DIGITAL
@app.route('/digital')
def digital():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM digital t JOIN personnels p ON t.personnel_id = p.id")
    data_digital = cursor.fetchall()
    cursor.execute("SELECT * FROM personnels")
    data_personnels = cursor.fetchall()
    cursor.close()
    return render_template('digital.html', digitals=data_digital, personnels=data_personnels)

@app.route('/digital/insert', methods=['POST'])
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
def delete_digital(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM digital WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('digital'))

# MATERIELS
@app.route('/materiels')
def materiels():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM materiels")
    data_materiels = cursor.fetchall()
    cursor.close()
    return render_template('materiel.html', materiels=data_materiels)

@app.route('/materiels/insert', methods=['POST'])
def insert_materiels():
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
    
    return redirect(url_for('materiels'))

@app.route('/materiels/update', methods=['POST', 'GET'])
def update_materiels():
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
    
    return redirect(url_for('materiels'))

@app.route('/materiels/delete/<string:id_data>', methods = ['POST', 'GET'])
def delete_materiels(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM materiels WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('materiels'))


# PERSONNELS
@app.route('/personnels')
def personnels():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM personnels")
    data_personnels = cursor.fetchall()
    cursor.close()
    return render_template('personnel.html', personnels=data_personnels)

@app.route('/personnels/insert', methods=['POST'])
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
def delete_personnels(id_data):
    conn, cursor = init_db()
    flash('Dossier supprimé avec succés')
    cursor.execute("DELETE FROM personnels WHERE id=%s", (id_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('personnels'))


if __name__ == "__main__":
    app.run(debug=True)