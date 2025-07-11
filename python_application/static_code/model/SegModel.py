"""
Enumeration to simplify SAM usage and SAM 2 usage by SegModel class.

Each item contains the name SAM understands and corresponding path to its
weights. This way, given an instance of the enumeration the rest of needed
values are available. Besides, there is no possible misspelling as the
enumeration values are provided to the developer.

Items are sorted from the smallest (ViT_B) to the biggest (ViT_H). The biggest
is the more capable version of the model, but also the one that needs more
resources.

Four additional models are available: Tiny, Small, BasePlus and Large. These
are the models used in the SAM 2 paper. They are also sorted from the smallest
to the biggest.
"""

from enum import Enum
from collections import namedtuple

SegModelItem = namedtuple(
    'SegModelItem',
    ['version', 'name', 'checkpoint', 'configuration', 'description']
)


class SegModel(SegModelItem, Enum):
    """
    Segmentation available models.
    """

    SAM_ViT_B = SegModelItem(
        version=1,
        name='vit_b',
        checkpoint='model_checkpoints/sam_vit_b_01ec64.pth',
        configuration='',
        description='SAM ViT-B'
    )
    # MedSAM model obtained from: https://drive.google.com/file/d/1UAmWL88roYR7wKlnApw5Bcuzf2iQgk6_/view?usp=drive_link
    # GitHub Repo link: https://github.com/bowang-lab/MedSAM/tree/main
    MedSAM_ViT_B = SegModelItem(
        version=1,
        name='vit_b',
        checkpoint='model_checkpoints/medsam_vit_b_01ec64.pth',
        configuration='',
        description='MedSAM ViT-B'
    )
    SAM_ViT_L = SegModelItem(
        version=1,
        name='vit_l',
        checkpoint='model_checkpoints/sam_vit_l_0b3195.pth',
        configuration='',
        description='SAM ViT-L'
    )
    SAM_ViT_H = SegModelItem(
        version=1,
        name='vit_h',
        checkpoint='model_checkpoints/sam_vit_h_4b8939.pth',
        configuration='',
        description='SAM ViT-H'
    )
    SAM2_Tiny = SegModelItem(
        version=2,
        name='sam2_hiera_t',
        checkpoint='model_checkpoints/sam2_hiera_t.pt',
        configuration='sam2_hiera_t.yaml',
        description='SAM 2 Tiny'
    )
    SAM2_Small = SegModelItem(
        version=2,
        name='sam2_hiera_s',
        checkpoint='model_checkpoints/sam2_hiera_s.pt',
        configuration='sam2_hiera_s.yaml',
        description='SAM 2 Small'
    )
    # Huggingface model obtained from: https://huggingface.co/jiayuanz3/MedSAM2_pretrain/tree/main
    MedSAM2_Tiny = SegModelItem(
        version=2,
        name='sam2_hiera_t',
        checkpoint='model_checkpoints/MedSAM2_pretrain.pth',
        configuration='sam2_hiera_t.yaml',
        description='MedSAM 2 Tiny'
    )
    SAM2_BasePlus = SegModelItem(
        version=2,
        name='sam2_hiera_b_plus',
        checkpoint='model_checkpoints/sam2_hiera_b_plus.pt',
        configuration='sam2_hiera_b+.yaml',
        description='SAM 2 Base+'
    )
    SAM2_Large = SegModelItem(
        version=2,
        name='sam2_hiera_l',
        checkpoint='model_checkpoints/sam2_hiera_l.pt',
        configuration='sam2_hiera_l.yaml',
        description='SAM 2 Large'
    )

    # TODO: Not working yet models
    # LiteMedSAM model obtained from: https://drive.google.com/file/d/18Zed-TUTsmr2zc5CHUWd5Tu13nb6vq6z/view?usp=drive_link
    # GitHub Repo link: https://github.com/bowang-lab/MedSAM/tree/LiteMedSAM
    # LiteMedSAM_ViT_B = SegModelItem(
    #     version=1,
    #     name='vit_b',
    #     checkpoint='model_checkpoints/lite_medsam.pth',
    #     configuration='',
    #     description='LiteMedSAM ViT-B'
    # )
    # SAM_Tiny2p1 = SegModelItem(
    #     version=2.1,
    #     name='sam2p1_hiera_t',
    #     checkpoint='model_checkpoints/sam2p1_hiera_t.pt',
    #     configuration='sam2_hiera_t.yaml',
    #     description='SAM 2.1 Tiny'
    # )
    # Huggingface model obtained from: https://huggingface.co/wanglab/MedSAM2
    # MedSAM_Tiny2p1 = SegModelItem(
    #     version=2.1,
    #     name='sam2p1_hiera_t',
    #     checkpoint='model_checkpoints/MedSAM2_latest.pt',
    #     configuration='sam2_hiera_t.yaml',
    #     description='MedSAM 2.1 Tiny'
    # )
    # SAM_Small2p1 = SegModelItem(
    #     version=2.1,
    #     name='sam2p1_hiera_s',
    #     checkpoint='model_checkpoints/sam2p1_hiera_s.pt',
    #     configuration='sam2_hiera_s.yaml',
    #     description='SAM 2.1 Small'
    # )
    # SAM_BasePlus2p1 = SegModelItem(
    #     version=2.1,
    #     name='sam2p1_hiera_b_plus',
    #     checkpoint='model_checkpoints/sam2p1_hiera_b_plus.pt',
    #     configuration='sam2_hiera_b+.yaml',
    #     description='SAM 2.1 Base+'
    # )
    # SAM_Large2p1 = SegModelItem(
    #     version=2.1,
    #     name='sam2p1_hiera_l',
    #     checkpoint='model_checkpoints/sam2p1_hiera_l.pt',
    #     configuration='sam2_hiera_l.yaml',
    #     description='SAM 2.1 Large'
    # )

    @staticmethod
    def from_string(model_str: str) -> "SegModel":
        """
        Create an instance of SegModel from a string.

        Parameters:
        - model_str (str): A string representing the model.

        Returns:
        - SegModel: A new instance of SegModel matching the provided string.

        Raises:
        - ValueError: if no matching model is found.
        """
        for model in SegModel:
            if model.value == model_str:
                return model
        raise ValueError("No matching SegModel found.")

    @staticmethod
    def from_description(description: str) -> "SegModel":
        """
        Create an instance of SegModel from the description string.

        Parameters:
        - description (str): A string representing the model.

        Returns:
        - SegModel: A new instance of SegModel matching the provided description string.

        Raises:
        - ValueError: if no matching model is found.
        """
        for model in SegModel:
            if model.description == description:
                return model
        raise ValueError("No matching SegModel found.")
