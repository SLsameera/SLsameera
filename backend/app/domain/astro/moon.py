from __future__ import annotations

import math
from datetime import datetime
from typing import Tuple


class MoonOrbitSimulator:
    """
    Simplified Earth–Moon orbital simulator.

    - Elliptical orbit using Kepler's equation (constant elements)
    - Fixed inclination relative to reference plane
    - Returns ECI-like coordinates in km (approximate; not for navigation)
    """

    def __init__(self) -> None:
        # Mean orbital elements (approximate, J2000-ish constants)
        self.semi_major_axis_km: float = 384_400.0  # a
        self.eccentricity: float = 0.0549  # e
        self.orbital_period_days: float = 27.321661  # sidereal period
        self.inclination_deg: float = 5.145  # relative to ecliptic (approx)
        # For simplicity, set ascending node and argument of periapsis to zero
        # You can refine with Ω and ω for better orientation
        self.longitude_ascending_node_deg: float = 0.0  # Ω
        self.argument_of_periapsis_deg: float = 0.0  # ω
        self.epoch: datetime = datetime(2023, 1, 1)

    def _solve_kepler(self, mean_anomaly_rad: float, eccentricity: float) -> float:
        """Solve Kepler's equation for eccentric anomaly using Newton-Raphson."""
        eccentric_anomaly = mean_anomaly_rad
        for _ in range(6):
            f = eccentric_anomaly - eccentricity * math.sin(eccentric_anomaly) - mean_anomaly_rad
            f_prime = 1 - eccentricity * math.cos(eccentric_anomaly)
            eccentric_anomaly -= f / f_prime
        return eccentric_anomaly

    def get_moon_position(self, dt: datetime) -> Tuple[float, float, float]:
        """
        Calculate the Moon's approximate 3D position (km) at datetime `dt`.

        Steps:
        - Compute mean anomaly from epoch and sidereal period
        - Solve Kepler's equation to get eccentric anomaly and true anomaly
        - Compute radius r = a (1 - e cos E)
        - Position in orbital plane, then rotate by inclination
        """
        delta_days = (dt - self.epoch).total_seconds() / 86400.0
        mean_motion = 2 * math.pi / self.orbital_period_days  # rad/day
        mean_anomaly = (mean_motion * delta_days) % (2 * math.pi)

        E = self._solve_kepler(mean_anomaly, self.eccentricity)

        # True anomaly from eccentric anomaly
        cos_E = math.cos(E)
        sin_E = math.sin(E)
        sqrt_one_minus_e2 = math.sqrt(1 - self.eccentricity ** 2)
        true_anomaly = math.atan2(sqrt_one_minus_e2 * sin_E, cos_E - self.eccentricity)

        # Distance from Earth (km)
        radius = self.semi_major_axis_km * (1 - self.eccentricity * cos_E)

        # Position in the orbital plane
        x_orb = radius * math.cos(true_anomaly)
        y_orb = radius * math.sin(true_anomaly)
        z_orb = 0.0

        # Rotate by argument of periapsis (ω) around z (kept 0 here)
        # Then by inclination (i) around x
        # Then by longitude of ascending node (Ω) around z (kept 0 here)
        i_rad = math.radians(self.inclination_deg)
        cos_i = math.cos(i_rad)
        sin_i = math.sin(i_rad)

        # Rotation around x-axis by inclination i
        x1 = x_orb
        y1 = y_orb * cos_i - z_orb * sin_i
        z1 = y_orb * sin_i + z_orb * cos_i

        # With Ω=0 and ω=0, additional z-rotations are identity
        return (x1, y1, z1)

    def estimate_tidal_force(self, dt: datetime) -> float:
        """
        Estimate tidal force magnitude using inverse-cube dependence.
        Returns a normalized scalar proportional to 1 / r^3.
        """
        x, y, z = self.get_moon_position(dt)
        distance = math.sqrt(x * x + y * y + z * z)
        if distance <= 0:
            return float("inf")
        return 1.0 / (distance ** 3)


if __name__ == "__main__":
    sim = MoonOrbitSimulator()
    now = datetime.utcnow()
    pos = sim.get_moon_position(now)
    force = sim.estimate_tidal_force(now)
    print(f"Moon position at {now} (km): x={pos[0]:.0f}, y={pos[1]:.0f}, z={pos[2]:.0f}")
    print(f"Estimated tidal force magnitude (normalized): {force:.3e}")