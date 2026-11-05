#2.1 et 2.2 : on synthétise la commande puis on simule le moteur
#x_k=[theta_k,omega_k] ; dtheta/dt=omega et domega/dt=-omega/T+G*u/T
#on suppose la tension constante entre deux échantillons
#on prend donc la discrétisation exacte : F=exp(A*Te)
#Bd=intégrale de exp(A*tau)*B_continu entre 0 et Te
#attention ici la variable B désigne Bd, pas la matrice B du modèle continu
#on mesure uniquement la position, quantifiée par le codeur à L valeurs par tour
#la simulation renvoie x de taille (2,N) et y de taille (N,)
#si on veut les deux colonnes demandées dans le sujet, on prend x.T ou xe.T

import numpy as np


def matrices(G, T, Te):
    a = np.exp(-Te / T)
    F = np.array([[1., T * (1 - a)], [0., a]])
    B = np.array([[G * (Te - T * (1 - a))], [G * (1 - a)]])
    return F, B


def entree(D, amplitude, periode, Te):
    t = np.arange(0., D, Te)
    return amplitude / 2 * np.sign(np.sin(2 * np.pi * t / periode))


def simule(u, G, T, Te, L, x1):
    u = np.asarray(u).reshape(-1)
    F, B = matrices(G, T, Te)
    x = np.zeros((2, len(u)))
    x[:, 0] = np.asarray(x1).reshape(2)
    for k in range(len(u) - 1):
        x[:, k + 1] = F @ x[:, k] + B.ravel() * u[k]
    pas = 2 * np.pi / L
    
    #l'arrondi crée déjà le bruit de quantification, on n'en rajoute pas un deuxième
    y = np.round(x[0] / pas) * pas
    return x, y
