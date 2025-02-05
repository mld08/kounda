import mysql.connector


class Projet:
    def __init__(self, id, nom, description, date_debut, date_fin, budget, statut, departement):
        self.id = id
        self.nom = nom
        self.description = description
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.budget = budget
        self.statut = statut
        self.departement = departement

    def save(self, cursor):
        try:
            sql = """
            INSERT INTO projets (nom, description, date_debut, date_fin, budget, statut, departement) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (self.nom, self.description, self.date_debut, self.date_fin, self.budget, self.statut, self.departement))
        except mysql.connector.Error as e:
            print(f"Erreur lors de l'insertion du projet dans la BD : {e}")

    def update(self, cursor):
        try:
            sql = """
            UPDATE projets 
            SET nom=%s, description=%s, date_debut=%s, date_fin=%s, budget=%s, statut=%s, departement=%s
            WHERE id = %s
            """
            cursor.execute(sql, (self.nom, self.description, self.date_debut, self.date_fin, self.budget, self.statut, self.departement, self.id))
        except mysql.connector.Error as e:
            print(f"Erreur lors de la modification du projet dans la BD : {e}")
