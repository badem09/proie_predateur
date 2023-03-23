import itertools
import tkiteasy as tki
from characters import Proie, Predateur
import random


def pos_valide(x, y) -> bool:
    """
    :param x:
    :param y:
    :return: bool en fonction de la validité disponibilité de la postition
    """
    return 0 <= x < NB_CASES and 0 <= y < NB_CASES and not cadre[x][y]


def naissance_proie(num):
    for _ in range(num):
        x = y = None
        while not x or not y or cadre[x][y]:  # recherche d'une case libre.
            x = random.randint(0, NB_CASES - 1)
            y = random.randint(0, NB_CASES - 1)
        p = Proie(APROIE, g.dessinerDisque(x * RATIO + RATIO/2, y * RATIO + RATIO/2, RATIO/3, 'green'), x, y)
        cadre[x][y] = p
        proies.append(p)


def deplace_proie():
    for p in proies:
        pos = [(0, 0), (-1, 0), (0, -1), (1, 0), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        x, y = random.choice(pos)
        while len(pos) > 0 and not pos_valide(x + p.cadre_x, y + p.cadre_y):
            x, y = random.choice(pos)
            pos.remove((x, y))
        if len(pos) > 1:  # si deplacement
            cadre[p.cadre_x][p.cadre_y] = None
            g.deplacer(p.graph, x * RATIO, y * RATIO)
            p.cadre_y += y
            p.cadre_x += x
            cadre[p.cadre_x][p.cadre_y] = p
    death_proies()

def death_proies():
    dead_proie = set()
    for p in proies:
        p.age -= 1
        if p.age == 0:
            dead_proie.add(p)
        g.actualiser()

    for p in dead_proie:  #la faucheuse
        proies.remove(p)
        cadre[p.cadre_x][p.cadre_y] = None
        g.supprimer(p.graph)


def place_libre(p1, p2):
    positions = [(-1, 0), (0, -1), (1, 0), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for pos in positions:
        if pos_valide(p1.cadre_x + pos[0], p1.cadre_y + pos[1]):
            return p1.cadre_x + pos[0], p1.cadre_y + pos[1]
        if pos_valide(p2.cadre_x + pos[0], p2.cadre_y + pos[1]):
            return p2.cadre_x + pos[0], p2.cadre_y + pos[1]


def reprod_proie():
    en_couple = set()
    new_proies = []
    for p1 in proies:
        for p2 in proies:
            if p1 != p2 and proie_proches(p1, p2) and p1 not in en_couple and p2 not in en_couple:
                en_couple.update([p1, p2])
                new_pos = place_libre(p1, p2)
                if new_pos:
                    p = Proie(4, g.dessinerDisque(new_pos[0] * RATIO + RATIO/2, new_pos[1] * RATIO + RATIO/2, RATIO/3, 'green'),
                              *new_pos)
                    new_proies.append(p)
                    cadre[p.cadre_x][p.cadre_y] = p
                    g.actualiser()
    proies.extend(new_proies)


def proie_proches(p1, p2) -> bool:
    """
    :param p1: Proie
    :param p2: Proie
    :return: retourne un booléan en fonction de la proximité ou non de deux proies
    """
    return p1.graph.x == p2.graph.x or p1.graph.y == p2.graph.y \
           or abs(p1.graph.x - p2.graph.x) == RATIO or abs(p1.graph.y - p2.graph.y) == RATIO


def naissance_pred(num):
    for _ in range(num):
        x = y = None
        while not x or not y or cadre[x][y]:
            x = random.randint(0, NB_CASES -1)
            y = random.randint(0, NB_CASES -1)
        p = Predateur(EPRE, g.dessinerDisque(x * RATIO + RATIO/2, y * RATIO + RATIO/2, RATIO/3, 'red'), x, y)
        cadre[x][y] = p
        predateurs.append(p)


def find_proie(pred, n) -> Proie | None:
    """
    Trouve la proie l'une des proies les plus proches à n cases.
    :param pred: Predateur
    :param n: distance en cases
    :return: Proie | None
    """
    if len(proies) == 0:
        return
    positions = list(itertools.product(range(-n, n + 1), range(-n, n + 1)))
    #coordonnées des positions situés à n cases
    start = True
    while start or len(positions) > 1 and not isinstance(cadre[nx][ny], Proie):

        x, y = random.choice(positions)
        nx = x + pred.cadre_x
        ny = y + pred.cadre_y
        nx = 0 if nx < 0 else NB_CASES-1 if nx > NB_CASES-1 else nx
        ny = 0 if ny < 0 else NB_CASES-1 if ny > NB_CASES-1 else ny
        positions.remove((x, y))
        start = False
    return cadre[nx][ny] if len(positions) > 1 else None


def deplace_pred():
    if len(proies) == 0:
        return
    for pred in predateurs:
        n = 1 # portée du flair
        proie = find_proie(pred, n)
        while not proie:
            n += 1
            proie = find_proie(pred, n)
            if n > FLAIR:
                return

        cadre[pred.cadre_x][pred.cadre_y] = None
        dx = 1 if proie.cadre_x > pred.cadre_x else -1 if proie.cadre_x < pred.cadre_x else 0  # distance x
        dy = 1 if proie.cadre_y > pred.cadre_y else -1 if proie.cadre_y < pred.cadre_y else 0  # distance y
        if not cadre[pred.cadre_x][pred.cadre_y]:  # case libre
            pred.cadre_x += dx
            pred.cadre_y += dy
            cadre[pred.cadre_x][pred.cadre_y] = pred
            g.deplacer(pred.graph, dx * RATIO, dy * RATIO)

        if (pred.cadre_x, pred.cadre_y) == (proie.cadre_x, proie.cadre_y):  # Consommation d'une proie
            g.supprimer(proie.graph)
            proies.remove(proie)
            pred.energie += CALORIES_PROIE
            if len(proies) == 0:
                return

        if pred.energie % F_REPR_PRED == 0:
            naissance_pred(1)
        g.actualiser()


def death_pred():
    for pred in predateurs:
        pred.energie -= 1
        if pred.energie == 0:
            g.supprimer(pred.graph)
            predateurs.remove(pred)
            cadre[pred.cadre_x][pred.cadre_y] = None


if __name__ == '__main__':
    longueur = largeur = 600
    NB_CASES = 20
    RATIO = longueur // NB_CASES

    g = tki.ouvrirFenetre(longueur, largeur)
    proies = []
    predateurs = []
    liste = [None].copy() * NB_CASES
    cadre = [liste.copy() for _ in range(NB_CASES)]

    EPRE = 4  # énergie des prédateurs
    APROIE = 10  # durée de vie des proies
    FLAIR = 5  # flair des prédateurs
    F_REPR_PRED = 8  # Fréquence de reproduction des prédateurs
    CALORIES_PROIE = 2  # Points d'énergies aquis à la consommation d'une proie

    for i in range(0, longueur, longueur//NB_CASES):
        g.dessinerLigne(i, 0, i, longueur, 'white')
        g.dessinerLigne(0, i, longueur, i, 'white')

    liste_pred = []
    liste_proie = []

    naissance_proie(20)
    naissance_pred(5)
    for _ in range(500):
        liste_proie.append(len(proies))
        liste_pred.append(len(predateurs))
        naissance_proie(5)
        deplace_proie()
        g.actualiser()
        reprod_proie()
        g.actualiser()
        deplace_pred()
        g.actualiser()
        death_pred()
        if len(predateurs) == 0 or len(proies) == 0:
            break

    import matplotlib.pyplot as plt

    X = range(len(liste_proie))
    plt.plot(X, liste_pred,'r',label="Prédateurs")
    plt.plot(X, liste_proie,'g', label="Proies")

    plt.xlabel("Nombre de cycles")
    plt.ylabel("Taille de la population")
    plt.legend(loc="upper left")

    plt.show()

    g.attendreClic()
    g.fermerFenetre()
