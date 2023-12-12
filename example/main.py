from ycappuccino_core import init, start
import logging
import argparse

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    # Setup logs
    logging.basicConfig(level=logging.INFO)
    root_path = None
    parser = argparse.ArgumentParser(description='argument for app application')
    parser.add_argument('--root-path', type=str,  help='root path of the application')
    parser.add_argument('--port', default=5000, type=int, help='http port of the application')

    args = parser.parse_args()

    init(root_path=args.root_path, app=["ycappuccino_host","ycappuccino_service_comm_storage"], layers=["ycappuccino_host","ycappuccino_service_comm","ycappuccino_service_comm_storage","ycappuccino_swagger","ycappuccino_storage","ycappuccino_endpoints","ycappuccino_endpoints_storage","ycappuccino_endpoints_service"], bundle_prefix=["ycappuccino"], port=args.port)
    # Run the server
    start()

