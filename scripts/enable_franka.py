"""Script to fully enable Franka by taking control, opening the joints and activating FCI."""

import argparse
import os
import time

from franka_desk import FrankaDesk


def enable_robot(robot_ip: str):
    user = os.getenv("FRANKA_DESK_USERNAME")
    password = os.getenv("FRANKA_DESK_PASSWORD")

    if not user or not password:
        raise RuntimeError(
            "Missing user or password. They should be set as environment variables FRANKA_DESK_USERNAME and FRANKA_DESK_PASSWORD"
        )

    franka_desk = FrankaDesk(robot_ip=robot_ip, user=user, password=password)

    print("Requesting control of the robot.")

    try:
        franka_desk.take_control()
    except Exception as e:
        print(
            f"Failed to take control of the Franka :{e}. We will reboot and try again in 1 min."
        )
        franka_desk.reboot()

        # Wait until we reach execution state
        time.sleep(60.0)

        while franka_desk.get_operating_mode() != "Execution":
            # keep sleeping until we reach execution mode...
            time.sleep(2.0)

        franka_desk.take_control()

    print(f"We have the control of the robot. The control key is: {franka_desk.key}")

    print("Unlocking joints.")
    franka_desk.unlock_joints()

    print("Activating FCI.")
    franka_desk.activate_fci()

    print("Done!")
    # franka_desk.deactivate_fci()
    # franka_desk.lock_joints()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Example script with one string argument."
    )
    parser.add_argument(
        "robot_ip",
        type=str,
        help="IP address of the robot to be enabled, this argument is mandatory!.",
    )
    args = parser.parse_args()

    enable_robot(args.robot_ip)
