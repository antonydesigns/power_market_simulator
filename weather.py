from standard import *
from scipy.ndimage import gaussian_filter1d
import numpy.typing as npt

np.set_printoptions(suppress=True, precision=6)

rng = np.random.RandomState(seed=24)
# rng = np.random


class Weather:

    def __init__(self, profile: list[float]):
        """
        #### Input
        - profile \n
            e.g. [ `min factor`:float, `max factor`:float, `smoothing factor`:float

        #### Properties
        - self.weather_factor_schedules: list[np.array]

        #### Methods
        - self.create_schedules: list[np.array]
        """

        self.profile = profile
        self.weather_factor_schedules = []

    def create_schedules(self, n_schedule: int, continuous=False):

        if continuous:
            self.weather_factor_schedules = self.smooth_random_curve(
                self.profile, n_schedule, True
            )
        else:
            for _ in range(n_schedule):
                self.weather_factor_schedules.append(
                    self.smooth_random_curve(self.profile, n_schedule, False)
                )

    def smooth_random_curve(
        self, profile, n_schedule, continuous
    ) -> npt.NDArray | list[npt.NDArray]:
        min, max, smoothing_factor = profile
        range = max - min

        # create random noise
        if continuous:
            # continuous random noise will be split by N schedules later
            x = rng.random(24 * n_schedule)
        else:
            x = rng.random(24)

        # smoothing
        x_smooth = gaussian_filter1d(x, smoothing_factor, mode="nearest")

        # normalization
        x_smooth -= x_smooth.min()
        if x_smooth.max() > 0:
            x_smooth /= x_smooth.max()

        # outputs 0 --> min --> max
        result: npt.NDArray = min + x_smooth * range

        if continuous:
            parts = np.split(result, n_schedule)
            return parts
        else:
            return result
