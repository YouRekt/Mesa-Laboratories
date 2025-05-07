import logging

from mesa import Model
from mesa.experimental.cell_space import Grid2DMovingAgent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PersonAgent(Grid2DMovingAgent):
    _is_infected: bool
    _has_comorbidities: bool
    _moving_probability: float

    def __init__(
        self,
        model: Model,
        is_infected: bool = False,
        has_comorbidities: bool = False,
        moving_probability: float = 0.5,
    ):
        super().__init__(model)
        self._is_infected = is_infected
        self._has_comorbidities = has_comorbidities
        self._moving_probability = moving_probability

    @property
    def is_infected(self) -> bool:
        return self._is_infected

    @property
    def has_comorbidities(self) -> bool:
        return self._has_comorbidities

    def _get_infected(self, is_direct: bool, agent_id: str = None):
        self._is_infected = True
        if is_direct:
            self.model.direct_infections += 1
            logger.info(f"[{self.unique_id}] {agent_id} has infected me!")
        else:
            self.model.location_infections += 1
            logger.info(f"[{self.unique_id}] I got infected!")

    def get_infected_from_cell(self):
        self.check_grid_initialization(
            error_msg="The agent cannot get infected from the cell."
        )

        if (
            not self.is_infected
            and self.random.random() < self._get_infection_probabilty()
        ):
            self._get_infected(is_direct=False)

    def _get_infection_probabilty(self):
        self.check_grid_initialization(
            error_msg="The agent cannot get infection probability"
        )
        infection_probability = 0.25 if self.has_comorbidities else 0.0

        if self.cell.properties["is_infected"]:
            infection_probability += 0.5
        elif self._in_neighbourhood_of_infection():
            infection_probability += 0.25
        else:
            return 0.0

        return infection_probability

    def _in_neighbourhood_of_infection(self):
        self.check_grid_initialization(
            error_msg="The agent cannot check if neighbouring cells are infected"
        )

        for cell in self.cell.neighborhood:
            if cell.properties["is_infected"]:
                return True
        return False

    def check_grid_initialization(self, error_msg: str = ""):
        if self.cell is None:
            logger.error("Couldn't perform operation on the grid: {error_msg}.")
            raise ValueError(f"The grid has not been initialized: {error_msg}")

    def move_around(self):
        self.check_grid_initialization(
            error_msg="The agent cannot move around the grid."
        )
        if self.random.random() < self._moving_probability:
            self.move_to(self.cell.neighborhood.select_random_cell())

    def spread_virus(self):
        self.check_grid_initialization(error_msg="The agent cannot spread the virus.")

        if self.is_infected:
            if not self.cell.properties["is_infected"]:
                self.cell.properties["is_infected"] = True

            encountered_agents = [
                agent for agent in self.cell.agents if agent is not self
            ]

            for agent in encountered_agents:
                infection_probability = 0.75 if agent.has_comorbidities else 0.5
                if (
                    not agent.is_infected
                    and self.random.random() < infection_probability
                ):
                    agent._get_infected(agent_id=self.unique_id, is_direct=True)
