import logging

from mesa import Model
from mesa.experimental.cell_space import OrthogonalVonNeumannGrid, PropertyLayer
from mesa.datacollection import DataCollector

from agents import PersonAgent

logger = logging.getLogger(__name__)


class InfectiousDiseaseSpreadModel(Model):
    population_size: int
    infected_population_size: int
    comorbidities_population_size: int
    moving_probability: float
    seed: int
    grid: OrthogonalVonNeumannGrid
    infected_property_layer: PropertyLayer
    direct_infections: int
    location_infections: int
    datacollector: DataCollector

    def __init__(
        self,
        population_size: int = 10,
        infected_population_size: int = 1,
        comorbidities_population_size: int = 4,
        moving_probability: float = 0.5,
        grid_width: int = 10,
        grid_height: int = 10,
        seed: int = None,
    ):
        super().__init__(seed=seed)

        self.population_size = population_size
        self.infected_population_size = infected_population_size
        self.comorbidities_population_size = comorbidities_population_size
        self.moving_probability = moving_probability
        self.direct_infections = 0
        self.location_infections = 0

        self.grid = OrthogonalVonNeumannGrid(
            (grid_width, grid_height), True, random=self.random
        )

        self.generate_person_agents()
        self.initialize_infected_property_layer()
        self.initialize_data_collector()

    def generate_person_agents(self):
        PersonAgent.create_agents(
            self,
            self.infected_population_size,
            is_infected=True,
            has_comorbidities=False,
            moving_probability=self.moving_probability,
        )

        PersonAgent.create_agents(
            self,
            self.comorbidities_population_size,
            is_infected=False,
            has_comorbidities=True,
            moving_probability=self.moving_probability,
        )

        PersonAgent.create_agents(
            self,
            self.population_size
            - self.infected_population_size
            - self.comorbidities_population_size,
            is_infected=False,
            has_comorbidities=False,
            moving_probability=self.moving_probability,
        )

        self.place_agents_on_grid()

    def place_agents_on_grid(self):
        x_range = self.rng.integers(0, self.grid.width, size=self.population_size)
        y_range = self.rng.integers(0, self.grid.height, size=self.population_size)

        for agent, x_coord, y_coord in zip(
            self._agents_by_type[PersonAgent], x_range, y_range
        ):
            agent.cell = self.grid[(x_coord, y_coord)]

    def initialize_infected_property_layer(self):
        for cell in self.grid.all_cells.cells:
            cell.properties["is_infected"] = False
            cell.properties["virus_persistence"] = 0

        self.infected_property_layer = PropertyLayer(
            "is_infected", self.grid.dimensions, False, bool
        )

        self.grid.add_property_layer(self.infected_property_layer)

    def get_direct_infections(self):
        return self.direct_infections

    def get_location_infections(self):
        return self.location_infections

    def initialize_data_collector(self):
        self.datacollector = DataCollector(
            model_reporters={
                "Infected by direct interaction": self.get_direct_infections,
                "Infected by visiting an infected cell": self.get_location_infections,
            },
        )
        self.datacollector.collect(self)

    def _stop_condition(step) -> None:
        def perform_step(self):
            if (
                len(
                    self._agents_by_type[PersonAgent].select(
                        lambda agent: not agent.is_infected
                    )
                )
                == 0
            ):
                self.running = False
                logger.info("All agents are infected. Stopping the simulation.")
            else:
                step(self)

        return perform_step

    @_stop_condition
    def step(self):
        self.datacollector.collect(self)
        self._agents_by_type[PersonAgent].do("move_around")
        self._agents_by_type[PersonAgent].do("spread_virus")
        self._agents_by_type[PersonAgent].do("get_infected_from_cell")

        for cell in self.grid.all_cells.cells:
            if cell.properties["is_infected"]:
                self.infected_property_layer.data[cell.coordinate[0]][
                    cell.coordinate[1]
                ] = True
                if any(agent.is_infected for agent in cell.agents):
                    cell.properties["virus_persistence"] = 0
                else:
                    cell.properties["virus_persistence"] += 1

                if cell.properties["virus_persistence"] > 2:
                    cell.properties["is_infected"] = False
                    cell.properties["virus_persistence"] = 0
                    self.infected_property_layer.data[cell.coordinate[0]][
                        cell.coordinate[1]
                    ] = False
