#!/home/jerome/anaconda3/bin/python3

#Importation des modules.
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("seaborn-whitegrid")
import pandas as pd
import imageio as io
from skimage import img_as_ubyte
from decimal import Decimal
import cv2 as cv

def intensity_profiling(path_file,path_csv,path_image,path_glob_ells,k):
    print("Début de l'algorithme.")
    
    #Création du répertoire parent de stockage des résultats.
    output_path_analyze = f"{path_file}/Local_Map_Analyze"
    Path(output_path_analyze).mkdir(parents=True, exist_ok=True)
    
    #Importation des coordonnées des ellipses depuis le fichier csv.
    df_marks = pd.read_csv(path_csv)
    list_center_x = df_marks["Center Col"]
    list_center_y = df_marks["Center Row"]
    list_maj_axis = df_marks["Semi Major Axis"]
    
    #Ouverture des fichiers.
    file_info = open(f"{output_path_analyze}/Informations.txt","w")
    file_resultats = open(f"{output_path_analyze}/Resultats.txt","w")
    file_comparaison = open(f"{output_path_analyze}/Test_classif.txt","w")
    
    img_global = plt.imread(path_image)
    img_glob_ells = plt.imread(path_glob_ells)
    
    #Création de la figure ellipse all.
    fig_all = plt.figure()
    ax_all = plt.axes()
    plt.title(label="Intensité moyenne en fonction de la distance de toutes les ellipses")
    ax_all = ax_all.set(xlabel = "Distance au centre (%)",
                ylabel = "Intensité moyenne des pixels")
    
    #Initialisation.
    n = len(list_center_x)
    n_img = 1
    # list_compact = [2,5,6,8,9,13,17]
    # list_cystique = [1,3,4,7,14,18,27,30,34,39]
    # list_dechet = [10,11,12,15,16,19,20,21,22,23,24,25,26,28,29,31,32,33,35,36,37,38,40,41,42]
    n_cystique = 0
    n_compact = 0
    n_dechet = 0
    # list_organoid = []
    compact = {}
    cystique = {}
    dechet = {}
    (compact["taille"],compact["contour"],compact["max_intensity"],compact["max_indice"],
    compact["mean_intensity"],compact["rapp_taille_perim"],compact["mean_creux"],compact["seuil"]) = ([],[],[],[],
                                                                                                      [],[],[],[])
    (cystique["taille"],cystique["contour"],cystique["max_intensity"],cystique["max_indice"],
    cystique["mean_intensity"],cystique["rapp_taille_perim"],cystique["mean_creux"],cystique["seuil"]) = ([],[],[],[],
                                                                                                      [],[],[],[])
    (dechet["taille"],dechet["contour"],dechet["max_intensity"],dechet["max_indice"],
    dechet["mean_intensity"],dechet["rapp_taille_perim"],dechet["mean_creux"],dechet["seuil"]) = ([],[],[],[],
                                                                                                      [],[],[],[])
    
    # compact["taille"] = compact["contour"] = compact["max_intensity"] = compact["max_indice"] = []
    # compact["mean_intensity"] = compact["rapp_taille_perim"] = compact["mean_creux"] = compact["seuil"] = []
    # cystique["taille"] = cystique["contour"] = cystique["max_intensity"] = cystique["max_indice"] = []
    # cystique["mean_intensity"] = cystique["rapp_taille_perim"] = cystique["mean_creux"] = cystique["seuil"] = []
    # dechet["taille"] = dechet["contour"] = dechet["max_intensity"] = dechet["max_indice"] = []
    # dechet["mean_intensity"] = dechet["rapp_taille_perim"] = dechet["mean_creux"] = dechet["seuil"] = []

    #Début des itérations sur les images.
    while n_img <= n:
        print("Ellipse numéro", n_img, "en cours de traitement.")
        img_ellipse = np.load(f"{path_file}/local_map_{n_img}.npy")
        max_img = np.max(img_ellipse)
        
        #Création de la liste des niveaux.
        list_Niveau = [0]
        i_Niveau = 1
        while len(list_Niveau) <= k:
            Niveau = round(max_img/k*i_Niveau,5)
            list_Niveau += [Niveau]
            # if Niveau < 1:
            #     list_Niveau += [Niveau] + [Niveau + 1]
            # else:
            #     list_Niveau += [Niveau]
            i_Niveau+=1

        #Mise en place des coordonnées.
        center_x = list_center_x[n_img-1]
        center_y = list_center_y[n_img-1]
        maj_axis = int(round(list_maj_axis[n_img-1]))

        bord_gauche = (center_x-maj_axis)
        bord_droit = (center_x+maj_axis) 
        bord_haut = (center_y-maj_axis)
        bord_bas = (center_y+maj_axis)
        
        if bord_gauche < 0:
            bord_gauche = 0
        if bord_haut < 0:
            bord_haut = 0
        if bord_droit > img_ellipse.shape[0]-1:
            bord_droit = img_ellipse.shape[0]-1
        if bord_bas > img_ellipse.shape[1]-1:
            bord_bas = img_ellipse.shape[1]-1
        
        coordonnees = [bord_gauche,bord_droit,bord_haut,bord_bas]
        
        
        #Création et sauvegarde des images locales de la carte des distances et de l'image d'origine.
        img_ell_locale = img_ellipse[coordonnees[2]:coordonnees[3],
                                     coordonnees[0]:coordonnees[1]]
        img_glob_locale = img_global[coordonnees[2]:coordonnees[3],
                                     coordonnees[0]:coordonnees[1]]
        img_glob_ells_locale = img_glob_ells[coordonnees[2]:coordonnees[3],
                                     coordonnees[0]:coordonnees[1]]
        
        
        #Début du parcours de l'ellipse en cours.
        list_somme = [0] * k
        list_count = [0] * k
        for i in range(0,img_ell_locale.shape[0]):
            for j in range(0,img_ell_locale.shape[1]):
                value_distmap = round(img_ell_locale[i,j],5)
                if value_distmap > 0:
                    i_discretisation = 0
                    Found = False
                    while i_discretisation < len(list_Niveau)-1 and Found == False:
                        if (value_distmap > list_Niveau[i_discretisation] 
                        and value_distmap <= list_Niveau[i_discretisation+1]):
                            list_count[i_discretisation] += 1
                            list_somme[i_discretisation] += img_glob_locale[i,j]
                            Found = True
                        i_discretisation += 1
        
        
        #Calcul de la liste des moyennes de l'ellipse en cours.
        i_mean = 0
        list_mean = []
        k_cut = k
        while i_mean < k:
            try:
                list_mean += [round(list_somme[i_mean]/list_count[i_mean],2)]
                i_mean += 1
            except ZeroDivisionError:
                i_mean += 1
                k_cut -= 1
                print("Division 0,", i_mean)
        list_mean.reverse()
        
        
        #Création du seuil d'égalité entre l'intégrale des courbes avant/après.
        ratio = 1/k_cut
        seuil, diff_seuil = Seuillage(list_mean,ratio)
        
        x = list(frange(Decimal(ratio),Decimal(1+ratio),ratio))
        
        #Calcul des paramètres de l'ellipse.
        taille = sum(list_count)
        contour = make_contour(img_ellipse)
        rapp_taille_perim = taille/(contour**2)
        max_intensity = max(list_mean)
        max_indice = x[list_mean.index(max_intensity)]
        mean_intensity = np.mean(list_mean)

        
        
        #Calcul du creux des ellipses.
        borne80 = int(len(x) * 0.8)
        list_mean_0_80 = list_mean[:borne80]
        mean_0_80 = np.mean(list_mean_0_80)
        
        #Classification des organoïdes par leur paramètres.
        if mean_intensity > 90:
            type_organoid = "Compact"
            n_compact += 1
        elif max_indice >= 0.8 and contour >=  1100 and seuil >= 0.55:
            type_organoid = "Cystique"
            n_cystique += 1
        else:
            type_organoid = "Déchet"
            n_dechet += 1
        #list_organoid += [type_organoid]
        
        #Somme des paramètres de chaque organoïdes selon leur type.
        if type_organoid == "Compact":
            compact["taille"] += [taille]
            compact["contour"] += [contour]
            compact["rapp_taille_perim"] += [rapp_taille_perim]
            compact["max_intensity"] += [max_intensity]
            compact["max_indice"] += [max_indice]
            compact["mean_intensity"] += [mean_intensity]
            compact["mean_creux"] += [mean_0_80]
            compact["seuil"] += [seuil]
        elif type_organoid == "Cystique":
            cystique["taille"] += [taille]
            cystique["contour"] += [contour]
            cystique["rapp_taille_perim"] += [rapp_taille_perim]
            cystique["max_intensity"] += [max_intensity]
            cystique["max_indice"] += [max_indice]
            cystique["mean_intensity"] += [mean_intensity]
            cystique["mean_creux"] += [mean_0_80]
            cystique["seuil"] += [seuil]
        elif type_organoid == "Déchet":
            dechet["taille"] += [taille]
            dechet["contour"] += [contour]
            dechet["rapp_taille_perim"] += [rapp_taille_perim]
            dechet["max_intensity"] += [max_intensity]
            dechet["max_indice"] += [max_indice]
            dechet["mean_intensity"] += [mean_intensity]
            dechet["mean_creux"] += [mean_0_80]
            dechet["seuil"] += [seuil]

        
        #Création du graphique de l'ellipse en cours.
        #Bloc if permettant de pallier au fait que parfois une valeur très proche de 100 en trop
        #au lieu d'égal à 100 à cause de l'imprécision est ajoutée à  x.
        if len(x) > len(list_mean):
            x = x[:-1]
        fig_ell = plt.figure()
        ax_ell = plt.axes()
        plt.title(f"""Intensité moyenne en fonction de la
                  distance dans l'ellipse {n_img}""")
        ax_ell = ax_ell.set(xlabel = "Distance au centre (%)",
                    ylabel = "Intensité moyenne des pixels")
        plt.plot(x, list_mean)
        plt.vlines(seuil,0,200,
                   colors="r",linestyles="dashed")
        
        
        #Bloc de code uniquement pour le test des exemples déjà classifiés.
        fig_ell.savefig(f"{output_path_analyze}/{type_organoid}_graphic_ellipse_{n_img}.png")
        plt.close()
        #Ajout de la courbe de l'ellipse en cours dans le graphique contenant toutes les ellipses.
        plt.plot(x, list_mean)
        #Sauvegarde des images locales de l'organoïde et de la carte des distance.
        io.imwrite(f"{path_file}/Local_Map_Analyze/{type_organoid}_Image_locale_{n_img}.png",(img_ell_locale))
        io.imwrite(f"{path_file}/Local_Map_Analyze/{type_organoid}_Global_Image_locale_{n_img}.png",img_as_ubyte(img_glob_ells_locale))
        
        
        #Ecriture des niveaux discrétisés de chaque ellipse dans le fichier d'info.
        file_info.write(f"\t ---------   Ellipse numéro {n_img} {type_organoid} --------- \n \n"
                        + f"""Liste des niveau discrétisés ellipse : {k} \n \n"""
                        + f"""Liste des bornes des intervalles de niveau ({len(list_Niveau)}) : \n {list_Niveau} \n \n""")
        
        #Ecriture des coordonnées dans le fichier Information.txt.
        file_info.write(f"""\t Center ({center_x}, {center_y})  Major Axis ({maj_axis}) \n"""
                        + f"""\t Coord box x = {coordonnees[0]} et {coordonnees[1]}. \n"""
                        + f"""\t Coord box y = {coordonnees[2]} et {coordonnees[3]}. \n \n""")
        
        #Ecriture des caractéristiques des profils de niveaux dans le fichier d'info.
        file_info.write(f"""Liste des sommes des intensités par niveau  : {len(list_somme)} éléments. 
                        \n {list_somme} \n \n"""
                        + f"""Liste des nombre de pixels par niveau : {len(list_count)} éléments. 
                        \n {list_count} \n \n"""
                        + f"""Liste des moyennes d'intensité par niveau : {len(list_mean)} éléments. 
                        \n {list_mean} \n \n \n""")

        
        #Ecriture des résultats de l'ellipse en cours.
        file_resultats.write(f"\t ---------   Ellipse numéro {n_img} {type_organoid} --------- \n \n"
                            + f""" Taille de l'ellipse (nb de pixels) : {taille} \n"""
                            + f""" Longueur du périmètre de l'ellipse : {contour} \n"""
                            + f""" Rapport taille/périmètre² : {rapp_taille_perim} \n"""
                            + f""" Maximum du profil d'intensité de l'ellipse : {max_intensity} \n"""
                            + f""" Indice du maximum du profil d'intensité de l'ellipse : {max_indice} \n"""
                            + f""" Moyenne du profil d'intensité de l'ellipse : {round(mean_intensity,3)} \n"""
                            + f""" Moyenne du creux de l'ellipse (0-80) : {round(mean_0_80,3)} \n \n"""
                            + f""" Seuil = {round(seuil,3)} \t Différence au seuil = {round(diff_seuil,3)} \n \n""")
        
        
        
        n_img += 1

    # list_organoid_exemple = []
    # for n in range(1,43):
    #         if n in list_compact:
    #             list_organoid_exemple += ["Compact"]
    #         elif n in list_cystique:
    #             list_organoid_exemple += ["Cystique"]
    #         elif n in list_dechet:
    #             list_organoid_exemple += ["Déchet"]

    # #Ecriture fichier comparaison.
    # file_comparaison.write(f"\t --------- Comparaisons des classifications --------- \n \n"
    #                         + f"Nombre cystique : Réel {len(list_cystique)} / Classifié {n_cystique} \n"
    #                         + f"Nombre compact : Réel {len(list_compact)} / Classifié {n_compact} \n"
    #                         + f"Nombre déchets : Réel {len(list_dechet)} / Classifié {n_dechet} \n \n")
    
    # i_organoid = 1
    # match = 0
    # for organoid in list_organoid:
    #     file_comparaison.write(f"Organoïde n°{i_organoid} : Réel {list_organoid_exemple[i_organoid-1]} / Classifié {organoid} \t")
    #     if list_organoid_exemple[i_organoid-1] == organoid:
    #         file_comparaison.write(f"--- MATCH \n")
    #         match += 1
    #     else:
    #         file_comparaison.write("--- NOT MATCH \n")
    #     i_organoid += 1
    
    # file_comparaison.write(f"\n Ratio de matching : {match} / {len(list_organoid)}"
    #                        +f" => {round(match/(len(list_organoid))*100,2)}%")
    
    
    #Sauvegarde du graphique contenant les courbes de toutes les ellipses.
    fig_all.savefig(f"{output_path_analyze}/Graphic_ellipse_all.png")
    
    #Fermeture des fichiers
    file_resultats.close()
    file_info.close()
    
    #Calcul des statistiques des ellipses de l'image.
    dict_mean, dict_std = statistiques(compact,cystique,dechet)
    
    #Ecriture du fichier excel des statistiques de l'image. 
    number = [n_compact,n_cystique,n_dechet]
    excel_writing(dict_mean, dict_std, number, path_file)
    
    

