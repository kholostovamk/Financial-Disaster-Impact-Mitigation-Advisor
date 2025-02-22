def disaster_loss_estimation(state: dict) -> dict:
    loss_prob_wrt_disastor = state["loss_prob_wrt_disastor"]
    disaster_probability = state["disaster_probability"]
    objects = state["objects"]
    
    objects = [object['name'] for object in objects]

    combined_loss = {
        k: sum(
            [
                loss_prob_wrt_disastor[obj][k] * disaster_probability[obj]
                for obj in loss_prob_wrt_disastor
            ]
        )
        for k in objects
    }
    return {"estimated_damage": combined_loss}

def compare_insurance(state: dict) -> dict:
    estimated_damage = state["estimated_damage"]
    policy_images = state["policy_images"]
    
    # covered_disasters = ["floods", "fires"]
    # coverage = {disaster: 1 if disaster in policy_text else 0 for disaster in estimated_damage}
    
    # total_estimated_loss = sum(estimated_damage.values())
    # total_covered = sum(coverage.values())

    return {"coverage": 0, "gap": 0}

def report_generation(state: dict) -> dict:
    gap = state["gap"]
    suggestions = []
    if gap > 0:
        suggestions.append("Consider increasing insurance coverage for uncovered disasters.")
    return {"report": "Insurance Analysis Report", "suggestions": suggestions}
