from typing import Dict, Any
from typing_extensions import TypedDict

class State(TypedDict):
    image: Any
    pdf: Any
    location: Any
    image_data: Any
    pdf_data: Any
    fips: int
    house_type: str
    objects: Dict
    price_data: Dict
    loss_prob_wrt_disastor: dict
    policy_images: str
    disaster_probability: dict
    estimated_damage: dict
    coverage: dict
    gap: float
    report: str
    suggestions: list
