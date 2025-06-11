# Franka Desk API Client

Simple python module to interact the Franka Robotics Desk API.

## How to use it

### Set your credentials

Be sure that your credentials are set as enviroment variables when running any script.
Do not push any of these credentials to a repository!
You can define a `.env` file in your home directory which looks like:
```bash
FRANKA_DESK_USERNAME=********
FRANKA_DESK_PASSWORD=********
```
and add the following lines to you `.bashrc` or `.zshrc`:
```bash
# Set env variables
if [ -f ~/.env ]; then
  export $(grep -v '^#' ~/.env | xargs)
fi
```
### Enable the franka

To enable your franka (take control, unlock joints and enable fci) simply run:
```bash
uv run scripts/enable_franka.py <robot_ip>
```

## Collaborating

You want to add some other scripts? Create a PR.

