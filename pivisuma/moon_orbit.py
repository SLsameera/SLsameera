"""
Pivisuma: Simplified Earth–Moon orbital mechanics and tidal model

This module provides a lightweight, extensible model of the Moon's geocentric
position and an estimate of the tidal acceleration it induces at Earth's
surface. It is intended as a first module for the "Pivisuma" project and
balances educational transparency with reasonable accuracy for environmental
cycle studies.

Key features
- Compute the Moon's geocentric Earth-Centered Inertial (ECI, equatorial) coordinates (x, y, z).
- Estimate the maximum tidal acceleration at Earth's surface for a given datetime.
- Clean, modular design that can be extended with higher fidelity models later.

Physics notes and simplifications
- We use a simplified Keplerian model with mean lunar elements referenced to the
  ecliptic of J2000 and then rotate to the equatorial frame using a fixed
  obliquity. This captures the main geometry and time evolution but ignores many
  smaller perturbations (e.g., evection, variation, annual equation) and time
  scale differences (TT vs UTC).
- The Moon's mean orbital elements are treated as slowly varying linear functions
  of time since J2000. This reproduces the major motions of the Moon including
  node regression and perigee advance with approximate rates.
- Tidal acceleration magnitude is computed at the sublunar point using the
  textbook approximation a_tide ≈ 2 G M_moon R_earth / r^3. This represents the
  maximum vertical tidal acceleration at Earth's surface due to the Moon at a
  given geocentric distance r, and is sufficient for coarse environmental
  correlations.

Units
- All internal distances are meters unless otherwise noted.
- Angles are in radians internally; API functions accept and return SI units.

Caveats
- For precise ephemerides, consider replacing the element model with ELP2000,
  VSOP/Chapront series, or JPL DE ephemerides. This module is designed to be a
  clear starting point rather than a high-precision reference.

Example
    Run this module as a script to print the Moon's position and tidal
    acceleration for the current UTC datetime.

    $ python -m pivisuma.moon_orbit

"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from typing import Tuple


# ----------------------------
# Physical and astronomical constants
# ----------------------------
G_SI: float = 6.67430e-11  # m^3 kg^-1 s^-2
M_MOON_KG: float = 7.342e22  # kg
R_EARTH_M: float = 6371_000.0  # m
OBLIQUITY_EPSILON_RAD: float = math.radians(23.43929111)  # J2000 mean obliquity

# Epoch: J2000, approximately 2000-01-01 12:00:00 UTC for this simplified model
J2000_UTC = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class OrbitalElementsMeanLunar:
    """Simplified mean orbital elements of the Moon relative to the ecliptic.

    The elements evolve linearly with time since J2000 following widely-used
    average rates. This is adequate for educational and environmental-cycle
    applications, but not for precise navigation.

    Attributes
    - semi_major_axis_m: Semi-major axis in meters.
    - eccentricity: Eccentricity (dimensionless).
    - inclination_rad: Inclination with respect to the ecliptic (radians).
    - ascending_node_longitude_deg_at_j2000: Ω at J2000 in degrees.
    - ascending_node_longitude_deg_rate_per_day: dΩ/dt in deg/day (~ -0.05295).
    - argument_of_periapsis_deg_at_j2000: ω at J2000 in degrees.
    - argument_of_periapsis_deg_rate_per_day: dω/dt in deg/day (~ +0.16436).
    - mean_longitude_deg_at_j2000: L at J2000 in degrees.
    - mean_longitude_deg_rate_per_day: dL/dt in deg/day (~ +13.176396).

    These parameters imply a mean anomaly M = L - Ω - ω with a rate
    near 13.064993 deg/day, close to the lunar sidereal motion.
    """

    semi_major_axis_m: float = 384_400_000.0
    eccentricity: float = 0.0549
    inclination_rad: float = math.radians(5.145)

    ascending_node_longitude_deg_at_j2000: float = 125.08
    ascending_node_longitude_deg_rate_per_day: float = -0.0529538083

    argument_of_periapsis_deg_at_j2000: float = 318.15
    argument_of_periapsis_deg_rate_per_day: float = 0.1643573223

    mean_longitude_deg_at_j2000: float = 218.316
    mean_longitude_deg_rate_per_day: float = 13.176396


class MoonOrbitModel:
    """Compute Moon ECI coordinates and tidal acceleration using a simplified model.

    Methods
    - get_position_eci(dt): Geocentric ECI coordinates (x, y, z) in meters.
    - estimate_tidal_acceleration(dt): Maximum tidal acceleration at Earth's
      surface in m/s^2, at the sublunar point.

    Notes
    - ECI frame here is the mean equator and equinox of J2000 (no precession or
      nutation). The position is derived from ecliptic elements rotated by the
      fixed obliquity of J2000.
    """

    def __init__(self, elements: OrbitalElementsMeanLunar | None = None) -> None:
        self.elements = elements or OrbitalElementsMeanLunar()

    # ------------- Public API -------------
    def get_position_eci(self, dt: datetime) -> Tuple[float, float, float]:
        """Return the Moon's geocentric ECI coordinates (x, y, z) in meters.

        Parameters
        - dt: A timezone-aware or naive datetime. If naive, UTC is assumed.

        Returns
        - (x, y, z): Tuple of ECI coordinates in meters.
        """
        dt_utc = self._as_utc(dt)
        days_since_j2000 = self._days_since_j2000(dt_utc)

        # Compute time-dependent angles in radians
        omega_capital = math.radians(
            self.elements.ascending_node_longitude_deg_at_j2000
            + self.elements.ascending_node_longitude_deg_rate_per_day * days_since_j2000
        )
        omega_lower = math.radians(
            self.elements.argument_of_periapsis_deg_at_j2000
            + self.elements.argument_of_periapsis_deg_rate_per_day * days_since_j2000
        )
        mean_longitude = math.radians(
            self.elements.mean_longitude_deg_at_j2000
            + self.elements.mean_longitude_deg_rate_per_day * days_since_j2000
        )

        # Mean anomaly M = L - Ω - ω (normalize to [-pi, pi])
        mean_anomaly = self._normalize_radians(mean_longitude - omega_capital - omega_lower)

        # Solve Kepler's equation for eccentric anomaly E
        eccentric_anomaly = self._solve_kepler(mean_anomaly, self.elements.eccentricity)

        # True anomaly ν and radius r
        true_anomaly = 2.0 * math.atan2(
            math.sqrt(1.0 + self.elements.eccentricity) * math.sin(eccentric_anomaly / 2.0),
            math.sqrt(1.0 - self.elements.eccentricity) * math.cos(eccentric_anomaly / 2.0),
        )
        radius_m = self.elements.semi_major_axis_m * (1.0 - self.elements.eccentricity * math.cos(eccentric_anomaly))

        # Argument of latitude u = ω + ν
        argument_of_latitude = self._normalize_radians(omega_lower + true_anomaly)

        # Position in ecliptic frame from elements (x_ecl, y_ecl, z_ecl)
        x_ecl = radius_m * (
            math.cos(omega_capital) * math.cos(argument_of_latitude)
            - math.sin(omega_capital) * math.sin(argument_of_latitude) * math.cos(self.elements.inclination_rad)
        )
        y_ecl = radius_m * (
            math.sin(omega_capital) * math.cos(argument_of_latitude)
            + math.cos(omega_capital) * math.sin(argument_of_latitude) * math.cos(self.elements.inclination_rad)
        )
        z_ecl = radius_m * (math.sin(argument_of_latitude) * math.sin(self.elements.inclination_rad))

        # Rotate ecliptic -> equatorial by obliquity epsilon
        x_eci = x_ecl
        y_eci = y_ecl * math.cos(OBLIQUITY_EPSILON_RAD) - z_ecl * math.sin(OBLIQUITY_EPSILON_RAD)
        z_eci = y_ecl * math.sin(OBLIQUITY_EPSILON_RAD) + z_ecl * math.cos(OBLIQUITY_EPSILON_RAD)

        return x_eci, y_eci, z_eci

    def estimate_tidal_acceleration(self, dt: datetime) -> float:
        """Estimate maximum lunar tidal acceleration at Earth's surface in m/s^2.

        This computes the peak vertical tidal acceleration at the sublunar point:
            a_tide_max ≈ 2 G M_moon R_earth / r^3
        where r is the instantaneous geocentric distance Moon–Earth center.

        Parameters
        - dt: A timezone-aware or naive datetime. If naive, UTC is assumed.

        Returns
        - a_tide_max in m/s^2
        """
        x_m, y_m, z_m = self.get_position_eci(dt)
        r_m = math.sqrt(x_m * x_m + y_m * y_m + z_m * z_m)
        a_tide = 2.0 * G_SI * M_MOON_KG * R_EARTH_M / (r_m ** 3)
        return a_tide

    # ------------- Convenience Helpers -------------
    def estimate_tidal_acceleration_as_g(self, dt: datetime) -> float:
        """Return the tidal acceleration expressed as a fraction of standard gravity g0.

        Useful for quick intuition; the value is dimensionless (e.g., ~1e-6 g).
        """
        g0 = 9.80665
        return self.estimate_tidal_acceleration(dt) / g0

    # ------------- Internal utilities -------------
    @staticmethod
    def _as_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def _days_since_j2000(dt_utc: datetime) -> float:
        delta = dt_utc - J2000_UTC
        return delta.total_seconds() / 86400.0

    @staticmethod
    def _normalize_radians(angle_rad: float) -> float:
        # Normalize to [-pi, pi)
        wrapped = (angle_rad + math.pi) % (2.0 * math.pi) - math.pi
        return wrapped

    @staticmethod
    def _solve_kepler(mean_anomaly: float, eccentricity: float) -> float:
        """Solve Kepler's equation M = E - e*sin(E) for eccentric anomaly E.

        Uses a robust Newton-Raphson iteration with a good initial guess.
        """
        M = MoonOrbitModel._normalize_radians(mean_anomaly)
        e = eccentricity

        # Initial guess (good for small-to-moderate e)
        E = M if e < 0.8 else math.pi
        E += e * math.sin(M) / (1.0 - math.sin(M + e) + math.sin(M))

        # Iterate Newton-Raphson
        for _ in range(16):
            f = E - e * math.sin(E) - M
            f_prime = 1.0 - e * math.cos(E)
            delta = f / f_prime
            E -= delta
            if abs(delta) < 1e-12:
                break
        return E


# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    now_utc = datetime.now(timezone.utc)
    model = MoonOrbitModel()

    x, y, z = model.get_position_eci(now_utc)
    a_tide = model.estimate_tidal_acceleration(now_utc)
    a_tide_g = model.estimate_tidal_acceleration_as_g(now_utc)

    print("Pivisuma - Simplified Moon Ephemeris and Tidal Estimate")
    print(f"UTC datetime          : {now_utc.isoformat()}")
    print(f"Moon ECI position [m] : x={x: .0f}, y={y: .0f}, z={z: .0f}")
    r = math.sqrt(x*x + y*y + z*z)
    print(f"Geocentric distance [km]: {r/1000.0: .1f}")
    print(f"Tidal acceleration [m/s^2]: {a_tide:.6e}")
    print(f"Tidal acceleration [g]    : {a_tide_g:.6e}")