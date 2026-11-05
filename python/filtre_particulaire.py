#filtre particulaire bootstrap sur le même problème moteur
#on initialise des positions et vitesses possibles selon x0 et P0
#on les propage avec F, Bd et le bruit de covariance Q=q*Bd*Bd.T
#chaque poids indique si la mesure prédite par la particule correspond au codeur
#on approxime la vraisemblance de mesure par une gaussienne de variance R[0,0]
#on estime l'état par la moyenne pondérée avant de rééchantillonner
#on rééchantillonne ensuite pour conserver les particules les plus compatibles avec y
#seed fixe le hasard pour pouvoir reproduire la simulation
#si q=0, on peut perdre de la diversité : c'est une limite du bootstrap

import numpy as np


def estimer(y, u, F, B, H, Q, R, x0, P0, nombre=20000, seed=42):
    y, u = np.asarray(y).ravel(), np.asarray(u).ravel()
    rng = np.random.default_rng(seed)
    particules = rng.multivariate_normal(np.asarray(x0).ravel(), P0, size=nombre)
    
    #Q est singulière : on calcule sa racine avec ses valeurs propres
    valeurs, vecteurs = np.linalg.eigh(Q)
    racine_Q = vecteurs @ np.diag(np.sqrt(np.maximum(valeurs, 0.)))
    xe = np.zeros((2, len(y)))
    for k, z in enumerate(y):
        if k:
            bruit = rng.standard_normal((nombre, 2)) @ racine_Q.T
            particules = particules @ F.T + B.ravel() * u[k - 1] + bruit
        residus = z - (particules @ H.T).ravel()
        
        #calcul en log pour éviter que tous les poids deviennent numériquement nuls
        log_poids = -0.5 * residus**2 / R[0, 0]
        poids = np.exp(log_poids - log_poids.max())
        poids /= poids.sum()
        
        #on calcule la moyenne avant le rééchantillonnage
        xe[:, k] = poids @ particules
        
        #rééchantillonnage systématique ; les nouveaux poids sont uniformes
        cumul = np.cumsum(poids)
        cumul[-1] = 1.
        positions = (rng.random() + np.arange(nombre)) / nombre
        particules = particules[np.searchsorted(cumul, positions)]
    return xe