def statistiques(compact, cystique, dechet):
    dict_mean = {}
    dict_std = {}
    for key in compact:
        dict_mean[key] = [np.mean(compact[key]).round(3),np.mean(cystique[key]).round(3),np.mean(dechet[key]).round(3)]
        dict_std[key] = [np.std(compact[key]).round(3),np.std(cystique[key]).round(3),np.std(dechet[key]).round(3)]
    
    return dict_mean, dict_std
        

def excel_writing(dict_mean,dict_std, number, path_file):    
    list_result = [number, [], dict_mean["taille"],dict_std["taille"],dict_mean["contour"],dict_std["contour"],
                   dict_mean["rapp_taille_perim"],dict_std["rapp_taille_perim"], dict_mean["max_intensity"],
                   dict_std["max_intensity"], dict_mean["max_indice"], dict_std["max_indice"], dict_mean["mean_intensity"],
                   dict_std["mean_intensity"], dict_mean["mean_creux"], dict_std["mean_creux"], dict_mean["seuil"], 
                   dict_std["seuil"]]


    col = ["Compact","Cystique","Déchet"]
    
    ind_niv1 = ["Nombre d'organoïdes","","Taille","","Périmètre","",
            "Rapport taille/perim²","","Maximum du profil","","Indice du maximum du profil",
            "","Moyenne du profil","","Moyenne creux","","Seuil",""]
    ind_niv2 = ["Nombre","", "Moyenne", "Ecart-type", "Moyenne", "Ecart-type", "Moyenne", "Ecart-type", 
                "Moyenne", "Ecart-type","Moyenne", "Ecart-type", "Moyenne", "Ecart-type",
                "Moyenne", "Ecart-type", "Moyenne", "Ecart-type"]
    list_ind = [(niv1,niv2) for niv1,niv2 in zip(ind_niv1,ind_niv2)]
    ind = pd.MultiIndex.from_tuples(list_ind, names=["Paramètre","Statistique"])
    
    df_result = pd.DataFrame(list_result, columns = col, index = ind)
    df_result.to_csv(f"{path_file}/Local_Map_Analyze/Stats_Paramètres_organoïdes.csv",index=True)


