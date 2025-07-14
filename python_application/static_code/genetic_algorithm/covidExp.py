import sys, argparse, time, random, glob, os, gc, torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, List
from segment_anything import sam_model_registry, SamPredictor
from pymoo.core.problem import Problem
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.core.callback import Callback
import warnings
import nibabel as nib
from skimage.measure import regionprops

from python_application.generated_code.enumerations.DataType import DataType
from python_application.generated_code.enumerations.DeviceType import DeviceType
from python_application.generated_code.enumerations.FileFormatType import FileFormatType
from python_application.generated_code.enumerations.MetricType import MetricType
from python_application.generated_code.enumerations.ModelType import ModelType
from python_application.generated_code.enumerations.OptimizationAlgorithm import OptimizationAlgorithm
from python_application.generated_code.enumerations.PointType import PointType
from python_application.generated_code.model.BoundingBox import BoundingBox
from python_application.generated_code.model.Coordinates import Coordinates
from python_application.generated_code.model.Dataset import Dataset
from python_application.generated_code.model.Experiment import Experiment
from python_application.generated_code.model.FoundationModel import FoundationModel
from python_application.generated_code.model.MaxIterations import MaxIterations
from python_application.generated_code.model.Metric import Metric
from python_application.generated_code.model.NoImprovement import NoImprovement
from python_application.generated_code.model.OptimizationTask import OptimizationTask
from python_application.generated_code.model.PROBE import PROBE
from python_application.generated_code.model.Point import Point
from python_application.generated_code.model.PromptForImage import PromptForImage
from python_application.generated_code.model.Sample import Sample
from python_application.generated_code.model.State import State
from python_application.generated_code.model.Subset import Subset
from python_application.generated_code.model.TimeLimit import TimeLimit

# if warnings have been suppressed, they are now re-enabled
warnings.filterwarnings('default')


def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)


def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels == 1]
    neg_points = coords[labels == 0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white',
               linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white',
               linewidth=1.25)


def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0, 0, 0, 0), lw=2))


def compare_original_and_predicted_masks(
        original_mask: np.array, predicted_mask: np.array
) -> Tuple[float, float]:
    """
    Compares the original segmentation mask with the one predicted. Returns a
    tuple with the Jaccard index and the Dice coefficient.

    :param original_mask: original segmentation mask.
    :param predicted_mask: predicted segmentation mask.

    :return: Jaccard index and the Dice coefficient of the masks provided.
    """

    original_mask_transformed = np.squeeze(original_mask)
    original_mask_as_bool = original_mask_transformed != 0

    intersection = original_mask_as_bool * predicted_mask
    union = (original_mask_as_bool + predicted_mask) > 0

    jaccard = intersection.sum() / float(union.sum())
    dice = intersection.sum() * 2 / (original_mask_as_bool.sum() + predicted_mask.sum())

    return jaccard, dice


def compare_original_and_predicted_masks_mod_jaccard(
        original_mask_as_bool: np.array, predicted_mask: np.array
) -> float:
    intersection = original_mask_as_bool * predicted_mask
    union = (original_mask_as_bool + predicted_mask) > 0

    jaccard = intersection.sum() / float(union.sum())

    return jaccard


def compare_original_and_predicted_masks_mod_dice(original_mask_as_bool: np.array, predicted_mask: np.array) -> float:
    intersection = original_mask_as_bool * predicted_mask

    dice = intersection.sum() * 2 / (original_mask_as_bool.sum() + predicted_mask.sum())

    return dice


def find_bounding_box(mask):
    """
        Find the bounding box around every mask.
        """
    labels = np.unique(mask)

    print(labels)
    if labels.size > 1:
        print(f'Finding the bounding box around the mask.')
        mask = np.where(mask > 0, 1, mask)
        mask = mask.astype(np.int16)
        regions_properties = regionprops(mask)
        region_properties = regions_properties[0]
        bounding_box = region_properties.bbox
        print(bounding_box)
        return bounding_box
    else:
        print('There are no contours masks to work with.')


