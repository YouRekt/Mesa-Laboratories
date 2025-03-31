from mesa.visualization import SolaraViz, make_space_component

from agents import PersonAgent
from model import TrendSpreadModel

def agent_portrayal(agent):
    if isinstance(agent, PersonAgent):
        return {
            "color": "tab:blue" if agent.sport_enthusiast else "tab:red",
            "size": 50 if agent.knows_about_trend else 30,
            "marker": "x" if agent.knows_about_trend else "o",
        }
    return {}


model_params = {
    "population_size": {
        "type": "SliderInt",
        "value": 20,
        "label": "Number of agents:",
        "min": 10,
        "max": 20,
        "step": 1,
    },
    "influencer_group_size": {
        "type": "SliderInt",
        "value": 1,
        "label": "Number of influencer agents:",
        "min": 1,
        "max": 5,
        "step": 1,
    },
    "grid_width": 10,
    "grid_height": 10,
}


model = TrendSpreadModel(10, 1, 10, 10)
grid_visualization = make_space_component(agent_portrayal)


page = SolaraViz(
    model,
    components=[grid_visualization],
    model_params=model_params,
    name="Trend Spreading Model",
)
page