#on applique aussi l'EKF au moteur pour comparer avec Kalman
#en général on linéarise f et h avec leurs Jacobiennes
#ici f(x,u)=F*x+Bd*u et h(x)=H*x, donc les Jacobiennes sont simplement F et H
#on doit donc retrouver exactement le filtre de Kalman avec les mêmes paramètres
#FilterPy utilise F pour propager P et HJacobian pour corriger avec la mesure

import numpy as np
from filterpy.kalman import ExtendedKalmanFilter


def estimer(y, u, F, B, H, Q, R, x0, P0):
    y, u = np.asarray(y).ravel(), np.asarray(u).ravel()
    kf = ExtendedKalmanFilter(dim_x=2, dim_z=1)
    
    kf.F, kf.B = F.copy(), B.copy()
    kf.Q, kf.R = Q.copy(), R.copy()
    kf.x, kf.P = np.asarray(x0).reshape(2, 1).copy(), P0.copy()
    xe = np.zeros((2, len(y)))
    for k, z in enumerate(y):
        if k:
            kf.predict(u=np.array([[u[k - 1]]]))
        
        #la mesure prédite vaut H*x et sa Jacobienne vaut H
        kf.update(np.array([[z]]), HJacobian=lambda x: H, Hx=lambda x: H @ x)
        xe[:, k] = kf.x.ravel()
    return xe