class samPoint(Problem):

    def __init__(self):
        limit = []
        cxl = min(input_box[0], input_box[2])
        cxu = max(input_box[0], input_box[2])
        cyl = min(input_box[1], input_box[3])
        cyu = max(input_box[1], input_box[3])
        super().__init__(n_var=len(coordinates),
                         n_obj=1,
                         xl=np.array([cxl, cyl, cxl, cyl, cxl, cyl]),
                         xu=np.array([cxu, cyu, cxu, cyu, cxu, cyu]))

    def _evaluate(self, x, out, *args, **kwargs):
        if obj == 'score':
            sco = [1]
        elif obj == 'jaccard':
            jac = [1]
        else:
            dic = [1]

        global maskG
        global scoreG
        for i in range(popSize):

            input_point = []
            for j in range(0, len(coordinates)):
                input_point.append(x[i, j])

            input_point = np.asarray(input_point)
            input_point = input_point.reshape(int(len(coordinates) / 2), 2)

            if multimask:
                masks, scores, _ = predictor.predict(point_coords=input_point, point_labels=input_label,
                                                     box=input_box[None, :], multimask_output=True)
                mask = masks[np.argmax(scores), :, :]
                score = np.max(scores)

            else:
                mask, score, _ = predictor.predict(point_coords=input_point, point_labels=input_label,
                                                   box=input_box[None, :], multimask_output=False)

            if obj == 'score':
                if -score < min(sco):
                    maskG = mask
                    scoreG = float(score)
                sco.append(-score)
            elif obj == 'jaccard':
                jaccard = compare_original_and_predicted_masks_mod_jaccard(original_mask_as_bool, mask)
                if -jaccard < min(jac):
                    maskG = mask
                    scoreG = float(score)
                jac.append(-jaccard)
            else:
                dice = compare_original_and_predicted_masks_mod_dice(original_mask_as_bool, mask)
                if -dice < min(dic):
                    maskG = mask
                    scoreG = float(score)
                dic.append(-dice)

        if obj == 'score':
            sco.pop(0)
            out["F"] = [sco]
        elif obj == 'jaccard':
            jac.pop(0)
            out["F"] = [jac]
        else:
            dic.pop(0)
            out["F"] = [dic]


class History_CallBack(Callback):

    def __init__(self) -> None:
        super().__init__()
        self.n_evals = []
        self.optF = []
        self.optX = []

    def notify(self, algorithm):
        self.n_evals.append(algorithm.evaluator.n_eval)
        # retrieve the optimum from the algorithm
        opt = algorithm.opt[0]

        self.optF.append(opt.get("F"))
        self.optX.append(opt.get("X"))


############################################################################################################################################################################################################################################
#       MAIN
############################################################################################################################################################################################################################################
total_start_time = time.time()

# Parameters

# Processing device
processing_device = DeviceType.NVIDIA

# Build datasets
datasets = [
    Dataset(
        name="Coronacases",
        description="Lung CT (Coronacases Dataset)",
        type=DataType.IMAGE,
        subset=[
            Subset(
                name="trainingSet",
                path="/home/carlosbc24/PycharmProjects/phd2_code/datasets/covid",
                dataFolderName="COVID-19-CT-Seg_20cases",
                labelsFolderName="Lung_Mask",
                sample=[
                    Sample(
                        filename="coronacases_001.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_002.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_003.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_004.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_005.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_006.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_007.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_008.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_009.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_010.nii.gz",
                        extension=FileFormatType.NIFTI
                    )                ]
            )        ]
    )]

