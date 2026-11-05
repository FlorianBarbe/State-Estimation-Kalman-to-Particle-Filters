#On fait figurer ici tous les paramètres du problème

import numpy as np

L=512 #2^9, nombre de points du codeur incrémental
pas=2*np.pi/L #pas de quantification du codeur incrémental
p=9 #nombre de bits du codeur incrémental
delta =100e-3#période du créneau de la tension d'alimentation
Acc=0.1#tension crête à crête du signal d'alimentation
Te=1e-3 #période d'échantillonnage du créneau
G=50 #gain du moteur
T=20e-3 #constante de temps du moteur
D = 500e-3# durée totale de la simulation en secondes

#position et angle initiaux
theta0=0
omega0=0
x1=[theta0,omega0]

M=(2*np.pi)**2 #incertitude sur la position initiale theta_0 en rad^2, on prend une grande incertitude sur la position initiale theta_0 car on ne la connait pas du tout
q = 0.0 # Variance du bruit sur la tension d'entrée, en V²
r=pas**2/12 # Variance du bruit de mesure du codeur incrémental, en rad²

A=np.array([[0,1],[0,-1/T]]) #matrice du système continu
B=np.array([[0],[G/T]]) #matrice du système continu
a=np.exp(-Te/T) #coefficient de la matrice de transition d'état F

#matrices du modèle discret exact à entrée constante
F = np.array([[1., T * (1 - a)],[0., a]])
Bd = np.array([[G*(Te-T*(1-a))],[G*(1 - a)]])

# Mesure : seule la position est mesurée
H = np.array([[1., 0.]])

# Covariances des bruits
Q = q * (Bd @ Bd.T)          # forme (2, 2)
R = np.array([[r]])          # forme (1, 1)

# Estimation initiale : position arbitraire, vitesse nulle
x0_estime = np.array([[0.],[0.]])

# Position inconnue, vitesse connue exactement
# Grande variance illustrative sur la position
P0 = np.diag([M, 0.])