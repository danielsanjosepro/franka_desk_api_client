from time import time
import requests


class FrankaDesk:
    """Client to the Franka Desk API."""

    def __init__(
        self,
        robot_ip: str,
        user: str,
        password: str,
        name: str = "franka_desk_client",
    ):
        self._robot_ip = robot_ip
        self._url = f"https://{robot_ip}"
        self._user = user
        self._password = password
        self._name = name

        self.key: str | None = None

    def has_control(self) -> bool:
        return self.key is not None

    def take_control(self):
        """Acquire the control key and become the owner of the robot."""
        response = requests.post(
            f"{self._url}/api/system/control-token:take",
            json={"owner": self._name},
            auth=(self._user, self._password),
            timeout=5.0,
        )
        response.raise_for_status()

        self.key = response.json().get("token")

    def unlock_joints(self):
        if not self.has_control:
            raise RuntimeError(
                "We do not have control, you need to call the take_control function first."
            )

        response = requests.post(
            f"{self._url}/api/arm/joints:unlock",
            headers={"X-Control-Token": self.key},
            auth=(self._user, self._password),
        )

        if response.status_code not in [200, 500]:
            response.raise_for_status()

    def lock_joints(self):
        if not self.has_control:
            raise RuntimeError(
                "We do not have control, you need to call the take_control function first."
            )

        requests.post(
            f"{self._url}/api/arm/joints:lock",
            headers={"X-Control-Token": self.key},
            auth=(self._user, self._password),
        ).raise_for_status()

    def set_mode(self, mode: str = "Execution"):
        if not self.has_control:
            raise RuntimeError(
                "We do not have control, you need to call the take_control function first."
            )

        requests.post(
            f"{self._url}/api/system/operating-mode:change",
            json={"desiredOperatingMode": mode},
            headers={"X-Control-Token": self.key},
            auth=(self._user, self._password),
        ).raise_for_status()

    def reboot(self):
        requests.post(
            f"{self._url}/api/system:reboot",
            auth=(self._user, self._password),
        )

    def deactivate_fci(self):
        if not self.has_control:
            raise RuntimeError(
                "We do not have control, you need to call the take_control function first."
            )

        requests.post(
            f"{self._url}/api/fci:deactivate",
            headers={"X-Control-Token": self.key},
            auth=(self._user, self._password),
        ).raise_for_status()

    def activate_fci(self):
        if not self.has_control:
            raise RuntimeError(
                "We do not have control, you need to call the take_control function first."
            )

        response = requests.post(
            f"{self._url}/api/fci:activate",
            headers={"X-Control-Token": self.key},
            auth=(self._user, self._password),
        )

        if response.status_code not in [200, 500]:
            response.raise_for_status()

    def get_joint_states(self):
        response = requests.get(
            f"{self._url}/api/arm/joints",
            auth=(self._user, self._password),
        )
        response.raise_for_status()
        return [joint.get("brakeStatus") for joint in response.json()]

    def get_operating_mode(self):
        response = requests.get(
            f"{self._url}/api/system/operating-mode",
            auth=(self._user, self._password),
        )
        response.raise_for_status()
        return response.json().get("status")
