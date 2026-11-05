#on regroupe ici les paramètres du problème pour éviter de les recopier partout
#contexte : on cherche à estimer x_k=(theta_k,omega_k) à partir de u et du codeur
#u_k est la tension, v_k le bruit sur cette tension, de variance q, indépendant de w_k
#w_k est le bruit de mesure supposé blanc ; le sujet ne le suppose pas forcément gaussien
#pour le codeur à L valeurs par tour, pas=2*pi/L et r=pas²/12
#ça correspond à une erreur uniforme sur [-pas/2,pas/2]
#on utilisera une vraisemblance gaussienne approchée dans le filtre particulaire
#on sait que le moteur est initialement à l'arrêt mais on ne connaît pas theta initial
#on propose donc une position arbitraire avec beaucoup d'incertitude : P0=diag(M,0)
#les covariances sont nulles car l'erreur de vitesse initiale est exactement nulle
#M est la variance choisie ci-dessous, en rad², pas un écart-type
#q est une variance scalaire d'entrée ; Q=q*Bd*Bd.T est une matrice 2x2
#pour les simulations on distingue bien les paramètres exacts de ceux des filtres

import numpy as np

L=512 
pas=2*np.pi/L 
p=9 
delta =100e-3
Acc=0.1
Te=1e-3 
G=50 
T=20e-3 
D = 500e-3


G_exact = 50.
T_exact = 20e-3

G_filtre = 50.
T_filtres = [20e-3, 25e-3]


theta0=1
omega0=0
x1=[theta0,omega0]

M=(2*np.pi)**2 
q = 0.05 


q_tests = [0., 1e-6, 1e-4, 1e-2]


erreurs_initiales = [-0.05, 0.05]

r=pas**2/12 

A=np.array([[0,1],[0,-1/T]]) 
B=np.array([[0],[G/T]]) 
a=np.exp(-Te/T) 


F = np.array([[1., T * (1 - a)],[0., a]])
Bd = np.array([[G*(Te-T*(1-a))],[G*(1 - a)]])


H = np.array([[1., 0.]])



#on transforme le bruit de tension en bruit sur les deux composantes de l’état
Q = q * (Bd @ Bd.T)          
R = np.array([[r]])          


x0_estime = np.array([[0.],[0.]])




#la vitesse est connue nulle ; seule la position initiale est incertaine
P0 = np.diag([M, 0.])