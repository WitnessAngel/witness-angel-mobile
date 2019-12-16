import os

if __name__ == "__main__":
    os.environ["WACLIENT_TYPE"] = "SERVICE"
    from waclient.background_service import main  # NOW ONLY we trigger conf loading
    main()
