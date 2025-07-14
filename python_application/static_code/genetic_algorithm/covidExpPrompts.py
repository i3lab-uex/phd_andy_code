import warnings
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from pymoo.core.callback import Callback
from pymoo.termination import get_termination
from pymoo.algorithms.soo.nonconvex.ga import GA
import argparse, time, random, glob, os, gc, torch, json
from segment_anything import sam_model_registry, SamPredictor

from python_application.static_code.metrics.metric_calculation import (
    compare_original_and_predicted_masks_mod_jaccard,
    compare_original_and_predicted_masks_mod_dice,
    compare_original_and_predicted_masks,
)
from python_application.static_code.visualization.visual_helpers import (
    show_points,
    show_box,
    show_mask,
)

# if warnings have been suppressed, they are now re-enabled
warnings.filterwarnings("default")


class SamPoint(Problem):

    def __init__(self):
        limit = []
        cxl = min(input_box[0], input_box[2])
        cxu = max(input_box[0], input_box[2])
        cyl = min(input_box[1], input_box[3])
        cyu = max(input_box[1], input_box[3])
        if len(coordinates) == 6:
            xl = np.array([cxl, cyl, cxl, cyl, cxl, cyl])
            xu = np.array([cxu, cyu, cxu, cyu, cxu, cyu])
        elif len(coordinates) == 4:
            xl = np.array([cxl, cyl, cxl, cyl])
            xu = np.array([cxu, cyu, cxu, cyu])
        super().__init__(n_var=len(coordinates), n_obj=1, xl=xl, xu=xu)

    def _evaluate(self, x, out, *args, **kwargs):
        if obj == "score":
            sco = [1]
        elif obj == "jaccard":
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
                masks, scores, _ = predictor.predict(
                    point_coords=input_point,
                    point_labels=input_label,
                    box=input_box[None, :],
                    multimask_output=True,
                )
                mask = masks[np.argmax(scores), :, :]
                score = np.max(scores)
            else:
                mask, score, _ = predictor.predict(
                    point_coords=input_point,
                    point_labels=input_label,
                    box=input_box[None, :],
                    multimask_output=False,
                )

            if obj == "score":
                if -score < min(sco):
                    maskG = mask
                    scoreG = float(score)
                sco.append(-score)
            elif obj == "jaccard":
                jaccard = compare_original_and_predicted_masks_mod_jaccard(
                    original_mask_as_bool, mask
                )
                if -jaccard < min(jac):
                    maskG = mask
                    scoreG = float(score)
                jac.append(-jaccard)
            else:
                dice = compare_original_and_predicted_masks_mod_dice(
                    original_mask_as_bool, mask
                )
                if -dice < min(dic):
                    maskG = mask
                    scoreG = float(score)
                dic.append(-dice)

        if obj == "score":
            sco.pop(0)
            out["F"] = [sco]
        elif obj == "jaccard":
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


def initialize_pop(coords):
    print(coords)
    ind = np.ndarray(shape=(popSize, len(coords)), dtype=float)
    ind[0] = coords
    for i in range(1, popSize):
        x = random.uniform(-popSize / 2, popSize / 2)
        y = random.uniform(-popSize / 2, popSize / 2)
        for j in range(0, len(coords), 2):
            ind[i, j] = coords[j] + x

            while ind[i, j] > box_coor[2] or ind[i, j] < box_coor[0]:
                ind[i, j] = coords[j] + random.uniform(-popSize / 2, popSize / 2)

        for j in range(1, len(coords + 1), 2):
            ind[i, j] = coords[j] + y

            while ind[i, j] > box_coor[3] or ind[i, j] < box_coor[1]:
                ind[i, j] = coords[j] + random.uniform(-popSize / 2, popSize / 2)
    return ind


