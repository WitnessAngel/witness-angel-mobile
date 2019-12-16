import os

if __name__ == "__main__":
    os.environ["WACLIENT_TYPE"] = "APPLICATION"
    from waclient.app import main  # NOW ONLY we trigger conf loading
    main()
