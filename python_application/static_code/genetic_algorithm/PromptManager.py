import json
from typing import List, Tuple


class PromptManager:
    """Manages loading and processing of prompts from JSON files."""

    @staticmethod
    def parse_json_prompt(
        json_path: str, name: str, slice_num: int
    ) -> Tuple[List[int], List[float], List[float]]:
        """
        Parse a JSON file to extract prompts.

        Args:
            json_path (str): Path to JSON files directory
            name (str): File name
            slice_num (int): Slice number

        Returns:
            Tuple[List[int], List[float], List[float]]: Tuple with (box_coordinates, positive_coordinates, negative_coordinates)

        Raises:
            FileNotFoundError: If a JSON file is not found
            ValueError: If JSON structure is invalid or slice not found
        """
        json_file = f"{json_path}/{name}.json"

        try:
            with open(json_file) as file_in:
                data_list = json.load(file_in)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {json_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Error parsing JSON: {json_file}")

        # Validate JSON structure
        if not data_list or "image_file_path" not in data_list[0]:
            raise ValueError("Invalid JSON structure")

        expected_path = f"working_data/covid/image_{name}.npz"
        if data_list[0]["image_file_path"] != expected_path:
            raise ValueError(
                f"Incorrect image path in JSON: {data_list[0]['image_file_path']}"
            )

        # Search for specific slice
        slice_data = None
        for element in data_list:
            if element["slice_number"] == slice_num:
                slice_data = element
                break

        if slice_data is None:
            raise ValueError(f"Slice {slice_num} not found in {json_file}")

        # Extract bounding box
        bbox = slice_data["prompt"]["bounding_box"]
        box_coordinates = [
            bbox["upper_left_corner"]["row"],
            bbox["upper_left_corner"]["column"],
            bbox["bottom_right_corner"]["row"],
            bbox["bottom_right_corner"]["column"],
        ]

        # Extract points
        positive_coordinates = []
        negative_coordinates = []

        for point in slice_data["prompt"]["points"]:
            if point["label"] == 1:
                positive_coordinates.extend([point["row"], point["column"]])
            elif point["label"] == 0:
                negative_coordinates.extend([point["row"], point["column"]])
            else:
                raise ValueError(f"Invalid point label: {point['label']}")

        return box_coordinates, positive_coordinates, negative_coordinates