def parse_json(jsonpath, name, slice):
    jsonfile = jsonpath + "/" + name + ".json"
    with open(jsonfile) as filein:
        dicts = json.load(filein)
    if dicts[0]["image_file_path"] == "working_data/covid/image_" + name + ".npz":
        for element in dicts:
            if element["slice_number"] == slice:
                print(element["slice_number"])
                print(element["prompt"]["points"][0]["row"])
                data = element
                break
    else:
        print("Error: Bad json file")
        exit(1)

    box_coor = [
        data["prompt"]["bounding_box"]["upper_left_corner"]["row"],
        data["prompt"]["bounding_box"]["upper_left_corner"]["column"],
        data["prompt"]["bounding_box"]["bottom_right_corner"]["row"],
        data["prompt"]["bounding_box"]["bottom_right_corner"]["column"],
    ]

    pos_coor = []
    neg_coor = []

    for point in data["prompt"]["points"]:
        if point["label"] == 1:
            pos_coor.append(point["row"])
            pos_coor.append(point["column"])
        elif point["label"] == 0:
            neg_coor.append(point["row"])
            neg_coor.append(point["column"])
        else:
            print("Error in: " + str(point))
            exit(1)
    print(box_coor, pos_coor, neg_coor)
    return box_coor, pos_coor, neg_coor


############################################################################################################################################################################################################################################
#       MAIN
############################################################################################################################################################################################################################################
total_start_time = time.time()
# Create an instance of the ArgumentParser class
parser = argparse.ArgumentParser(description="SAM optimization")

# Add arguments with flags
parser.add_argument("-i", "--images", required=True, help="Input images path")
parser.add_argument(
    "-d",
    "--dataset",
    required=True,
    choices=["corona", "radio"],
    help="Select the dataset: corona (coronacases) or radio (radiopaedia)",
)
parser.add_argument("-k", "--masks", required=True, help="Manual masks path")
parser.add_argument(
    "-o",
    "--output",
    required=True,
    help="Output files path. Be careful, files will be rewrited!",
)
parser.add_argument(
    "-c", "--checkpoint", required=True, help="SAM Model Checkpoint file"
)
parser.add_argument(
    "-v",
    "--model",
    default="vit_h",
    choices=["vit_b", "vit_l", "vit_h"],
    help="Select the SAM model version. Default is vit_h",
)
parser.add_argument(
    "-f",
    "--objective",
    default="dice",
    choices=["dice", "jaccard", "score"],
    help="Select the objective function. Default is dice",
)
parser.add_argument(
    "-m", "--multimask", action="store_true", help="Multimask option on. Default is off"
)
parser.add_argument(
    "-s",
    "--stopping",
    default=None,
    help="Stopping criterion in hh:mm:ss format. Default no limit",
)
parser.add_argument(
    "--seed", type=int, default=1, help="Seed for random numbers. Default is 1"
)

# Parse the command line arguments
multimask = False
args = parser.parse_args()
print(args)


if args.images:
    path_images = args.images
if args.dataset:
    dataset = args.dataset
if args.masks:
    path_masks = args.masks
if args.output:
    outfiles_path = args.output
if args.checkpoint:
    sam_checkpoint = args.checkpoint
if args.model:
    model_type = args.model
if args.objective:
    obj = args.objective
if args.multimask:
    multimask = True
if args.stopping:
    stop = args.stopping
if args.seed:
    seed = args.seed

prompts = "promptsCovid"

popSize = 100
random.seed(seed)

if dataset == "corona":
    files = glob.glob(path_images + "/coronacases_*.nii.gz")
    windowing = True
elif dataset == "radio":
    files = glob.glob(path_images + "/radiopaedia_*.nii.gz")
    windowing = False

files.sort()


try:
    os.makedirs(outfiles_path)
except OSError:
    print("Directory %s cannot be created!!" % outfiles_path)

if dataset == "corona":
    outfile = outfiles_path + "/coronaExp.txt"
elif dataset == "radio":
    outfile = outfiles_path + "/radioExp.txt"

try:
    output = open(outfile, "w")
except IOError:
    print("File %s cannot be created!!" % outfile)

output.write(
    "Image"
    + "\t"
    + "Objective ("
    + obj
    + ")"
    + "\t"
    + "Jaccard"
    + "\t"
    + "Dice"
    + "\t"
    + "Score"
    + "\t"
    + "Time (s)"
    + "\t"
    + "Coordinates"
    + "\n"
)


# set SAM features
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

predictor = SamPredictor(sam)

