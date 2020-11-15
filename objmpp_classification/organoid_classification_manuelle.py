"""Written by Jérôme Emonet"""

from objmpp_classification.main.seg_orga_watershed import *
from objmpp_classification.main.classification_organoides import *
from objmpp_classification.main.traitements_objet import *
import pickle
import re


def organoid_classification_manuelle(path_data, path_images, debug=False):
	"""Run Organoid classification from obj.MPP output"""

	#Initialisation.
	# path_data = input("Entrez le chemin du dossier contenant les données à traiter : ")
	# path_images = input("Entrez le chemin du dossier contenant les images d'origines : ")
	# path_data = "/home/jerome/Stage_Classif_Organoid/Result_MPP/Organoïd/images-organoides"
	# path_images = "/home/jerome/Stage_Classif_Organoid/Image_Organoïdes/07012020-UBTD1-video"

	list_folder = [f for f in listdir(path_data) if "" == splitext(f)[1]]

	regexp_name = re.compile(r'(.*_.*)_(.*)')

	#Itérations sur chaque dossier/image.
	for objmpp_folder in list_folder:
		path_img_folder = path_data+"/"+objmpp_folder
		list_ref = [splitext(ref_img)[0] for ref_img in listdir(path_img_folder) if "All_ells_erod" in ref_img]
		for ref in list_ref:
			#Récupération du nom et de l'id de l'image en cours.
			name_img = ref.replace(f"All_ells_erod_","")
			name_img = re.sub(regexp_name,r'\1.\2',name_img)

			#Récupération des chemins requis pour la suite.
			#Vérification des fichiers.
			#Ajouter des blocs if/raise pour chaque élément afin de vérifier qu'ils existent et sinon envoyer une erreur explicite.
			files_id = [f for f in listdir(path_img_folder)]
			for f in files_id:
				if "All_ells_erod" in f:
					path_all_ells_erod = path_img_folder + "/" + f
				elif "All_ells" in f:
					path_all_ells = path_img_folder + "/" + f
			path_img = path_images + "/" + name_img

			#Création des régions binarisées et érodées.
			#all_ell_erod = Erode_ellipses(path_img_folder)
			#all_ell = Binaryze_ellipses(path_region)
			all_ells_erod = plt.imread(path_all_ells_erod)
			all_ells = plt.imread(path_all_ells)
   
			#Segmentation Watershed.
			Path(path_img_folder+"/Watershed").mkdir(parents=True, exist_ok=True)
			watershed = Seq_Water_meth2(path_img,all_ells,all_ells_erod,path_img_folder+"/Watershed",10)

			#Séparation des objets watershed.
			Path(path_img_folder+"/local_map_watershed").mkdir(parents=True, exist_ok=True)
			list_regions_obj = Separate_ellipses(watershed,path_csv)
			file_list_regions_obj = open(path_img_folder+"/local_map_watershed/Liste_regions_objets.txt","wb")
			pickle.Pickler(file_list_regions_obj).dump(list_regions_obj)
			file_list_regions_obj.close()

			#Transformation des objets en map des distance.
			list_dm_obj = Distance_map(path_img_folder+"/local_map_watershed",list_regions_obj)
			file_list_dm_obj = open(path_img_folder+"/local_map_watershed/Liste_dist_map_objets.txt","wb")
			pickle.Pickler(file_list_dm_obj).dump(list_dm_obj)
			file_list_dm_obj.close()
			
			#Classification des organoïdes.
			intensity_profiling(list_dm_obj,path_img_folder,path_csv,path_img,path_ellipse,20)
			
				
		#depickler = pickle.Unpickler(file).load()

		#np_img = np.array(Image.open(path_img))
		#Image.fromarray(watershed).save("/home/jerome/Bureau/Test/watershed.TIF")  

			

	    
	    


	    
