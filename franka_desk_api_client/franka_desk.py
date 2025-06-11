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
        self._key: str | None = None

    def has_control(self) -> bool:
        return self._key is not None

    def take_control(self):
        """Acquire the control key and become the owner of the robot."""
        response = requests.post(
            f"{self._url}/api/arm/control",
            json={"owner": self._name},
            auth=(self._user, self._password),
        )
        response.raise_for_status()

        self._key = response.json()["control_key"]

    def unlock_joints(self):
        if not self.has_control:
            raise RuntimeError(
                "We do not have control, you need to call the take_control function first."
            )

        requests.post(
            f"{self._url}/api/arm/unlock",
            json={"control-key": self._key},
            auth=(self._user, self._password),
        ).raise_for_status()

    def lock_joints(self):
        if not self.has_control:
            raise RuntimeError(
                "We do not have control, you need to call the take_control function first."
            )

        requests.post(
            f"{self._url}/api/arm/lock",
            json={"control-key": self._key},
            auth=(self._user, self._password),
        ).raise_for_status()

    def set_mode(self, mode: str = "execution"):
        if not self.has_control:
            raise RuntimeError(
                "We do not have control, you need to call the take_control function first."
            )

        requests.post(
            f"{self._url}/api/mode",
            json={"control-key": self._key},
            auth=(self._user, self._password),
        ).raise_for_status()

    def activate_fci(self):
        if not self.has_control:
            raise RuntimeError(
                "We do not have control, you need to call the take_control function first."
            )

        requests.post(
            f"{self._url}/api/fci/activate",
            json={"control-key": self._key},
            auth=(self._user, self._password),
        ).raise_for_status()
