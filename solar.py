from standard import *
import numpy.typing as npt


class Solar_PowerProducer:
    def __init__(self, nameplate_capacity=float, sunlight_schedule=[6, 12, 18]):
        """
        #### Inputs:
        - `nameplate_capacity`
            - Power (kW) at peak sunlight
            - e.g. 300  :float
        - `sunlight_schedule`
            - `sunrise` :int
            - `peak`    :int
            - `sunset`  :int
            - e.g. [6,12,18]

        #### Properties
        - self.supply_schedules: list[np.array]
        - self.original: list[np.array]
            - note: Saves the clear-sky output schedule (before weather effects are applied)

        #### Methods
        - self.create_supply_schedules: list[np.array]
        """

        self.sunlight_schedule = sunlight_schedule
        self.nameplate_capacity = nameplate_capacity

    def create_supply_schedules(self, n_schedule: int) -> list[npt.NDArray]:

        sunrise, peak, sunset = self.sunlight_schedule
        capacity = self.nameplate_capacity
        self.supply_schedules = []

        for _ in range(n_schedule):

            hours = np.arange(24)
            output = np.zeros(24)
            mask = (hours >= sunrise) & (hours <= sunset)
            h = hours[mask]
            x = (h - peak) / (sunset - sunrise) * np.pi
            y = np.cos(x) ** 2
            output[mask] = capacity * y

            self.supply_schedules.append(output)

    def apply_weather_factor(
        self, weather_factor_schedules: list[npt.NDArray]
    ) -> list[npt.NDArray]:
        """
        This overwrites the supply schedules, but saves the original in self.original_schedules
        """

        if len(weather_factor_schedules) != len(self.supply_schedules):
            print(f"The number of sample schedules do not match.")
        else:
            weather_factor_schedules = np.stack(weather_factor_schedules)
            supply_schedules = np.stack(self.supply_schedules)
            supply_schedules = weather_factor_schedules * supply_schedules

        self.original = self.supply_schedules.copy()
        self.supply_schedules = list(supply_schedules)
