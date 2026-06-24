import json
import math
import random
import os

import weatherrouting

# If this script is used to regenerate `polar_get_speed_reference.json`,
# update the JSON metadata accordingly: source version, commit, script path,
# and generation date.

POLAR_PATH = os.path.join(os.path.dirname(__file__),
                          "../tests/data/bavaria38.pol")
OUT_PATH = os.path.join(os.path.dirname(__file__),
                        "../tests/data/polar_get_speed_reference.json")

def main():
    polar = weatherrouting.Polar(POLAR_PATH)
    random.seed(1)

    num_tws_samples = 10
    num_twa_samples = 10

    tws_min = 0
    tws_max = polar.tws[-1] + 10
    twa_min = 0
    twa_max = math.pi

    tws_samples = [random.uniform(tws_min, tws_max) for _ in range(num_tws_samples)]
    twa_samples = [random.uniform(twa_min, twa_max) for _ in range(num_twa_samples)]

    rows = []
    for tws in tws_samples:
        for twa in twa_samples:
            rows.append(
                {
                    "tws": tws,
                    "twa": twa,
                    "speed": polar.get_speed(tws, twa),
                }
            )

    with open(OUT_PATH, "w") as f:
        json.dump(rows, f, indent=2, sort_keys=True)

if __name__ == "__main__":
    main()
