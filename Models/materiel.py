import mysql.connector

import mysql.connector

class Materiel:
    def __init__(self, id, nom_produit, fournisseur, date_sortie, date_reception, quantite, prix_unit, montant_ht, tva, montant_ttc, observations):
        self.id = id
        self.nom_produit = nom_produit
        self.fournisseur = fournisseur
        self.date_sortie = date_sortie
        self.date_reception = date_reception
        self.quantite = quantite
        self.prix_unit = prix_unit
        self.montant_ht = montant_ht
        self.tva = tva
        self.montant_ttc = montant_ttc
        self.observations = observations

    def save(self, cursor):
        try:
            sql = """
            INSERT INTO materiels (id, nom_produit, fournisseur, date_sortie, date_reception, quantite, prix_unit, montant_ht, tva, montant_ttc, observations) VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (self.id, self.nom_produit, self.fournisseur, self.date_sortie, self.date_reception, self.quantite, self.prix_unit, self.montant_ht, self.tva, self.montant_ttc, self.observations))
        except mysql.connector.Error as e:
            print(f"Erreur lors de l'insertion de Trading dans la bd: {e}")

    def update(self, cursor):
        try:
            sql = """UPDATE materiels SET nom_produit=%s, fournisseur=%s, date_sortie=%s, date_reception=%s, quantite=%s, prix_unit=%s, montant_ht=%s, tva=%s, montant_ttc=%s, observations=%s WHERE id = %s
            """
            cursor.execute(sql, (self.nom_produit, self.fournisseur, self.date_sortie, self.date_reception, self.quantite, self.prix_unit, self.montant_ht, self.tva, self.montant_ttc, self.observations, self.id))
        except mysql.connector.Error as e:
            print(f"Erreur lors de la modification de Trading dans la bd: {e}")
            
            