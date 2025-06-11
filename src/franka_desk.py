import requests
from typing import Union, List


class FrankaDesk:
    """Client to the Franka Desk API.

    This class provides a Python interface to interact with the Franka Desk API,
    allowing control and monitoring of Franka robots through HTTP requests.

    Args:
        robot_ip (str): IP address of the Franka robot.
        user (str): Username for authentication.
        password (str): Password for authentication.
        name (str, optional): Name identifier for this client. Defaults to "franka_desk_client".

    Attributes:
        key (str | None): Control token for robot operations. None if control is not acquired.
    """

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

        self.key: Union[str, None] = None

    def has_control(self) -> bool:
        """Check if this client currently has control of the robot.

        Returns:
            bool: True if this client has control (has a valid control token),
                 False otherwise.
        """
        return self.key is not None

    def take_control(self):
        """Acquire the control key and become the owner of the robot.

        This method requests a control token from the robot. The token is required
        for most control operations. Only one client can have control at a time.

        Raises:
            requests.exceptions.HTTPError: If the request fails or authentication is invalid.
        """
        response = requests.post(
            f"{self._url}/api/system/control-token:take",
            json={"owner": self._name},
            auth=(self._user, self._password),
            timeout=5.0,
        )
        response.raise_for_status()

        self.key = response.json().get("token")

    def unlock_joints(self):
        """Unlock all robot joints.

        This method unlocks all joints of the robot, allowing them to be moved.
        The client must have control of the robot to perform this operation.

        Raises:
            RuntimeError: If the client does not have control of the robot.
            requests.exceptions.HTTPError: If the request fails (except for 500 status).
        """
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
        """Lock all robot joints.

        This method locks all joints of the robot, preventing them from being moved.
        The client must have control of the robot to perform this operation.

        Raises:
            RuntimeError: If the client does not have control of the robot.
            requests.exceptions.HTTPError: If the request fails.
        """
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
        """Change the operating mode of the robot.

        Args:
            mode (str, optional): The desired operating mode. Defaults to "Execution".
                Valid modes include "Execution" and other robot-specific modes.

        Raises:
            RuntimeError: If the client does not have control of the robot.
            requests.exceptions.HTTPError: If the request fails or the mode is invalid.
        """
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
        """Reboot the robot system.

        This method initiates a system reboot of the robot. No control token is required
        for this operation.

        Raises:
            requests.exceptions.HTTPError: If the request fails.
        """
        requests.post(
            f"{self._url}/api/system:reboot",
            auth=(self._user, self._password),
        )

    def deactivate_fci(self):
        """Deactivate the Fast Control Interface (FCI).

        This method deactivates the Fast Control Interface of the robot.
        The client must have control of the robot to perform this operation.

        Raises:
            RuntimeError: If the client does not have control of the robot.
            requests.exceptions.HTTPError: If the request fails.
        """
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
        """Activate the Fast Control Interface (FCI).

        This method activates the Fast Control Interface of the robot.
        The client must have control of the robot to perform this operation.

        Raises:
            RuntimeError: If the client does not have control of the robot.
            requests.exceptions.HTTPError: If the request fails (except for 500 status).
        """
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

    def get_joint_states(self) -> List[str]:
        """Get the current brake status of all robot joints.

        This method retrieves the current brake status for each joint of the robot.
        No control token is required for this operation.

        Returns:
            List[str]: A list of brake status strings for each joint.

        Raises:
            requests.exceptions.HTTPError: If the request fails.
        """
        response = requests.get(
            f"{self._url}/api/arm/joints",
            auth=(self._user, self._password),
        )
        response.raise_for_status()
        return [joint.get("brakeStatus") for joint in response.json()]

    def get_operating_mode(self) -> str:
        """Get the current operating mode of the robot.

        This method retrieves the current operating mode of the robot.
        No control token is required for this operation.

        Returns:
            str: The current operating mode of the robot.

        Raises:
            requests.exceptions.HTTPError: If the request fails.
        """
        response = requests.get(
            f"{self._url}/api/system/operating-mode",
            auth=(self._user, self._password),
        )
        response.raise_for_status()
        return response.json().get("status")