# Build optimization tasks
optimization_task = [
    OptimizationTask(
        name="Genetic Algorithms",
        description="Tarea de optimización mediante el uso de algoritmos genéticos",
        algorithm=OptimizationAlgorithm.GENETIC,
        foundation_model=FoundationModel(
            name="vit_l",
            version=1.0,
            description="SAM ViT-L",
            checkpointFilepath="/home/carlosbc24/PycharmProjects/phd2_code/model_checkpoints/sam_vit_l_0b3195.pth",
            configuration="",
            type=ModelType.IMAGE_SEGMENTATION
        ),
        experiment=[
            Experiment(
                name="Experiment 1 - coronacases_001",
                initial_state=State(
                    description="Experiment 1 Initial State",
                    hasImproved=False,
                    prompt=PromptForImage(
                        bounding_box=[BoundingBox(min_coordinates=Coordinates(x=102, y=218), max_coordinates=Coordinates(x=400, y=437))],
                        point=[Point(type=PointType.POSITIVE, coordinates=Coordinates(x=347, y=325)), Point(type=PointType.POSITIVE, coordinates=Coordinates(x=166, y=327)), Point(type=PointType.NEGATIVE, coordinates=Coordinates(x=251, y=327))]
                    )
                ),
                stop_condition=[NoImprovement(), TimeLimit(minutesDuration=5.0), MaxIterations(numIterations=1000)],
                sample=Sample(
                    filename="coronacases_001.nii.gz",
                    extension=FileFormatType.NIFTI
                )
            )
,
            Experiment(
                name="Experiment 2 - coronacases_002",
                initial_state=State(
                    description="Experiment 1 Initial State",
                    hasImproved=False,
                    prompt=PromptForImage(
                        bounding_box=[BoundingBox(min_coordinates=Coordinates(x=102, y=218), max_coordinates=Coordinates(x=400, y=437))],
                        point=[Point(type=PointType.POSITIVE, coordinates=Coordinates(x=347, y=325)), Point(type=PointType.POSITIVE, coordinates=Coordinates(x=166, y=327)), Point(type=PointType.NEGATIVE, coordinates=Coordinates(x=251, y=327))]
                    )
                ),
                stop_condition=[NoImprovement()],
                sample=Sample(
                    filename="coronacases_002.nii.gz",
                    extension=FileFormatType.NIFTI
                )
            )
        ],
        optimization_metric=Metric(name="Sam Score as an optimization metric", type=MetricType.SAM_SCORE),
        performance_metric=[
            Metric(name="Jaccard Index", type=MetricType.JACCARD,
   ),
            Metric(name="Dice Coefficient", type=MetricType.DICE,
   ),
            Metric(name="SAM Score", type=MetricType.SAM_SCORE,
   )    ]
    )
,
    OptimizationTask(
        name="Swarm Algorithms",
        description="Tarea de optimización mediante el uso de algoritmos de enjambres (SWARM)",
        algorithm=OptimizationAlgorithm.PARTICLE_SWARM,
        foundation_model=FoundationModel(
            name="SAM 2 Large",
            version=2.0,
            description="MedSAM ViT-h",
            checkpointFilepath="/home/carlosbc24/PycharmProjects/phd2_code/model_checkpoints/sam2_hiera_l.pt",
            configuration="sam2_hiera_l.yaml",
            type=ModelType.IMAGE_SEGMENTATION
        ),
        experiment=[
            Experiment(
                name="Experiment 1 - coronacases_001",
                initial_state=State(
                    description="Experiment 1 Initial State",
                    hasImproved=False,
                    prompt=PromptForImage(
                        bounding_box=[BoundingBox(min_coordinates=Coordinates(x=102, y=218), max_coordinates=Coordinates(x=400, y=437))],
                        point=[Point(type=PointType.POSITIVE, coordinates=Coordinates(x=347, y=325)), Point(type=PointType.POSITIVE, coordinates=Coordinates(x=166, y=327)), Point(type=PointType.NEGATIVE, coordinates=Coordinates(x=251, y=327))]
                    )
                ),
                stop_condition=[NoImprovement(), TimeLimit(minutesDuration=5.0), MaxIterations(numIterations=1000)],
                sample=Sample(
                    filename="coronacases_001.nii.gz",
                    extension=FileFormatType.NIFTI
                )
            )
        ],
        optimization_metric=Metric(name="Sam Score as an optimization metric", type=MetricType.SAM_SCORE),
        performance_metric=[
            Metric(name="Jaccard Index", type=MetricType.JACCARD,
   ),
            Metric(name="Dice Coefficient", type=MetricType.DICE,
   ),
            Metric(name="SAM Score", type=MetricType.SAM_SCORE,
   )    ]
    )
]

# Build the PROBE instance
probe = PROBE(
    device=processing_device,
    dataset=datasets,
    optimization_task=optimization_task
)


# Add arguments with flags
# parser.add_argument('-i', '--images', required=True, help='Input images path')
# parser.add_argument('-d', '--dataset', required=True, choices=['corona', 'radio'], help= 'Select the dataset: corona (coronacases) or radio (radiopaedia)')
# parser.add_argument('-k', '--masks', required=True,  help='Manual masks path')
# parser.add_argument('-o', '--output', required=True,  help='Output files path. Be careful, files will be rewrited!')
# parser.add_argument('-c', '--checkpoint', required=True,  help='SAM Model Checkpoint file')
# parser.add_argument('-v', '--model', default='vit_h', choices=['vit_b', 'vit_l', 'vit_h'], help= 'Select the SAM model version. Default is vit_h')
# parser.add_argument('-f', '--objective', default='dice', choices=['dice', 'jaccard', 'score'], help= 'Select the objective function. Default is dice')
# parser.add_argument('-m', '--multimask', action='store_true', help='Multimask option on. Default is off')
# parser.add_argument('-s', '--stopping', default=None,  help='Stopping criterion in hh:mm:ss format. Default no limit')
# parser.add_argument('--seed', type=int, default=1, help='Seed for random numbers. Default is 1')

# Parse the command line arguments
# args = parser.parse_args()
# print (args)


if probe.dataset[0].subset[0].path and probe.dataset[0].subset[0].dataFolderName:
    path_images = Path(probe.dataset[0].subset[0].path + "/" + probe.dataset[0].subset[0].dataFolderName)
