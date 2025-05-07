from mesa.visualization import SolaraViz, make_space_component, make_plot_component

from agents import PersonAgent
from model import InfectiousDiseaseSpreadModel


def agent_portrayal(agent):
    if isinstance(agent, PersonAgent):
        return {
            "color": "tab:red" if agent.is_infected else "tab:blue",
            "size": 50 if agent.is_infected else 20,
            "marker": "x" if agent.has_comorbidities else "o",
        }
    return {}


propertylayer_portrayal = {
    "is_infected": {
        "color": "tab:red",
        "vmax": True,
        "vmin": False,
        "alpha": 0.3,
        "colorbar": False,
    },
}

model_params = {
    "population_size": {
        "type": "SliderInt",
        "value": 15,
        "label": "Number of agents:",
        "min": 5,
        "max": 100,
        "step": 1,
    },
    "infected_population_size": {
        "type": "SliderInt",
        "value": 1,
        "label": "Number of infected agents:",
        "min": 1,
        "max": 10,
        "step": 1,
    },
    "comorbidities_population_size": {
        "type": "SliderInt",
        "value": 4,
        "label": "Number of agents with comorbidities:",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "moving_probability": {
        "type": "SliderFloat",
        "value": 0.5,
        "label": "Probability of an agent moving:",
        "min": 0.01,
        "max": 1.0,
        "step": 0.01,
    },
    "grid_width": {
        "type": "SliderInt",
        "value": 10,
        "label": "Grid width:",
        "min": 5,
        "max": 30,
        "step": 1,
    },
    "grid_height": {
        "type": "SliderInt",
        "value": 10,
        "label": "Grid height:",
        "min": 5,
        "max": 30,
        "step": 1,
    },
}

model = InfectiousDiseaseSpreadModel()
grid_visualization = make_space_component(
    agent_portrayal, propertylayer_portrayal=propertylayer_portrayal
)

infection_plot = make_plot_component(
    {
        "Infected by direct interaction": "tab:red",
        "Infected by visiting an infected cell": "tab:green",
    }
)

page = SolaraViz(
    model,
    components=[grid_visualization, infection_plot],
    model_params=model_params,
    name="Virus X Spreading Model",
)
page
