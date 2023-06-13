

class valid_cmd:
    """
    Class: valid_cmd
    Desc: Class to keep valid commands in to reference late
    """

    def __init__(self, cmd_str, params_req):
        self.cmd_str = cmd_str
        self.params_req = params_req


assign_cmd = valid_cmd("assign", 3)

release_cmd = valid_cmd("release", 2)

new_run_cmd = valid_cmd("newrun", 1)

victory_cmd = valid_cmd("victory", 1)

VALID_CMDS = [release_cmd, assign_cmd, new_run_cmd, victory_cmd]