if probe.dataset[0].name:
    dataset = probe.dataset[0].name
if probe.dataset[0].subset[0].path and probe.dataset[0].subset[0].labelsFolderName:
    path_masks = Path(probe.dataset[0].subset[0].path + "/" + probe.dataset[0].subset[0].labelsFolderName)
if probe.optimization_task[0].foundation_model.checkpointFilepath:
    sam_checkpoint = probe.optimization_task[0].foundation_model.checkpointFilepath
if probe.optimization_task[0].foundation_model.name:
    model_type = probe.optimization_task[0].foundation_model.name
if probe.optimization_task[0].optimization_metric.name:
    obj = probe.optimization_task[0].optimization_metric.name

print("Input_images_path: ", path_images)
print("Dataset name: ", dataset)
print("Input masks path: ", path_masks)
outfiles_path = f"output/{probe.dataset[0].name}/{probe.optimization_task[0].name}"
print("Output files path: ", outfiles_path)
print("Checkpoint file: ", sam_checkpoint)
print("Model name: ", model_type)
print("Objective function: ", obj)
multimask = False
print("Multimask option: ", multimask)
stop = None
print("Stopping criterion: ", stop)
seed = 1
print("Seed: ", seed)

popSize = 100
random.seed(seed)

if dataset == "Coronacases":
    files = glob.glob(str(path_images) + '/coronacases_*.nii.gz')
    windowing = True
    outfile = outfiles_path + "/coronaExp.txt"
elif dataset == "Radiopaedia":
    files = glob.glob(str(path_images) + '/radiopaedia_*.nii.gz')
    windowing = False
    outfile = outfiles_path + "/radioExp.txt"

files.sort()

try:
    os.makedirs(outfiles_path, exist_ok=True)
except OSError:
    print("Directory %s cannot be created!!" % outfiles_path)

try:
    output = open(outfile, 'w')
except IOError:
    print("File %s cannot be created!!" % outfile)

output.write(
    "Image" + "\t" + "Objective (" + obj + ")" + "\t" + "Jaccard" + "\t" + "Dice" + "\t" + "Score" + "\t" + "Time (s)" + "\t" + "Coordinates" + "\n")

#Following values are not important, just to create the arrays...
coordinates = np.arange(6)
pos_coor = [4, 5, 6, 7]
neg_coor = [8, 9]

input_label = []
for i in range(int(len(pos_coor) / 2)):
    input_label.append(1)
for i in range(int(len(neg_coor) / 2)):
    input_label.append(0)
input_label = np.asarray(input_label)

#set SAM features
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

predictor = SamPredictor(sam)

#pymoo element
if 'stop' in globals():
    termination = get_termination("time", stop)
else:
    termination = None

diceL = []
jaccardL = []
scoreL = []
part_timeL = []

