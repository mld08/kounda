import mysql.connector

class Academy:
    def __init__(self, id, date_const, personnel_id, type_libelle, nom_client, prenom_client, phone_client, email_client, items, quantite, prix_unit, montant_ht, tva, montant_ttc, modalite_paiement, type_paiement, observations):
        self.id = id
        self.date_const = date_const
        self.personnel_id = personnel_id
        self.type_libelle = type_libelle
        self.nom_client = nom_client
        self.prenom_client = prenom_client
        self.phone_client = phone_client
        self.email_client = email_client
        self.items = items
        self.quantite = quantite
        self.prix_unit = prix_unit
        self.montant_ht = montant_ht
        self.tva = tva
        self.montant_ttc = montant_ttc
        self.modalite_paiement = modalite_paiement
        self.type_paiement = type_paiement
        self.observations = observations

    def save(self, cursor):
        try:
            sql = """
            INSERT INTO academy (id, date_const, personnel_id, type_libelle, nom_client, prenom_client, phone_client, email_client, items, quantite, prix_unit, montant_ht, tva, montant_ttc, modalite_paiement, type_paiement, observations) VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (self.id, self.date_const, self.personnel_id, self.type_libelle, self.nom_client, self.prenom_client, self.phone_client, self.email_client, self.items, self.quantite, self.prix_unit, self.montant_ht, self.tva, self.montant_ttc, self.modalite_paiement, self.type_paiement, self.observations))
        except mysql.connector.Error as e:
            print(f"Erreur lors de l'insertion de Trading dans la bd: {e}")

    def update(self, cursor):
        try:
            sql = """UPDATE academy SET date_const=%s, personnel_id=%s, type_libelle=%s, nom_client=%s, prenom_client=%s, phone_client=%s, email_client=%s, items=%s, quantite=%s, prix_unit=%s, montant_ht=%s, tva=%s, montant_ttc=%s, modalite_paiement=%s, type_paiement=%s, observations=%s WHERE id = %s
            """
            cursor.execute(sql, (self.date_const, self.personnel_id, self.type_libelle, self.nom_client, self.prenom_client, self.phone_client, self.email_client, self.items, self.quantite, self.prix_unit, self.montant_ht, self.montant_ttc, self.modalite_paiement, self.type_paiement, self.observations, self.id))
        except mysql.connector.Error as e:
            print(f"Erreur lors de la modification de Trading dans la bd: {e}")
            
            