import mysql.connector


class Finance:
    def __init__(self, id, date, libelle, numero_compte, credit, debit, montant_ht, tva, montant_ttc, observations):
        self.id = id
        self.date = date
        self.libelle = libelle
        self.numero_compte = numero_compte
        self.credit = credit
        self.debit = debit
        self.montant_ht = montant_ht
        self.tva = tva
        self.montant_ttc = montant_ttc
        self.observations = observations

    def save(self, cursor):
        try:
            sql = """
            INSERT INTO finances (date, libelle, numero_compte, credit, debit, montant_ht, tva, montant_ttc, observations) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (self.date, self.libelle, self.numero_compte, self.credit, self.debit, self.montant_ht, self.tva, self.montant_ttc, self.observations))
        except mysql.connector.Error as e:
            print(f"Erreur lors de l'insertion de Finance dans la bd: {e}")

    def update(self, cursor):
        try:
            sql = """UPDATE finances SET date=%s, libelle=%s, numero_compte=%s, credit=%s, debit=%s, montant_ht=%s, tva=%s, montant_ttc=%s, observations=%s WHERE id = %s
            """
            cursor.execute(sql, (self.date, self.libelle, self.numero_compte, self.credit, self.debit, self.montant_ht, self.tva, self.montant_ttc, self.observations, self.id))
        except mysql.connector.Error as e:
            print(f"Erreur lors de la modification de Finance dans la bd: {e}")
            
            