#on lance tout depuis ce fichier : simulation, estimations, erreurs et graphiques
#par défaut on compare les cinq filtres sur un cas choisi
#avec --tout on reprend les scénarios de la question 2.4 : plusieurs q, T et erreurs initiales
#on impose theta_hat_1/0-theta_1=+0.05 ou -0.05 selon le scénario
#la vraie position sert à construire le test, elle n'est pas fournie aux filtres
#le simulateur reste déterministe : q règle l'incertitude des filtres, pas un bruit ajouté à la simulation
#les trois Kalman (classique, EKF, UKF) doivent coïncider sur ce modèle linéaire

import argparse
import numpy as np
import parametres as p
from modele_moteur import entree, simule, matrices
from filtre_kalman import estimer as kalman
from filtre_stationnaire import estimer as stationnaire
from filtre_ekf import estimer as ekf
from filtre_ukf import estimer as ukf
from filtre_particulaire import estimer as particulaire


def comparer(q, T_filtre, erreur, nombre):
    #on simule une commande et des mesures communes à toutes les méthodes
    u = entree(p.D, p.Acc, p.delta, p.Te)
    x, y = simule(u, p.G_exact, p.T_exact, p.Te, p.L, p.x1)
    F, B = matrices(p.G_filtre, T_filtre, p.Te)
    H = np.array([[1., 0.]])
    Q = q * (B @ B.T)
    R = np.array([[(2*np.pi/p.L)**2 / 12]])
    #vitesse connue nulle et erreur initiale imposée sur la position
    x0 = np.array([[x[0, 0] + erreur], [0.]])
    arguments = (y, u, F, B, H, Q, R, x0, p.P0.copy())
    estimations = {
        'Kalman': kalman(*arguments),
        'Stationnaire': stationnaire(*arguments),
        'EKF': ekf(*arguments),
        'UKF': ukf(*arguments),
        'Particulaire': particulaire(*arguments, nombre=nombre),
    }
    print(f'\nq={q:g} V² | T filtre={T_filtre*1000:g} ms | erreur initiale={erreur:+g} rad')
    print('Filtre          RMSE position (rad)   RMSE vitesse (rad/s)')
    for nom, xe in estimations.items():
        #on compare à la vérité uniquement pour évaluer le résultat
        #RMSE=racine de la moyenne des erreurs au carré, démarrage compris
        rmse = np.sqrt(np.mean((xe-x)**2, axis=1))
        print(f'{nom:15s} {rmse[0]:19.6g} {rmse[1]:22.6g}')
    return u, x, y, estimations


def main():
    parser = argparse.ArgumentParser(description='Comparaison des filtres sur le moteur')
    parser.add_argument('--q', type=float, default=p.q)
    parser.add_argument('--t-filtre', type=float, default=p.T, help='En secondes')
    parser.add_argument('--erreur', type=float, default=0.05, help='En radians')
    parser.add_argument('--particules', type=int, default=20000)
    parser.add_argument('--tout', action='store_true', help='Tous les scénarios de la question 2.4')
    parser.add_argument('--simulation', action='store_true', help='Afficher aussi commande, codeur et quantification')
    parser.add_argument('--sans-affichage', action='store_true')
    args = parser.parse_args()
    qs = list(p.q_tests) if args.tout else [args.q]
    Ts = list(p.T_filtres) if args.tout else [args.t_filtre]
    erreurs = list(p.erreurs_initiales) if args.tout else [args.erreur]
    if not qs or not Ts or not erreurs or any(q < 0 for q in qs) or any(T <= 0 for T in Ts) or args.particules < 1:
        parser.error('Listes non vides, q >= 0, T > 0 et particules >= 1 requis')
    if not args.sans_affichage:
        import matplotlib.pyplot as plt
    simulation = None
    for T_filtre in Ts:
        for erreur in erreurs:
            if args.tout and not args.sans_affichage:
                fig, axes = plt.subplots(2, len(qs), figsize=(4*len(qs), 7), sharex=True, squeeze=False)
            for j, q in enumerate(qs):
                u, x, y, estimations = comparer(q, T_filtre, erreur, args.particules)
                simulation = (u, x, y)
                if args.sans_affichage:
                    continue
                t = np.arange(len(u))*p.Te
                if args.tout:
                    #grille de la question 2.4 : une colonne par q, position puis vitesse
                    for i in range(2):
                        for nom, xe in estimations.items():
                            axes[i, j].plot(t, xe[i]-x[i], label=nom)
                        axes[i, j].axhline(0, color='black', linewidth=0.5)
                        axes[i, j].grid()
                        axes[i, j].legend(fontsize='small')
                    axes[0, j].set_title(f'q={q:g} V²')
                    axes[1, j].set_xlabel('Temps (s)')
                else:
                    fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True)
                    for i, unite in enumerate(('rad', 'rad/s')):
                        axes[i, 0].plot(t, x[i], 'k', label='Réel')
                        for nom, xe in estimations.items():
                            axes[i, 0].plot(t, xe[i], '--', label=nom)
                            axes[i, 1].plot(t, xe[i]-x[i], label=nom)
                        axes[i, 0].set_ylabel(('Position' if i == 0 else 'Vitesse') + f' ({unite})')
                        axes[i, 1].set_ylabel(f'Erreur ({unite})')
                    for ax in axes.flat:
                        ax.grid()
                        ax.legend()
                    for ax in axes[-1]:
                        ax.set_xlabel('Temps (s)')
                    fig.suptitle(f'q={q:g} V² | T filtre={T_filtre*1000:g} ms | écart initial={erreur:+g} rad')
                    fig.tight_layout()
            if args.tout and not args.sans_affichage:
                axes[0, 0].set_ylabel('Erreur de position (rad)')
                axes[1, 0].set_ylabel('Erreur de vitesse (rad/s)')
                fig.suptitle(f'T réel={p.T_exact*1000:g} ms | T filtre={T_filtre*1000:g} ms | écart initial={erreur:+g} rad')
                fig.tight_layout(rect=(0, 0, 1, 0.93))
    if args.simulation and not args.sans_affichage:
        #on garde aussi les graphiques utiles de l'ancien main.py
        u, x, y = simulation
        t = np.arange(len(u))*p.Te
        fig, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
        axes[0].step(t, u, where='post', label='Commande (V)')
        axes[1].plot(t, x[0], label='Position réelle (rad)')
        axes[1].step(t, y, where='post', label='Codeur (rad)')
        axes[2].plot(t, x[1], label='Vitesse réelle (rad/s)')
        #erreur signée y-theta : sa valeur absolue reste sous un demi-pas
        axes[3].plot(t, y-x[0], label='Erreur du codeur (rad)')
        for ax in axes:
            ax.grid()
            ax.legend()
        axes[-1].set_xlabel('Temps (s)')
        fig.tight_layout()
    if not args.sans_affichage:
        plt.show()



if __name__ == '__main__':
    main()