# pymoo element
if "stop" in globals():
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
    bname = os.path.splitext(name2)[0]
    print(name)
    image = nib.load(element)
    manualnib = nib.load(path_masks + "/" + name)
    print(f"Image dimensions: {image.shape}")
    print(f"Masks dimensions: {manualnib.shape}")
    print("Total slices: " + str(image.shape[2]))
    for slice_number in range(0, image.shape[2]):
        print("Slice number: " + str(slice_number))
        start_time = time.time()
        masks_slice = manualnib.dataobj[..., slice_number]
        image_slice = image.dataobj[..., slice_number]

        print(f"Image slice dimensions: {image_slice.shape}")
        print(f"Masks slice dimensions: {masks_slice.shape}")
        labels = np.unique(masks_slice)
        if labels.size > 1:
            processed_points = np.copy(image_slice)
            if windowing:
                # Windowing settings
                window_level = -650
                window_width = 1500
                processed_points = processed_points[:, :].clip(
                    window_level - window_width // 2, window_level + window_width // 2
                )

            processed_points = (
                (processed_points - processed_points.min())
                / (processed_points.max() - processed_points.min())
                * 255
            )
            processed_points = processed_points.astype(np.uint8)
            processed_points = np.stack((processed_points,) * 3, axis=-1)
            print("Processed image slice dimensions: " + str(processed_points.shape))

            box_coor, pos_coor, neg_coor = parse_json(prompts, bname, slice_number)

            bb = [box_coor[0], box_coor[1], box_coor[2], box_coor[3]]
            input_box = np.asarray(bb)

            input_label = []
            for i in range(int(len(pos_coor) / 2)):
                input_label.append(1)
            for i in range(int(len(neg_coor) / 2)):
                input_label.append(0)
            input_label = np.asarray(input_label)

            coordinates = np.asarray(pos_coor + neg_coor)

            original_mask_transformed = np.squeeze(masks_slice)
            original_mask_as_bool = original_mask_transformed != 0

            predictor.set_image(processed_points)

            # Run pymoo elements
            problem = SamPoint()

            algorithm = GA(pop_size=popSize, sampling=initialize_pop(coordinates))
            histCallBack = History_CallBack()
            res = minimize(
                problem,
                algorithm,
                termination,
                seed,
                callback=histCallBack,
                save_history=False,
                verbose=True,
            )

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
            print(
                "Elapsed time:               "
                + str(time.time() - start_time)
                + " secs."
            )

            diceL.append(dice)
            jaccardL.append(jaccard)
            scoreL.append(scoreG)
            outfileHist = outfiles_path + "/" + bname + "_" + str(slice_number) + ".txt"
            try:
                outputHist = open(outfileHist, "w")
            except IOError:
                print("File %s cannot be created!!" % outfile)

            outputHist.write(
                "num_evals"
                + "\t"
                + "Objective ("
                + obj
                + ")"
                + "\t"
                + "Coordinates"
                + "\n"
            )

            for i in range(0, len(histCallBack.n_evals)):
                histS = ",".join([str(j) for j in histCallBack.optX[i]])
                outputHist.write(
                    str(histCallBack.n_evals[i])
                    + "\t"
                    + str(histCallBack.optF[i][0])
                    + "\t"
                    + str(histS)
                    + "\n"
                )

            outputHist.close()

            part_time = time.time() - start_time
            part_timeL.append(part_time)
            output.write(
                bname
                + "_"
                + str(slice_number)
                + "\t"
                + str(objective)
                + "\t"
                + str(jaccard)
                + "\t"
                + str(dice)
                + "\t"
                + str(scoreG)
                + "\t"
                + str(part_time)
                + "\t"
                + str(s)
                + "\n"
            )

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

            if obj == "score":
                plt.title(
                    f"SCORE: {scoreG:.3f}, Jaccard: {jaccard:.3f}, Dice: {dice:.3f}",
                    fontsize=18,
                )
            elif obj == "jaccard":
                plt.title(
                    f"JACCARD: {jaccard:.3f}, Dice: {dice:.3f}, Score: {scoreG:.3f}",
                    fontsize=18,
                )
            else:
                plt.title(
                    f"DICE: {dice:.3f}, Jaccard: {jaccard:.3f}, Score: {scoreG:.3f}",
                    fontsize=18,
                )
            plt.axis("on")

            fig.savefig(outfiles_path + "/" + bname + "_" + str(slice_number) + ".pdf")
            fig.clf()
            plt.close("all")
            gc.collect()  # To prevent running out of memory due to plotting in a loop

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
