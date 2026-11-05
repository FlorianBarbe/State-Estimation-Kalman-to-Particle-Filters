from pathlib import Path
import argparse
import contextlib
import csv
import io
import os
import sys
from importlib.metadata import version


def main():
    default = Path(__file__).resolve().parents[1] if Path(__file__).resolve().parent.name == 'docs' else Path('/home/florian/Desktop/State-Estimation-Kalman-to-Particle-Filters')
    parser = argparse.ArgumentParser(description='Génère le README, les figures et les résultats du moteur')
    parser.add_argument('--projet', type=Path, default=default)
    parser.add_argument('--particules', type=int, default=20000)
    args = parser.parse_args()
    root = args.projet.resolve()
    if args.particules < 1 or not (root/'python/comparaison.py').is_file():
        parser.error('Projet introuvable ou nombre de particules invalide')
    os.environ.setdefault('MPLCONFIGDIR', '/tmp/readme-moteur-matplotlib')
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root/'python'))
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import parametres as p
    from comparaison import comparer
    from modele_moteur import entree, simule

    #Les données et les figures sont calculées avant de remplacer le README.
    qs = list(p.q_tests)
    Ts = list(p.T_filtres)
    erreurs = list(p.erreurs_initiales)
    if not qs or not Ts or not erreurs:
        parser.error('Les listes de scénarios sont vides')
    resultats = {}
    rows = []
    ecart_ekf = ecart_ukf = 0.
    for T in Ts:
        for erreur in erreurs:
            for q in qs:
                with contextlib.redirect_stdout(io.StringIO()):
                    u, x, y, estimations = comparer(q, T, erreur, args.particules)
                for nom, xe in estimations.items():
                    if not np.isfinite(xe).all():
                        raise RuntimeError(f'Estimation non finie : {nom}')
                    rms = np.sqrt(np.mean((xe-x)**2, axis=1))
                    rows.append({'T_filtre_s':T,'q_V2':q,'erreur_initiale_rad':erreur,'filtre':nom,'rmse_position_rad':rms[0],'rmse_vitesse_rad_s':rms[1]})
                ecart_ekf=max(ecart_ekf,float(np.max(np.abs(estimations['EKF']-estimations['Kalman']))))
                ecart_ukf=max(ecart_ukf,float(np.max(np.abs(estimations['UKF']-estimations['Kalman']))))
                resultats[T,erreur,q]=(u,x,y,estimations)
                print(f'Calculé : T={T*1000:g} ms, q={q:g}, écart={erreur:+g}',flush=True)

    docs = root/'docs'
    figures = docs/'figures'
    figures.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.grid':True,'grid.alpha':.22,'savefig.facecolor':'white'})
    couleurs={'Kalman':'#2563eb','Stationnaire':'#ea580c','EKF':'#16a34a','UKF':'#9333ea','Particulaire':'#dc2626'}
    styles={'Kalman':'-','Stationnaire':'--','EKF':':','UKF':'-.','Particulaire':'-'}
    u=entree(p.D,p.Acc,p.delta,p.Te)
    x,y=simule(u,p.G_exact,p.T_exact,p.Te,p.L,p.x1)
    temps=np.arange(len(u))*p.Te
    fig, axes=plt.subplots(4,1,figsize=(11,8),sharex=True,layout='constrained')
    axes[0].step(temps,u,where='post',color='#ea580c')
    axes[0].set_ylabel('Tension (V)')
    axes[1].plot(temps,x[0],label='Position réelle',color='#2563eb')
    axes[1].step(temps,y,where='post',label='Codeur',color='#ea580c',alpha=.8)
    axes[1].set_ylabel('Position (rad)'); axes[1].legend(loc='upper left')
    axes[2].plot(temps,x[1],color='#2563eb'); axes[2].set_ylabel('Vitesse (rad/s)')
    axes[3].plot(temps,y-x[0],color='#9333ea',linewidth=1)
    pas=2*np.pi/p.L
    for borne in (-pas/2,pas/2): axes[3].axhline(borne,color='#64748b',linestyle='--',linewidth=1)
    axes[3].set_ylabel('Erreur codeur (rad)'); axes[3].set_xlabel('Temps (s)')
    fig.suptitle('Moteur à courant continu · commande, état et mesure',fontsize=15)
    fig.savefig(figures/'simulation.png',dpi=170);plt.close(fig)
    erreur_figure=.05 if .05 in erreurs else erreurs[-1]
    noms_figures=[]
    for index,T in enumerate(Ts):
        fig, axes=plt.subplots(2,len(qs),figsize=(4*len(qs),7),sharex=True,sharey='row',squeeze=False)
        for j,q in enumerate(qs):
            _,x,y,estimations=resultats[T,erreur_figure,q]
            for i in range(2):
                for nom,xe in estimations.items():
                    axes[i,j].plot(temps,xe[i]-x[i],label=nom,color=couleurs[nom],linestyle=styles[nom],linewidth=1.2,alpha=.88)
                axes[i,j].set_yscale('symlog',linthresh=1e-4 if i==0 else 1e-3)
                axes[i,j].axhline(0,color='#64748b',linewidth=.6)
            axes[0,j].set_title(f'q = {q:g} V²')
            axes[1,j].set_xlabel('Temps (s)')
        axes[0,0].set_ylabel('Erreur de position (rad)')
        axes[1,0].set_ylabel('Erreur de vitesse (rad/s)')
        fig.suptitle(f'Comparaison des filtres · T réel = {p.T_exact*1000:g} ms, T filtre = {T*1000:g} ms\nÉcart initial = {erreur_figure:+g} rad · erreurs signées en échelle symlog',fontsize=14)
        handles,labels=axes[0,0].get_legend_handles_labels()
        fig.legend(handles,labels,loc='lower center',ncol=5,frameon=False)
        fig.tight_layout(rect=(0,.06,1,.89))
        name=f'erreurs_T{T*1000:g}ms.png'
        fig.savefig(figures/name,dpi=160);plt.close(fig)
        noms_figures.append((T,name))
    with (docs/'resultats.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    versions={name:version(name) for name in ('numpy','scipy','matplotlib','filterpy')}
    (root/'python/requirements.txt').write_text(''.join(f'{name}=={v}\n' for name,v in versions.items()),encoding='utf-8')
    with (docs/'environnement.txt').open('w',encoding='utf-8') as stream:
        stream.write(f'Python {sys.version.split()[0]}\n')
        stream.write(''.join(f'{name}=={v}\n' for name,v in versions.items()))
        stream.write(f'Particules={args.particules}; seed=42\n')
    table=['| T filtre | q (V²) | Filtre | RMSE position (rad) | RMSE vitesse (rad/s) |','| --- | ---: | --- | ---: | ---: |']
    qs_table=[q for q in qs if q in (0.,1e-4,1e-2)] or qs
    for row in rows:
        if row['erreur_initiale_rad']==erreur_figure and row['q_V2'] in qs_table and row['filtre'] in ('Kalman','Stationnaire','Particulaire'):
            table.append(f"| {row['T_filtre_s']*1000:g} ms | {row['q_V2']:g} | {row['filtre']} | {row['rmse_position_rad']:.4g} | {row['rmse_vitesse_rad_s']:.4g} |")
    figures_md='\n\n'.join(f"### T filtre = {T*1000:g} ms\n\n![Erreurs des cinq filtres avec T filtre égal à {T*1000:g} ms](docs/figures/{name})" for T,name in noms_figures)
    quantif=float(np.max(np.abs(y-x[0])))
    readme=f'''# State Estimation · Kalman to Particle Filters

**Estimer la position et la vitesse d’un moteur à courant continu à partir de sa commande et d’un codeur angulaire.**

Projet Python autour du TP MSTAT DataSIM : Kalman optimal, Kalman stationnaire, EKF, UKF et filtre particulaire bootstrap. Les cinq méthodes sont appliquées au **même moteur**, avec les mêmes mesures et conditions initiales.

> Le moteur étudié est linéaire : EKF et UKF servent ici à comparer les implémentations. Ils doivent retrouver Kalman, aux erreurs numériques près. Le modèle scalaire non linéaire proposé dans la partie 3 de l’énoncé n’est pas implémenté dans ce dépôt Python.

[Installation](#installation) · [Lancer les simulations](#lancer-les-simulations) · [Résultats](#résultats) · [Organisation](#organisation)

## Installation

Les commandes suivantes sont prévues pour un terminal Linux, depuis la racine du dépôt. Python 3 et son module `venv` sont nécessaires. Si `python3 -m venv` échoue sur Ubuntu/Debian, installer le paquet `python3-venv`.

```bash
cd State-Estimation-Kalman-to-Particle-Filters
python3 -m venv python/.venv
source python/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r python/requirements.txt
cd python
python comparaison.py --sans-affichage
```

Le dernier lancement affiche les RMSE et vérifie que les cinq filtres s’exécutent, sans ouvrir de fenêtres. Si tu es déjà à la racine du dépôt, commence directement à `python3 -m venv`.

Pour une session suivante, depuis la racine :

```bash
source python/.venv/bin/activate
cd python
python comparaison.py
```

Environnement ayant servi aux résultats ci-dessous : **Python {sys.version.split()[0]}**, NumPy {versions['numpy']}, SciPy {versions['scipy']}, Matplotlib {versions['matplotlib']}, FilterPy {versions['filterpy']}. Les versions sont enregistrées dans [requirements.txt](python/requirements.txt) et [environnement.txt](docs/environnement.txt). Les mêmes versions doivent disposer de distributions compatibles avec ton Python ; la référence testée est celle indiquée ici.

Dans VS Code, choisir `python/.venv/bin/python` comme interpréteur. Pour quitter l’environnement : `deactivate`.

## Lancer les simulations

Toutes ces commandes se lancent depuis `python/` avec l’environnement activé.

```bash
# Les cinq filtres avec les valeurs par défaut de parametres.py
python comparaison.py

# Ajouter commande, position quantifiée, vitesse et erreur du codeur
python comparaison.py --simulation

# Tous les scénarios : q, modèles exact/imprécis, erreurs initiales ±0,05 rad
python comparaison.py --tout

# Un cas choisi : T filtre en secondes, erreur de position en radians
python comparaison.py --q 0.0001 --t-filtre 0.025 --erreur -0.05

# Calcul sans interface graphique
python comparaison.py --tout --sans-affichage

# Essai plus rapide du bootstrap, avec davantage d'erreur Monte-Carlo
python comparaison.py --particules 2000 --sans-affichage

# Liste des options
python comparaison.py --help
```

| Option | Rôle |
| --- | --- |
| `--q` | Variance supposée du bruit sur la tension d’entrée, en V² ; défaut : `p.q` |
| `--t-filtre` | Constante de temps du modèle utilisé par les filtres, en secondes ; défaut : `p.T` |
| `--erreur` | Position estimée initiale moins position réelle ; défaut : +0,05 rad |
| `--particules` | Nombre de particules ; défaut : 20 000 |
| `--tout` | Utilise `q_tests`, `T_filtres` et `erreurs_initiales` de `parametres.py` ; remplace les scénarios unitaires |
| `--simulation` | Ajoute les graphiques du simulateur |
| `--sans-affichage` | Affiche uniquement les résultats numériques |

`plt.show()` attend la fermeture des fenêtres. Sur une machine sans affichage graphique, utiliser `--sans-affichage`. L’avertissement `FigureCanvasAgg is non-interactive` indique un moteur de rendu sans fenêtre ; sur un bureau Linux, installer si nécessaire le support Tk (`python3-tk` sur Ubuntu/Debian) et essayer `MPLBACKEND=TkAgg python comparaison.py`.

## Modèle et hypothèses

L’état est la position et la vitesse :

```text
X_k = [theta_k, Omega_k]^T

X_(k+1) = F X_k + B_d (u_k + v_k)
y_k     = H X_k + w_k
```

La discrétisation est exacte lorsque la tension est constante sur une période d’échantillonnage. Avec $a=e^{{-T_e/T}}$ :

```text
    [ 1   T(1-a) ]          [ G[Te - T(1-a)] ]
F = [            ]    B_d = [               ]    H = [1  0]
    [ 0      a   ]          [    G(1-a)     ]
```

Ici, `theta` désigne la position angulaire et `Omega` la vitesse ; `Te` est la période d’échantillonnage.

| Paramètre réel | Valeur actuelle |
| --- | ---: |
| Gain $G$ | {p.G_exact:g} rad·s⁻¹·V⁻¹ |
| Constante de temps $T$ | {p.T_exact*1000:g} ms |
| Échantillonnage $T_e$ | {p.Te*1000:g} ms |
| Durée | {p.D:g} s |
| Créneau | {p.Acc:g} V crête à crête ; période {p.delta*1000:g} ms |
| Codeur | {p.L} valeurs par tour |
| État initial réel | position {p.x1[0]:g} rad ; vitesse {p.x1[1]:g} rad/s |

Le codeur arrondit la position au multiple de $\\Delta\\theta=2\\pi/L$ le plus proche. Son erreur est approximée par une loi uniforme sur un demi-pas de chaque côté, d’où $r=\\Delta\\theta^2/12$ et $R=[r]$. L’incertitude sur l’entrée donne **$Q=qB_dB_d^\\top$**, une matrice 2×2 : `q` et `Q` ne sont pas interchangeables.

**Dans ces expériences, `q` règle les filtres ; aucun bruit d’entrée aléatoire n’est ajouté au simulateur.** Les mesures sont issues de la quantification. Le bootstrap utilise une vraisemblance gaussienne approchée de variance `r`, pour comparer les méthodes sous la même approximation de bruit.

La vitesse initiale est connue nulle. La position initiale est inconnue pour les filtres : la comparaison impose un écart de ±0,05 rad et utilise `P_(1/0) = diag(M, 0)`, avec $M=(2\\pi)^2$ dans les paramètres actuels. Le premier échantillon est traité par une correction, sans prédiction préalable.

## Résultats

Les figures et les chiffres suivants sont **calculés avec le code du dépôt**, sur {len(u)} échantillons et {args.particules:,} particules (graine 42). Le CSV contient les {len(Ts)*len(erreurs)*len(qs)} scénarios, y compris les deux signes d’erreur initiale.

### Simulation et quantification

![Commande du moteur, position réelle et quantifiée, vitesse et erreur du codeur](docs/figures/simulation.png)

L’erreur maximale de quantification observée vaut **{quantif:.6g} rad**, pour un demi-pas de **{pas/2:.6g} rad**. Les lignes pointillées du dernier graphique indiquent cette borne.

### Effet du modèle et du réglage q

Les figures ci-dessous prennent un écart initial de **{erreur_figure:+g} rad**. Les erreurs sont signées : estimation moins état réel. Une échelle **symlog** conserve le signe et permet de voir simultanément les pics et les petites erreurs ; elle devient linéaire autour de zéro (seuils : 10⁻⁴ rad et 10⁻³ rad/s).

{figures_md}

- **Modèle exact, q nul :** Kalman corrige l’erreur initiale de position. Le gain stationnaire limite est nul : le stationnaire conserve le décalage initial. La vitesse est reconstruite exactement avec le modèle et sa condition initiale connue.
- **Modèle imprécis :** avec T filtre = 25 ms au lieu de 20 ms, un faible `q` laisse apparaître des erreurs périodiques liées au modèle. Augmenter `q` donne davantage de poids aux mesures et peut mieux compenser cette erreur.
- **q élevé :** la correction est plus réactive, mais la quantification se répercute davantage sur l’estimation, notamment sur la vitesse. Le stationnaire peut présenter un pic au démarrage car il ne tient pas compte de l’incertitude initiale dans son gain.
- **EKF et UKF :** leurs courbes se superposent à Kalman sur ce moteur linéaire. Écarts maximaux observés sur l’ensemble des scénarios : EKF/Kalman **{ecart_ekf:.3g}**, UKF/Kalman **{ecart_ukf:.3g}** (composantes position et vitesse réunies, dans leurs unités respectives).
- **Bootstrap :** il approche le filtrage par un ensemble fini de particules. Le nombre de particules, le rééchantillonnage et la graine influencent les résultats. Le cas `q=0` est sensible à l’appauvrissement des particules.

### Quelques RMSE

Écart initial de {erreur_figure:+g} rad. La RMSE est calculée **sur toute la simulation, démarrage inclus** : elle ne décrit pas seulement le régime établi. EKF et UKF sont omis de ce tableau car leurs valeurs coïncident avec Kalman à la précision affichée.

{chr(10).join(table)}

[Consulter tous les résultats numériques (CSV)](docs/resultats.csv). Ces résultats décrivent les scénarios et le réglage testés ; ils ne constituent pas un classement universel des filtres.

## Organisation

```text
.
├── README.md
├── tp-mstat-2627.pdf          # énoncé du TP
├── matlab/                   # scripts MATLAB existants
├── python/
│   ├── parametres.py         # paramètres physiques et scénarios
│   ├── modele_moteur.py      # commande, matrices exactes, simulateur
│   ├── filtre_kalman.py      # gain variable, FilterPy
│   ├── filtre_stationnaire.py # gain constant, Riccati
│   ├── filtre_ekf.py         # Jacobiennes du moteur
│   ├── filtre_ukf.py         # points sigma
│   ├── filtre_particulaire.py # bootstrap
│   ├── comparaison.py       # point d’entrée commun
│   └── requirements.txt
└── docs/
    ├── figures/              # images du README
    ├── resultats.csv
    ├── environnement.txt
    └── generer_resultats.py   # régénération de cette documentation
```

Chaque filtre expose `estimer(y, u, F, B, H, Q, R, x0, P0)` ; le bootstrap accepte aussi `nombre` et `seed`. Les états estimés sont stockés sous forme **(2, N)**, position puis vitesse. Utiliser `xe.T` pour obtenir les deux colonnes **(N, 2)** demandées par l’énoncé. Le simulateur renvoie `x` de forme `(2, N)` et `y` de forme `(N,)`.

## Régénérer ce README et ses figures

Depuis la racine du dépôt, avec l’environnement installé :

```bash
source python/.venv/bin/activate
python docs/generer_resultats.py
```

Cette commande recalcule les scénarios, exporte les images et le CSV, relève les versions installées dans `python/requirements.txt`, puis remplace le README. Elle utilise le rendu sans fenêtre et laisse les fichiers de filtres et leurs commentaires intacts. Pour un aperçu plus rapide : `python docs/generer_resultats.py --particules 2000` ; le nombre réellement utilisé sera indiqué dans les nouveaux résultats.

## Inspiration et remerciements

Nous nous sommes beaucoup inspirés du dépôt [Kalman and Bayesian Filters in Python](https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python) de Roger R. Labbe Jr. pour comprendre les méthodes de filtrage et construire nos implémentations. Ses explications et exemples nous ont servi de référence pour les filtres de Kalman, l’EKF, l’UKF et le filtrage particulaire, que nous appliquons ici au modèle de moteur du TP MSTAT.

## Références

- [Énoncé MSTAT 2026–2027](tp-mstat-2627.pdf), §2.1 à §2.4 pour le moteur et les comparaisons de Kalman.
- [FilterPy — Kalman](https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html), [EKF](https://filterpy.readthedocs.io/en/latest/kalman/ExtendedKalmanFilter.html), [UKF](https://filterpy.readthedocs.io/en/latest/kalman/UnscentedKalmanFilter.html).
- [SciPy — équation de Riccati discrète](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_discrete_are.html).
'''
    (root/'README.md').write_text(readme,encoding='utf-8')
    source=Path(__file__).read_text(encoding='utf-8')
    (docs/'generer_resultats.py').write_text(source,encoding='utf-8')
    print(f'README, {1+len(Ts)} figures et {len(rows)} lignes de résultats générés dans {root}',flush=True)


if __name__=='__main__':
    main()
