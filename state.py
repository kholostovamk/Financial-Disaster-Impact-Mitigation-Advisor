from typing import Dict, Any
from typing_extensions import TypedDict

class State(TypedDict):
    image: Any
    image_bytes: bool
    pdf: Any
    pdf_bytes: bool
    location: Any
    image_data: Any
    pdf_data: Any
    fips: int
    house_type: str
    objects: Dict
    price_data: Dict
    loss_prob_wrt_disastor: dict
    policy_text: str
    disaster_probability: dict
    estimated_damage: dict
    evaluation : dict
    report: str