for element in files:
    name = os.path.basename(element)
    name2 = os.path.splitext(name)[0]
    print(name)
    image = nib.load(element)
    manualnib = nib.load(path_masks + '/' + name)
    print(f'Image dimensions: {image.shape}')
    print(f'Masks dimensions: {manualnib.shape}')
    print("Total slices: " + str(image.shape[2]))
    for slice_number in range(0, image.shape[2]):
        print("Slice number: " + str(slice_number))
        start_time = time.time()
        masks_slice = manualnib.dataobj[..., slice_number]
        image_slice = image.dataobj[..., slice_number]

        print(f'Image slice dimensions: {image_slice.shape}')
        print(f'Masks slice dimensions: {masks_slice.shape}')
        labels = np.unique(masks_slice)
        if labels.size > 1:
            processed_points = np.copy(image_slice)
            if windowing:
                # Windowing settings
                window_level = -650
                window_width = 1500
                processed_points = processed_points[:, :].clip(window_level - window_width // 2,
                                                               window_level + window_width // 2)

            processed_points = (processed_points - processed_points.min()) / (
                    processed_points.max() - processed_points.min()) * 255
            processed_points = processed_points.astype(np.uint8)
            processed_points = np.stack((processed_points,) * 3, axis=-1)
            print("Processed image slice dimensions: " + str(processed_points.shape))

            bb = find_bounding_box(masks_slice)
            bb = [bb[1], bb[0], bb[3], bb[2]]
            input_box = np.asarray(bb)

            original_mask_transformed = np.squeeze(masks_slice)
            original_mask_as_bool = original_mask_transformed != 0

            predictor.set_image(processed_points)

            #Run pymoo elements
            problem = samPoint()

            algorithm = GA(pop_size=popSize)
            histCallBack = History_CallBack()
            res = minimize(problem,
                           algorithm,
                           termination,
                           seed,
                           callback=histCallBack,
                           save_history=False,
                           verbose=True)

            X = res.X
            F = res.F

            objective = float(-F)

            jaccard, dice = compare_original_and_predicted_masks(masks_slice, maskG)
            s = ",".join([str(i) for i in X])

            print("Predicted mask dimensions: " + str(maskG.shape))

            print("Coordinates:                " + str(s))
            print("Objective function (" + obj + "): " + str(objective))
            print("Dice:                       " + str(dice))
            print("Jaccard:                    " + str(jaccard))
            print("Score:                      " + str(scoreG))
            print("Elapsed time:               " + str(time.time() - start_time) + " secs.")

            diceL.append(dice)
            jaccardL.append(jaccard)
            scoreL.append(scoreG)

            outfileHist = outfiles_path + "/" + name2 + "_" + str(slice_number) + ".txt"
            try:
                outputHist = open(outfileHist, 'w')
            except IOError:
                print("File %s cannot be created!!" % outfile)

            outputHist.write("num_evals" + "\t" + "Objective (" + obj + ")" + "\t" + "Coordinates" + "\n")

            for i in range(0, len(histCallBack.n_evals)):
                histS = ",".join([str(j) for j in histCallBack.optX[i]])
                outputHist.write(
                    str(histCallBack.n_evals[i]) + "\t" + str(histCallBack.optF[i][0]) + "\t" + str(histS) + "\n")

            outputHist.close()

            part_time = time.time() - start_time
            part_timeL.append(part_time)
            output.write(name2 + "_" + str(slice_number) + "\t" + str(objective) + "\t" + str(jaccard) + "\t" + str(
                dice) + "\t" + str(scoreG) + "\t" + str(part_time) + "\t" + str(s) + "\n")

            fig = plt.figure(figsize=(10, 10))
            plt.imshow(processed_points)
            show_mask(maskG, plt.gca())

            show_box(input_box, plt.gca())
            points = []
            for i in range(0, len(coordinates)):
                points.append(X[i])
            points = np.asarray(points)
            points = points.reshape(int(len(coordinates) / 2), 2)

            show_points(points, input_label, plt.gca())

            if obj == 'score':
                plt.title(f"SCORE: {scoreG:.3f}, Jaccard: {jaccard:.3f}, Dice: {dice:.3f}", fontsize=18)
            elif obj == 'jaccard':
                plt.title(f"JACCARD: {jaccard:.3f}, Dice: {dice:.3f}, Score: {scoreG:.3f}", fontsize=18)
            else:
                plt.title(f"DICE: {dice:.3f}, Jaccard: {jaccard:.3f}, Score: {scoreG:.3f}", fontsize=18)
            plt.axis('on')

            fig.savefig(outfiles_path + '/' + name2 + "_" + str(slice_number) + '.pdf')
            fig.clf()
            plt.close('all')
            gc.collect()  #To prevent running out of memory due to plotting in a loop


        else:
            print("This slice's manual mask has no data. Skipping")

output.write("\nMinimum Jaccard: " + str(np.min(jaccardL)) + "\n")
output.write("Maximum Jaccard: " + str(np.max(jaccardL)) + "\n")
output.write("Average Jaccard: " + str(np.mean(jaccardL)) + "\n")
output.write("Standard Deviation Jaccard: " + str(np.std(jaccardL)) + "\n\n")
output.write("Minimum Dice: " + str(np.min(diceL)) + "\n")
output.write("Maximum Dice: " + str(np.max(diceL)) + "\n")
output.write("Average Dice: " + str(np.mean(diceL)) + "\n")
output.write("Standard Deviation Dice: " + str(np.std(diceL)) + "\n\n")
output.write("Minimum Score: " + str(np.min(scoreL)) + "\n")
output.write("Maximum Score: " + str(np.max(scoreL)) + "\n")
output.write("Average Score: " + str(np.mean(scoreL)) + "\n")
output.write("Standard Deviation Score: " + str(np.std(scoreL)) + "\n\n")
output.write("Minimum individual Time: " + str(np.min(part_timeL)) + "\n")
output.write("Maximum individual Time: " + str(np.max(part_timeL)) + "\n")
output.write("Average individual Times: " + str(np.mean(part_timeL)) + "\n")
output.write("Standard Deviation individual Times: " + str(np.std(part_timeL)) + "\n\n")
output.write("Sum of individual Times: " + str(np.sum(part_timeL)) + "\n")
tot_time = str(time.time() - total_start_time)
output.write("Total Execution Time (s): " + str(tot_time) + "\n")

output.close()