def make_contour(img):
    img_bin = np.copy(img)
    img_bin[img_bin > 0] = 1
    img_laplacian = cv.Laplacian(img_bin,cv.CV_64F)
    img_laplacian = np.absolute(img_laplacian)
    img_laplacian = np.uint8(img_laplacian)
    img_laplacian[img_laplacian>0] = 1
    #io.imwrite(f"{path_file}/Test_contour/Image_laplacian_{n_img}.png",img_laplacian)
    
    return np.sum(img_laplacian)
    
    


def Coupage_courbes(list_mean):
    borne_80 = int(round(len(list_mean)*0.8))
    liste_80_100 = list_mean[borne_80:]
    max_local = max(liste_80_100)
    borne_sup = list_mean.index(max_local)
    
    return list_mean[:borne_sup]


def Seuillage(list_mean,ratio):
    list_diff = []
    list_seuil = list(frange(Decimal(ratio), Decimal(100+ratio), ratio))

    for i_seuil in range(1,len(list_mean)+1):
        sup_seuil = list_mean[i_seuil:]
        inf_seuil = list_mean[:i_seuil]
        diff_integral = round((sum(sup_seuil)-sum(inf_seuil)),2)
        list_diff += [diff_integral]
    
    min_diff = abs(list_diff[0])
    
    for diff in list_diff[1:]:
        if abs(diff) < min_diff:
            min_diff = diff
    
    Index_min = list_diff.index(min_diff)
    
    return round(list_seuil[Index_min],2), min_diff
        
        
def frange(start, stop, step):
    while start < stop:
        yield float(start)
        start += Decimal(step)


#Attributions des 4 variables nécessaires à la fonction (test).
path_file_t = "/home/jerome/Stage_Classif_Organoid/Result_MPP/Organoïd/Images_KO/local_map_UBTD1-03_w24-DAPI_TIF_2020y06m09d14h48m55s317l/Test_Results/Img_marker_watershed_segmentation/local_map"
path_csv_t = "/home/jerome/Stage_Classif_Organoid/Result_MPP/Organoïd/Images_KO/UBTD1-03_w24-DAPI_TIF-marks-2020y06m09d14h48m55s317l.csv"
path_image_t = "/home/jerome/Stage_Classif_Organoid/Image_Organoïdes/07012020-UBTD1-video/UBTD1-03_w24-DAPI.TIF"
path_glob_ells_t = "/home/jerome/Stage_Classif_Organoid/Result_MPP/Organoïd/Images_KO/UBTD1-03_w24-DAPI_TIF-ellipse-2020y06m09d14h48m55s317l.png"
k_t = 20

#Lancement de la fonction (test).
#intensity_profiling(path_file_t,path_csv_t,path_image_t,path_glob_ells_t,k_t)
