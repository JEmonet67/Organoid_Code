"""Written by Jérôme Emonet"""

from Main.SegOrgaWatershed import *
from Main.Classification_organoides import *
from Main.Traitements_objet import *
import pickle
import re
import click

@click.command()
@click.argument('path_data')
@click.argument('path_images')
@click.option('--debug', is_flag=True, help="Will print verbose messages.")
def organoid_classification(path_data, path_images, debug=False):

	#Initialisation.
	# path_data = input("Entrez le chemin du dossier contenant les données à traiter : ")
	# path_images = input("Entrez le chemin du dossier contenant les images d'origines : ")
	# path_data = "/home/jerome/Stage_Classif_Organoid/Result_MPP/Organoïd/images-organoides"
	# path_images = "/home/jerome/Stage_Classif_Organoid/Image_Organoïdes/07012020-UBTD1-video"

	list_folder = [f for f in listdir(path_data) if "" == splitext(f)[1]]

	regexp_id = re.compile(r'[0-9]{4}y([0-9]{2}[mdhs]){5}[0-9]{3}l')
	regexp_name = re.compile(r'(.*_.*)_(.*)')

	#Itérations sur chaque dossier/image.
	for objmpp_folder in list_folder:
	    path_folder = path_data+"/"+objmpp_folder
	    list_localmap = [folder_lm for folder_lm in listdir(path_folder) if "local_map" in folder_lm]
	    for folder in list_localmap:
		#Récupération du nom et de l'id de l'image en cours.
		id_image = regexp_id.search(folder).group(0)
		name_img = folder.replace("local_map_","").replace(f"_{id_image}","")
		name_img = re.sub(regexp_name,r'\1.\2',name_img)

		#Récupération des chemins requis pour la suite.
		#Vérification des fichiers.
		#Ajouter des blocs if/raise pour chaque élément afin de vérifier qu'ils existent et sinon envoyer une erreur explicite.
		files_id = [f for f in listdir(path_folder) if id_image in f]
		for f in files_id:
		    if "local_map" in f:
		        path_local_map = path_folder + "/" + f
		    elif "region" in f:
		        path_region = path_folder + "/" + f
		    elif "marks" in f:
		        path_csv = path_folder + "/" + f
		    elif "ellipse" in f:
		        path_ellipse = path_folder + "/" + f
		path_img = path_images + "/" + name_img

		#Création des régions binarisées et érodées.
		all_ell_erod = Erode_ellipses(path_local_map)
		all_ell = Binaryze_ellipses(path_region)
		
		#Segmentation Watershed.
		Path(path_local_map+"/Watershed").mkdir(parents=True, exist_ok=True)
		watershed = Seq_Water_meth2(path_img,all_ell,all_ell_erod,path_local_map+"/Watershed",10)

		#Séparation des objets watershed.
		Path(path_local_map+"/local_map_watershed").mkdir(parents=True, exist_ok=True)
		list_regions_obj = Separate_ellipses(watershed,path_csv)
		file_list_regions_obj = open(path_local_map+"/local_map_watershed/Liste_regions_objets.txt","wb")
		pickle.Pickler(file_list_regions_obj).dump(list_regions_obj)
		file_list_regions_obj.close()

		#Transformation des objets en map des distance.
		list_dm_obj = Distance_map(path_local_map+"/local_map_watershed",list_regions_obj)
		file_list_dm_obj = open(path_local_map+"/local_map_watershed/Liste_dist_map_objets.txt","wb")
		pickle.Pickler(file_list_dm_obj).dump(list_dm_obj)
		file_list_dm_obj.close()
		
		#Classification des organoïdes.
		intensity_profiling(list_dm_obj,path_local_map,path_csv,path_img,path_ellipse,20)
		
		    

	    #depickler = pickle.Unpickler(file).load()

	    #np_img = np.array(Image.open(path_img))
	    #Image.fromarray(watershed).save("/home/jerome/Bureau/Test/watershed.TIF")  

	    
	    
	    
	    


	    