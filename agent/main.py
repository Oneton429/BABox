import sys

from maa.agent.agent_server import AgentServer
from maa.toolkit import Toolkit

import action_check_and_stop_student_info_task
import action_clear_student_info_cache
import action_export_to_html
import action_save_and_stop_student_info_task
import reco_get_student_info


def main():
    Toolkit.init_option("./")

    if len(sys.argv) < 2:
        print("Usage: python main.py <socket_id>")
        print("socket_id is provided by AgentIdentifier.")
        sys.exit(1)

    socket_id = sys.argv[-1]

    AgentServer.start_up(socket_id)
    AgentServer.join()
    AgentServer.shut_down()


if __name__ == "__main__":
    main()
